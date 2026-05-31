import logging
import sys

from loguru import logger

from infra.core.config import settings, DATA_DIR

LOG_DIR = DATA_DIR / "logs/app"
LOG_FORMAT = "{time:YYYY-MM-DDTHH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"

THIRD_PARTY_LOGGERS = (
    "uvicorn",
    "uvicorn.access",
    "sqlalchemy",
    "httpcore",
    "httpx",
    "aio_pika",
    "aiormq",
)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        if record.levelno >= logging.INFO:
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO") -> None:
    logger.remove()

    if settings.version == "prod":
        logger.add(
            sys.stdout,
            level=level.upper(),
            format=LOG_FORMAT,
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            level=level.upper(),
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level:<8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,
        )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.add(
        LOG_DIR / "app.log",
        level=level.upper(),
        format=LOG_FORMAT,
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        enqueue=True,
        filter=lambda record: record["level"].no < logging.ERROR,
    )

    logger.add(
        LOG_DIR / "error.log",
        level="ERROR",
        format=LOG_FORMAT,
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=settings.version != "prod",
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in THIRD_PARTY_LOGGERS:
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False
