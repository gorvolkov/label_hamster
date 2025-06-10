import logging


class LoggerFormatter(logging.Formatter):
    """Форматтер для логгера. Красит сообщения в разные цвета"""

    # colors for colored output
    RESET = '\033[0m'
    COLORS = {
        'DEBUG': '\033[33m',  # жёлтый
        'INFO': '\033[32m',  # зелёный
        'WARNING': '\033[31m',  # красный
        'ERROR': '\033[31m',  # красный
    }
    # message format
    MSG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self):
        super().__init__(fmt=self.MSG_FMT)

    def format(self, message):
        color = self.COLORS.get(message.levelname, self.RESET)
        colored_msg = super().format(message)
        return f"{color}{colored_msg}{self.RESET}"


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger_handler = logging.StreamHandler()
logger_handler.setLevel(logging.DEBUG)

logger_formatter = LoggerFormatter()
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)