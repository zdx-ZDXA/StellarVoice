# 更新日志

## 1.0.3

- 补齐 `CHANGELOG.md`（AstrBot 启动告警消除）。

## 1.0.2

- `_conf_schema.json` 改为 AstrBot 扁平字典格式，修复插件加载失败。

## 1.0.1

- 去掉 `@register` 装饰器，改为 `class StellarVoice(Star)` 直接继承。
- 修复 AstrBot 4.x 导入路径。

## 1.0.0

- 对外接口 `speak(text, uid, umo)`，供星缀调用；失败返回 `None`。
- 后端：Azure Speech Services（默认 `zh-CN-XiaoxiuNeural`）、Google Cloud TTS。
- 每日配额限制，0 表示不限量。
