import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
FILENAME = 'device.log'
LEVEL = logging.INFO

def start():
    print("start called")
    logging.basicConfig(filename=FILENAME)
    logging.basicConfig(level=LEVEL)
    logging.basicConfig(format=FORMAT)

def start2():
    logger = logging.getLogger()
    logger.setLevel(LEVEL)

    formatter = logging.Formatter(FORMAT)

    handler = logging.FileHandler(FILENAME)
    handler.setLevel(LEVEL)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    # logger.setFormat('%(asctime)-15s %(levelname)s: %(message)')
    return logger

def stop():
    logging.shutdown()
