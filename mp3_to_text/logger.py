"""
日志管理模块
使用 loguru 库实现日志管理
"""

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger


def setup_logger(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    初始化日志配置

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_dir: 日志文件目录
    """
    # 移除默认的日志处理器
    logger.remove()

    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 日志文件名带时间戳
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"app_{timestamp}.log"

    # 控制台输出（彩色）
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )

    # 文件输出
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8"
    )

    # 记录启动信息
    logger.info("=" * 60)
    logger.info("MP3转文本工具 - 运行日志")
    logger.info("=" * 60)


def log_stage(stage_name: str) -> None:
    """记录阶段开始"""
    logger.info(f"📌 阶段: {stage_name}")


def log_file_found(file_path: str, total_count: int) -> None:
    """记录找到的文件"""
    logger.info(f"📁 发现 MP3 文件: {Path(file_path).name} ({total_count}个)")


def log_conversion_start(file_path: str, current: int, total: int) -> None:
    """记录转换开始"""
    logger.info(f"🎵 开始转换 [{current}/{total}]: {Path(file_path).name}")


def log_conversion_success(file_path: str, output_path: str, duration: float) -> None:
    """记录转换成功"""
    logger.info(f"✅ 转换成功: {Path(file_path).name} → {Path(output_path).name} (耗时: {duration:.1f}秒)")


def log_conversion_error(file_path: str, error: str) -> None:
    """记录转换错误"""
    logger.error(f"❌ 转换失败: {Path(file_path).name} - {error}")


def log_summary(total: int, success: int, failed: int, total_time: float) -> None:
    """记录运行总结"""
    logger.info("=" * 60)
    logger.info("运行总结")
    logger.info("=" * 60)
    logger.info(f"总文件数: {total}")
    logger.info(f"成功: {success}")
    logger.info(f"失败: {failed}")
    logger.info(f"总耗时: {total_time:.1f}秒")
    logger.info("=" * 60)


def get_log_file_path(log_dir: str = "logs") -> str:
    """获取当日日志文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d")
    return str(Path(log_dir) / f"app_{timestamp}.log")
