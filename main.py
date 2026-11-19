# -*- coding: utf-8 -*-
"""StellarVoice —— 星言，语音执行器 v1.0.0

星缀的语音挂载点，接口兼容 Amo_Speechsound 的 speak()。
支持 Azure、Google、elevenlabs 等 TTS 后端。
"""
from __future__ import annotations
from typing import Any, Dict, Optional
try:
    from astrbot.api import logger
    from astrbot.api.star import Context, Star
except ImportError:
    raise

PLUGIN_VERSION = "1.0.1"


class StellarVoice(Star):
    def __init__(self, context: Context, config: Dict[str, Any] | None = None) -> None:
        super().__init__(context)
        cfg = config or {}
        self._enabled: bool = bool(cfg.get("enable", True))
        self._backend: str = str(cfg.get("backend", "azure"))   # azure / google / elevenlabs
        self._api_key: str = str(cfg.get("api_key") or "")
        self._region: str = str(cfg.get("region") or "")
        self._voice_name: str = str(cfg.get("voice_name") or "")
        self._daily_limit: int = int(cfg.get("daily_limit") or 0)
        self._daily_used: Dict[str, int] = {}
        logger.info(f"[StellarVoice] v{PLUGIN_VERSION} 初始化，后端={self._backend}")

    async def speak(
        self,
        text: str,
        uid: str = "",
        umo: str = "",
        **kwargs,
    ) -> bytes | None:
        """公开接口：供星缀大脑调用的语音生成接口。

        返回音频 PCM/WAV 字节，失败返回 None。
        """
        if not self._enabled:
            return None
        if not text or len(str(text).strip()) < 2:
            return None

        # 配额检查
        if self._daily_limit > 0:
            used = self._daily_used.get(str(uid or umo), 0)
            if used >= self._daily_limit:
                logger.info(f"[StellarVoice] {uid} 今日配额已用完（{used}/{self._daily_limit}）")
                return None

        try:
            audio = await self._do_speak(str(text)[:1000])
            if audio:
                self._daily_used[str(uid or umo)] = (
                    self._daily_used.get(str(uid or umo), 0) + 1
                )
            return audio
        except Exception as e:
            logger.warning(f"[StellarVoice] 生成语音失败: {e}")
            return None

    async def _do_speak(self, text: str) -> bytes | None:
        """实际 TTS（根据 backend 路由）。"""
        if self._backend == "azure":
            return await self._azure_speak(text)
        elif self._backend == "google":
            return await self._google_speak(text)
        else:
            logger.warning(f"[StellarVoice] 不支持的后端：{self._backend}")
            return None

    async def _azure_speak(self, text: str) -> bytes | None:
        """Azure Speech Services TTS。"""
        try:
            import aiohttp
            ssml = f'''
<speak version='1.0' xml:lang='zh-CN'>
  <voice name='{self._voice_name or "zh-CN-XiaoxiuNeural"}'>
    <prosody rate='0.9' pitch='0'>{text}</prosody>
  </voice>
</speak>
            '''.strip()
            headers = {
                "Ocp-Apim-Subscription-Key": self._api_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            }
            url = f"https://{self._region or 'eastasia'}.tts.speech.microsoft.com/cognitiveservices/v1"
            async with aiohttp.ClientSession() as s:
                async with s.post(url, data=ssml, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status == 200:
                        return await r.read()
        except Exception as e:
            logger.warning(f"[StellarVoice] Azure TTS 失败: {e}")
        return None

    async def _google_speak(self, text: str) -> bytes | None:
        """Google Cloud Text-to-Speech。"""
        try:
            import aiohttp
            import json
            payload = {
                "input": {"text": text[:500]},
                "voice": {
                    "languageCode": "zh-CN",
                    "name": self._voice_name or "zh-CN-Standard-B",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            }
            headers = {"X-Goog-Api-Key": self._api_key, "Content-Type": "application/json"}
            url = "https://texttospeech.googleapis.com/v1/text:synthesize"
            async with aiohttp.ClientSession() as s:
                async with s.post(url, json=payload, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status == 200:
                        data = await r.json()
                        b64_audio = data.get("audioContent", "")
                        if b64_audio:
                            import base64
                            return base64.b64decode(b64_audio)
        except Exception as e:
            logger.warning(f"[StellarVoice] Google TTS 失败: {e}")
        return None
