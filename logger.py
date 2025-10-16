import sys
import loguru


logger = loguru.logger
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>"
)
