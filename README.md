# 🔊 星言 StellarVoice

星缀套件的语音执行器，支持 Azure / Google TTS。

## 功能

- 对外提供 `speak()` 接口，供星缀调用
- 配额管理
- 失败不抛异常

## 配置

| 项 | 默认 | 说明 |
|---|---|---|
| backend | azure | azure / google |
| api_key | | API 密钥 |
| region | eastasia | Azure 区域 |
| voice_name | zh-CN-XiaoxiuNeural | 音色 |
| daily_limit | 0 | 每日上限 |

---
v1.0.2 · 星缀套件 | https://github.com/zdx-ZDXA/StellarVoice
