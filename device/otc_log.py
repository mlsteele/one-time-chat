import logging

FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
FILENAME = 'device.log'
LEVEL = logging.INFO

def start(name):
    logger = logging.getLogger(name)

    logger.setLevel(LEVEL)

    formatter = logging.Formatter(FORMAT)
    
    handler = logging.FileHandler(FILENAME)
    handler.setLevel(LEVEL)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger

def stop(name):
    logging.getLogger(name).shutdown()
