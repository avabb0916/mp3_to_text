"""
配置文件
"""

from pathlib import Path

# ==================== 语音模型配置 ====================
# 可选模型: tiny, small, base, medium, large
# tiny   (~75MB)  - 最快，精度较低
# small  (~244MB) - 推荐，速度快，精度较好
# base   (~500MB) - 精度好，速度中等
# medium (~1.5GB) - 精度很好，速度较慢
# large  (~3GB)   - 精度最高，速度最慢
MODEL_SIZE = "small"

# 支持的语言设置
# None = 自动检测，"zh" = 中文，"en" = 英文
LANGUAGE = "zh"

# ==================== 文件输出配置 ====================
# 输出格式: "txt" 或 "md"
OUTPUT_FORMAT = "md"

# 输出目录 (相对于脚本运行目录)
OUTPUT_DIR = "output"

# ==================== 日志配置 ====================
# 日志目录
LOG_DIR = "logs"

# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# ==================== 音频处理配置 ====================
# 音频采样率
SAMPLE_RATE = 16000

# 临时文件目录
TEMP_DIR = "temp"

# ==================== 支持的格式 ====================
# 音频格式
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac"]
# 视频格式（ffmpeg 会自动提取音轨）
SUPPORTED_VIDEO_FORMATS = [".mp4", ".mkv"]
SUPPORTED_FORMATS = SUPPORTED_AUDIO_FORMATS + SUPPORTED_VIDEO_FORMATS


def get_model_path() -> Path:
    """获取模型缓存目录"""
    home = Path.home()
    model_path = home / ".cache" / "huggingface" / "hub"
    return model_path


def get_output_dir() -> Path:
    """获取输出目录"""
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_temp_dir() -> Path:
    """获取临时文件目录"""
    temp_path = Path(TEMP_DIR)
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path
