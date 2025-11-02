import logging
import os
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import Literal
from colorama import Fore, Back, Style, init as colorama_init

# 初始化 colorama，控制台自动重置颜色
colorama_init(autoreset=True)


class LogConfig:
    def __init__(
        self,
        model: Literal["debug", "release"] = "debug",
        console: bool = True,
        file: bool = True,
        file_path: str = "logs/app.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5000,
        when: str = "midnight",  # 时间切割
        interval: int = 1,
        encoding: str = "utf-8",
        fmt: str = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        rotate_type: Literal["time", "size"] = "time",
        level: str = None,
    ):
        """
        通用日志配置
        :param model: 模式(debug/release)
        :param console: 是否输出控制台
        :param file: 是否输出文件
        :param file_path: 日志文件路径
        :param max_bytes: 大小切割阈值
        :param backup_count: 保留文件个数
        :param when: 时间切割周期
        :param interval: 时间切割间隔
        :param encoding: 文件编码
        :param fmt: 日志格式，已包含函数名、文件名、行号
        :param datefmt: 时间格式
        :param rotate_type: 切割方式 ('time' 或 'size')
        :param level: 自定义日志级别（覆盖默认）
        """
        self.model = model
        self.console = console
        self.file = file
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.when = when
        self.interval = interval
        self.encoding = encoding
        self.fmt = fmt
        self.datefmt = datefmt
        self.rotate_type = rotate_type
        self.level = level


class ColorFormatter(logging.Formatter):
    """
    彩色控制台输出：
    - LEVEL 前景+背景色不同
    - 消息前景色根据级别不同
    - 保证文件输出无颜色
    """
    LEVEL_COLOR = {
        logging.DEBUG: (Fore.BLACK, Back.BLUE),
        logging.INFO: (Fore.BLACK, Back.GREEN),
        logging.WARNING: (Fore.BLACK, Back.YELLOW),
        logging.ERROR: (Fore.BLACK, Back.RED),
        logging.CRITICAL: (Fore.BLACK + Style.BRIGHT, Back.LIGHTRED_EX),
    }

    MSG_COLOR = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.LIGHTRED_EX + Style.BRIGHT,
    }

    def format(self, record):
        """
        只在控制台显示颜色，不修改文件输出
        """
        # 复制 record 避免影响文件输出
        record_copy = logging.LogRecord(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=record.msg,
            args=record.args,
            exc_info=record.exc_info,
            func=record.funcName,
            sinfo=record.stack_info
        )
        # LEVEL 前景+背景色
        fg, bg = self.LEVEL_COLOR.get(record.levelno, (Fore.WHITE, Back.BLACK))
        record_copy.levelname = f"{fg}{bg}{record.levelname}{Style.RESET_ALL}"
        # 消息前景色
        msg_fg = self.MSG_COLOR.get(record.levelno, Fore.WHITE)
        record_copy.msg = f"{msg_fg}{record_copy.msg}{Style.RESET_ALL}"
        return super().format(record_copy)


class LoggerFactory:
    """
    LoggerFactory 用于创建和缓存 logger 实例
    """
    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "root", config: LogConfig = None) -> logging.Logger:
        """
        获取带配置的 logger 实例（单例缓存）
        :param name: logger 名称
        :param config: LogConfig 配置实例
        :return: logging.Logger 对象
        """
        if not config:
            config = LogConfig()

        key = f"{name}-{id(config)}"
        if key in cls._loggers:
            return cls._loggers[key]

        # 根据 model 自动设置默认日志级别
        if config.level:
            level = getattr(logging, config.level.upper(), logging.INFO)
        else:
            level = logging.DEBUG if config.model == "debug" else logging.INFO

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()  # 防止重复添加 handler

        # 控制台输出（彩色）
        if config.console:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(ColorFormatter(fmt=config.fmt, datefmt=config.datefmt))
            logger.addHandler(ch)

        # 文件输出（普通，不带颜色）
        if config.file:
            os.makedirs(os.path.dirname(config.file_path), exist_ok=True)
            if config.rotate_type == "size":
                fh = RotatingFileHandler(
                    config.file_path,
                    maxBytes=config.max_bytes,
                    backupCount=config.backup_count,
                    encoding=config.encoding,
                )
            else:
                fh = TimedRotatingFileHandler(
                    config.file_path,
                    when=config.when,
                    interval=config.interval,
                    backupCount=config.backup_count,
                    encoding=config.encoding,
                )
            fh.setLevel(level)
            fh.setFormatter(logging.Formatter(fmt=config.fmt, datefmt=config.datefmt))
            logger.addHandler(fh)

        logger.propagate = False  # 防止重复打印
        cls._loggers[key] = logger
        return logger


# ===========================
# 全局简化接口
# ===========================

_logger: logging.Logger = None  # 全局 logger

def init(config: LogConfig = None):
    """
    初始化全局 logger
    :param config: LogConfig 配置对象
    """
    global _logger
    _logger = LoggerFactory.get_logger("root", config)


def debug(msg: str, *args, **kwargs):
    if _logger:
        _logger.debug(msg, *args, stacklevel=2, **kwargs)


def info(msg: str, *args, **kwargs):
    if _logger:
        _logger.info(msg, *args, stacklevel=2, **kwargs)


def warning(msg: str, *args, **kwargs):
    if _logger:
        _logger.warning(msg, *args, stacklevel=2, **kwargs)


def error(msg: str, *args, **kwargs):
    if _logger:
        _logger.error(msg, *args,  stacklevel=2,**kwargs)


def critical(msg: str, *args, **kwargs):
    if _logger:
        _logger.critical(msg, *args, stacklevel=2, **kwargs)
