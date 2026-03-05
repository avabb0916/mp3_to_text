"""
音频转换模块
使用 faster-whisper 进行语音识别
"""

import subprocess
import time
from pathlib import Path
from typing import Tuple

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("请先安装 faster-whisper: pip install faster-whisper")

import config
from logger import logger


class AudioConverter:
    """音频转换器"""

    def __init__(self, model_size: str = None, language: str = None):
        """
        初始化转换器

        Args:
            model_size: 模型大小 (tiny, small, base, medium, large)
            language: 语言代码 (zh, en, None=自动检测)
        """
        self.model_size = model_size or config.MODEL_SIZE
        self.language = language or config.LANGUAGE

        logger.info(f"初始化语音识别模型: {self.model_size}")
        logger.info(f"语言设置: {self.language or '自动检测'}")

        # 加载模型 - 使用更保守的设置
        self.model = WhisperModel(
            self.model_size,
            device="cpu",  # 显式使用 CPU，更稳定
            compute_type="int8"
        )

        logger.info("模型加载完成")

    def convert_to_wav(self, audio_path: Path) -> Path:
        """
        将音频转换为WAV格式（16kHz单声道）

        Args:
            audio_path: 原始音频文件路径

        Returns:
            WAV文件路径，失败返回None
        """
        temp_dir = config.get_temp_dir()
        wav_path = temp_dir / f"{audio_path.stem}_converted.wav"

        # 如果WAV已存在，直接使用
        if wav_path.exists():
            logger.info(f"使用已转换的WAV文件: {wav_path}")
            return wav_path

        try:
            # 使用 ffmpeg 转换
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-ar", "16000",        # 采样率 16kHz
                "-ac", "1",             # 单声道
                "-c:a", "pcm_s16le",    # WAV编码
                "-y",                   # 覆盖已存在的文件
                str(wav_path)
            ]

            logger.info(f"开始转换音频格式: {audio_path.name}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                logger.error(f"ffmpeg转换失败: {result.stderr}")
                return None

            logger.info(f"音频转换完成: {wav_path}")
            return wav_path

        except subprocess.TimeoutExpired:
            logger.error("音频转换超时")
            return None
        except FileNotFoundError:
            logger.error("未找到 ffmpeg，请先安装: brew install ffmpeg")
            return None
        except Exception as e:
            logger.error(f"音频转换异常: {e}")
            return None

    def recognize(self, audio_path: Path, show_progress: bool = True) -> Tuple[bool, str, float]:
        """
        识别音频文件

        Args:
            audio_path: 音频文件路径
            show_progress: 是否显示进度

        Returns:
            (是否成功, 识别文本, 耗时)
        """
        start_time = time.time()

        try:
            # 如果不是 WAV 格式，先转换
            if audio_path.suffix.lower() != ".wav":
                logger.info(f"正在转换音频格式: {audio_path.name}")
                wav_path = self.convert_to_wav(audio_path)
                if wav_path is None:
                    return False, "音频格式转换失败", 0
                audio_to_process = wav_path
            else:
                audio_to_process = audio_path

            # 执行语音识别 - 使用最简单的方式
            logger.info(f"开始语音识别: {audio_path.name}")
            logger.info(f"音频文件大小: {audio_to_process.stat().st_size / 1024 / 1024:.1f} MB")

            # 使用最简单的参数，不使用 VAD 和 chunking
            segments, info = self.model.transcribe(
                audio_to_process,
                language=self.language,
                beam_size=5,
                vad_filter=False,  # 禁用 VAD
                condition_on_previous_text=False
            )

            # 获取语言信息
            detected_language = info.language if info.language else "未知"
            logger.info(f"检测到语言: {detected_language}")

            # 收集识别结果
            text_segments = []
            segment_count = 0

            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_segments.append(text)
                    segment_count += 1
                    logger.debug(f"片段 {segment_count}: {text[:50]}...")

            full_text = "".join(text_segments)

            duration = time.time() - start_time
            logger.info(f"语音识别完成，耗时: {duration:.1f}秒")
            logger.info(f"识别到 {segment_count} 个片段，文本长度: {len(full_text)} 字符")

            return True, full_text, duration

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"识别异常: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, str(e), duration

    def format_markdown(self, mp3_path: Path, text: str, duration: float) -> str:
        """
        格式化为Markdown

        Args:
            mp3_path: 原始MP3文件路径
            text: 识别文本
            duration: 处理耗时

        Returns:
            Markdown格式文本
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = f"""# {mp3_path.name}

**转换时间**: {timestamp}
**原文件大小**: {mp3_path.stat().st_size / 1024 / 1024:.2f} MB
**处理耗时**: {duration:.1f} 秒
**使用模型**: {self.model_size}

---

{text}
"""

        return md_content

    def format_plain_text(self, text: str) -> str:
        """格式化为纯文本"""
        return text.strip()
