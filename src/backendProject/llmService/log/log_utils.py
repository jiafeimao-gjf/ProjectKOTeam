# 日志工具，用于获取通用日志输出工具
import logging


def get_logger(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(name)


logger = get_logger(__name__)
