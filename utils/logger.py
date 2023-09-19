import logging

# This goes first
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s - %(message)s",
    filename="log.txt",
    filemode="w",
)
# Set up logging
INFO_LEVEL = 25
DEBUG_LEVEL = 15
logging.addLevelName(INFO_LEVEL, "INFO")
logging.addLevelName(DEBUG_LEVEL, "DEBUG")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Adjust the log level as needed
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")
console_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


def log_info(message):
    logger.log(INFO_LEVEL, message)


def log_debug(message):
    logger.log(DEBUG_LEVEL, message)
