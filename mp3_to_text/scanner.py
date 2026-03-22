"""
目录扫描模块
递归遍历目录，查找所有支持的音视频文件（MP3、MP4、MKV 等）
"""

import os
from pathlib import Path
from typing import List

import config
from logger import logger


def scan_directory(root_path: str) -> List[Path]:
    """
    递归扫描目录，查找所有支持的音频文件

    Args:
        root_path: 根目录路径

    Returns:
        音频文件路径列表
    """
    root = Path(root_path)

    if not root.exists():
        logger.error(f"目录不存在: {root_path}")
        return []

    if not root.is_dir():
        logger.error(f"路径不是目录: {root_path}")
        return []

    logger.info(f"开始扫描目录: {root.absolute()}")

    audio_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            # 检查文件扩展名（不区分大小写）
            if file_path.suffix.lower() in config.SUPPORTED_FORMATS:
                audio_files.append(file_path)

    logger.info(f"扫描完成，共发现 {len(audio_files)} 个音频文件")

    if audio_files:
        logger.info("文件列表:")
        for i, f in enumerate(audio_files, 1):
            logger.info(f"  {i}. {f.relative_to(root)}")

    return audio_files


def validate_file(file_path: Path) -> bool:
    """
    验证文件是否有效

    Args:
        file_path: 文件路径

    Returns:
        是否有效
    """
    if not file_path.exists():
        logger.warning(f"文件不存在: {file_path}")
        return False

    if not file_path.is_file():
        logger.warning(f"不是有效文件: {file_path}")
        return False

    if file_path.suffix.lower() not in config.SUPPORTED_FORMATS:
        logger.warning(f"不支持的文件格式: {file_path.suffix}")
        return False

    # 检查文件大小
    file_size = file_path.stat().st_size
    if file_size == 0:
        logger.warning(f"文件为空: {file_path}")
        return False

    return True


def get_output_filename(mp3_path: Path, output_format: str = None) -> str:
    """
    根据MP3文件生成输出文件名

    Args:
        mp3_path: MP3文件路径
        output_format: 输出格式 (txt 或 md)

    Returns:
        输出文件名
    """
    if output_format is None:
        output_format = config.OUTPUT_FORMAT

    base_name = mp3_path.stem

    if output_format == "md":
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.md"
    else:
        return f"{base_name}.txt"
