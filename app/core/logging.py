import logging
import sys
from .config import settings
import traceback

logger = logging.getLogger("ecommerce_logger")

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_level = logging.DEBUG if settings.DEBUG else logging.INFO
console_handler.setLevel(console_level)
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
console_handler.setFormatter(console_formatter)

logger.addHandler(console_handler)

def log_request_info(request, level=logging.INFO):
    """
    Logs request method, URL, headers.
    Can be called in middlewares or exception handlers.
    """
    logger.log(
        level,
        f"Request: method={request.method}, url={request.url}, headers={dict(request.headers)}"
    )

def log_exception(exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Exception occurred:\n{tb}")

def log_info(message: str):
    logger.info(message)

def log_warning(message: str):
    logger.warning(message)