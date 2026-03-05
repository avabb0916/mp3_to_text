# MP3批量转文本工具

一个使用 Python 开发的本地语音识别工具，可以将 MP3 音频文件批量转换为文本。

## 功能特点

- 📁 递归扫描目录，支持子目录
- 🎵 支持多种音频格式：MP3、WAV、M4A、FLAC、OGG、WMA、AAC
- 📝 支持输出格式：TXT、Markdown
- 📊 带进度条显示
- 📝 完整的日志管理

## 环境要求

- macOS (Apple Silicon M1/M2/M3 推荐)
- Python 3.9+
- ffmpeg

## 安装

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/MP3ToTxt.git
cd MP3ToTxt/mp3_to_text

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 ffmpeg (如果没有)
brew install ffmpeg
```

## 使用方法

```bash
# 基本用法
python3 main.py /path/to/your/mp3_folder

# 指定输出目录
python3 main.py /path/to/folder -o ./output

# 指定输出格式 (txt 或 md)
python3 main.py /path/to/folder --format md

# 指定模型大小
# tiny   (~75MB)  - 最快，精度较低
# small  (~244MB) - 推荐，速度快，精度较好
# base   (~500MB) - 精度好，速度中等
# medium (~1.5GB) - 精度很好，速度较慢
python3 main.py /path/to/folder --model small

# 指定语言
python3 main.py /path/to/folder --language zh    # 中文
python3 main.py /path/to/folder --language en     # 英文

# 查看所有参数
python3 main.py --help
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | 输入目录路径 | (必填) |
| `-o, --output` | 输出目录 | `./output` |
| `--format` | 输出格式 (txt/md) | `md` |
| `--model` | 模型大小 | `small` |
| `--language` | 语言代码 | `zh` |
| `--log-level` | 日志级别 | `INFO` |

## 输出示例

### Markdown 格式
```markdown
# audio_001.mp3

**转换时间**: 2024-03-01 14:30:22
**原文件大小**: 15.5 MB
**处理耗时**: 120.5 秒
**使用模型**: small

---

[识别到的文本内容...]
```

## 项目结构

```
mp3_to_text/
├── main.py          # 主程序入口
├── config.py        # 配置文件
├── scanner.py       # 目录扫描模块
├── converter.py     # 音频转换模块
├── logger.py        # 日志管理模块
└── requirements.txt # 依赖
```

## 注意事项

### 内存问题

- **8GB 内存**：推荐使用 `tiny` 或 `small` 模型
- **16GB+ 内存**：可以使用 `medium` 或 `large` 模型获得更高精度

首次运行会自动下载模型（约 244MB for small）。

### 已知问题

1. 处理大型音频文件（>2小时）可能需要较长时间
2. M1/M2/M3 芯片建议使用 `int8` compute type

## 技术栈

- **语音识别**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **进度条**: tqdm
- **日志**: loguru

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-03-05)
- 初始版本
- 支持批量转换
- 支持多种输出格式
- 完整的日志管理
