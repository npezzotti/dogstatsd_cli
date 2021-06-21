import logging

def setup_logger(level=logging.INFO):
    logging.basicConfig(level=level, format='%(message)s')
    logger = logging.getLogger('dogstatsd_cli')
    return logger