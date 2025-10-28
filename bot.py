# -*- coding: utf-8 -*-
"""
QQ Bot SDK 主入口
"""
import argparse
import sys
import os

# 将 qqbot_sdk 添加到 python 路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'qqbot_sdk'))

from utils.logger import initialize_logging, print_banner
from utils.config import settings
from core.runner import main as run_bot


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QQ Bot SDK")
    parser.add_argument(
        "-local",
        "--local",
        action="store_true",
        help="启动本地命令测试工具",
    )
    return parser.parse_args()


def main() -> None:
    print_banner()
    # 使用 config/config.yaml
    initialize_logging(log_level="DEBUG" if settings.DEBUG_ENABLED else "INFO")
    args = _parse_args()
    run_bot(local_mode=args.local)


if __name__ == "__main__":
    main()
