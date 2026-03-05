#!/usr/bin/env python3
"""
MP3转文本工具 - 主程序
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import config
from logger import logger, log_stage, log_file_found, log_conversion_start, log_conversion_success, log_conversion_error, log_summary, get_log_file_path, setup_logger
from scanner import scan_directory
from converter import AudioConverter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MP3批量转文本工具 - 使用 faster-whisper 进行离线语音识别",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py /path/to/mp3_folder
  python main.py /path/to/folder -o ./output
  python main.py /path/to/folder --model medium --language zh
  python main.py /path/to/folder --format md --log-level DEBUG
        """
    )

    parser.add_argument(
        "input_dir",
        type=str,
        help="要扫描的目录路径"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=config.OUTPUT_DIR,
        help=f"输出目录 (默认: {config.OUTPUT_DIR})"
    )

    parser.add_argument(
        "--format", "--output-format",
        type=str,
        choices=["txt", "md"],
        default=config.OUTPUT_FORMAT,
        help=f"输出格式 (默认: {config.OUTPUT_FORMAT})"
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["tiny", "small", "base", "medium", "large"],
        default=config.MODEL_SIZE,
        help=f"语音识别模型大小 (默认: {config.MODEL_SIZE})"
    )

    parser.add_argument(
        "--language",
        type=str,
        default=config.LANGUAGE,
        help=f"语言代码，如 'zh' 中文, 'en' 英文 (默认: {config.LANGUAGE or '自动检测'})"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=config.LOG_LEVEL,
        help=f"日志级别 (默认: {config.LOG_LEVEL})"
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_args()

    # 更新配置
    config.LOG_LEVEL = args.log_level
    config.OUTPUT_FORMAT = args.format
    config.MODEL_SIZE = args.model
    config.LANGUAGE = args.language
    config.OUTPUT_DIR = args.output

    # 初始化日志
    setup_logger(config.LOG_LEVEL, config.LOG_DIR)

    # 记录启动信息
    logger.info("=" * 60)
    logger.info("MP3转文本工具 - 启动")
    logger.info("=" * 60)
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python版本: {sys.version.split()[0]}")
    logger.info(f"输入目录: {args.input_dir}")
    logger.info(f"输出目录: {args.output}")
    logger.info(f"输出格式: {args.format}")
    logger.info(f"模型大小: {args.model}")
    logger.info(f"语言设置: {args.language or '自动检测'}")
    logger.info("=" * 60)

    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("未安装 ffmpeg，请先运行: brew install ffmpeg")
        sys.exit(1)

    total_start_time = time.time()

    # 阶段1: 扫描目录
    log_stage("扫描目录")
    audio_files = scan_directory(args.input_dir)

    if not audio_files:
        logger.warning("未找到任何音频文件")
        sys.exit(0)

    # 阶段2: 初始化转换器
    log_stage("初始化语音识别模型")
    try:
        converter = AudioConverter(
            model_size=args.model,
            language=args.language
        )
    except Exception as e:
        logger.error(f"模型初始化失败: {e}")
        logger.error("请检查网络连接，确保模型可以正常下载")
        sys.exit(1)

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 阶段3: 批量转换
    log_stage("开始批量转换")

    success_count = 0
    failed_count = 0

    # 使用 tqdm 显示进度条
    with tqdm(total=len(audio_files), desc="转换进度", unit="个") as pbar:
        for i, audio_file in enumerate(audio_files, 1):
            log_conversion_start(str(audio_file), i, len(audio_files))

            # 执行识别
            success, text, duration = converter.recognize(audio_file)

            if success and text:
                # 生成输出文件
                if args.format == "md":
                    content = converter.format_markdown(audio_file, text, duration)
                else:
                    content = converter.format_plain_text(text)

                # 生成输出文件名
                base_name = audio_file.stem
                if args.format == "md":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{base_name}_{timestamp}.md"
                else:
                    output_filename = f"{base_name}.txt"

                output_path = output_dir / output_filename

                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    log_conversion_success(str(audio_file), str(output_path), duration)
                    success_count += 1
                except Exception as e:
                    log_conversion_error(str(audio_file), f"文件保存失败: {e}")
                    failed_count += 1
            else:
                log_conversion_error(str(audio_file), text if text else "识别失败")
                failed_count += 1

            # 更新进度条
            pbar.update(1)
            pbar.set_postfix({"成功": success_count, "失败": failed_count})

    # 阶段4: 完成
    total_time = time.time() - total_start_time

    logger.info("")
    log_summary(len(audio_files), success_count, failed_count, total_time)

    logger.info(f"📂 输出目录: {output_dir.absolute()}")
    logger.info(f"📝 日志文件: {get_log_file_path()}")

    return success_count, failed_count


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
