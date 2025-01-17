from collections import deque

import logging


LOGGER_NAME = 'common_logger'
LOG_LOCATION = './log/common.log'
logger = logging.getLogger(LOGGER_NAME)

CMF_LOCATION = './cmf/lorem.txt'
LEN_QUEUE = 300564
MSG_LEN = 4095


class MessageChecker:
    def __init__(self):
        self._count = 0
        self._errcount = 0


    # Getter for (successful) count:
    @property 
    def count(self):
        return self._count        


    # Getter for total count:
    @property 
    def errcount(self):
        return self._errcount        


    def check_quickly(self, message):
        if len(message) == MSG_LEN:
            self._count += 1
        else:
            self._errcount += 1


    def check_thoroughly(self, message):
        lorem = 'Lorem'
        loremslice = message[:5]
        cur = 'Cur'
        curslice = message[len(message)-3:]
    
        if lorem.upper() == loremslice.upper() and cur.upper() == curslice.upper():
            self._count += 1
            return cmf_pb2.ChangeReply(message='success')
        else:
            self._errcount += 1


def configure_logger(name: str, filepath: str, logLevel: int):
    global logger

    logger = logging.getLogger(name)
    handler = logging.FileHandler(filepath)
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logLevel)


def _message_generator(queue: deque, lorem: str) -> deque:    
    global logger

    words = lorem.split()
    logger.info('Word count in \"words\": {}'.format(len(words)))
    
    for _ in range(506): # Just a hair over 300,000 msgs..
        for idx, word in enumerate(words):
            words[idx] = word.upper()
            msg = ' '.join(words)
            queue.append(msg)
        # Re-lowercasify:        
        words = lorem.split()

    logger.info('Loaded Cmfx Requests!')
    
    return queue


def load_messages() -> deque:
    global logger

    configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    msg_content = open(CMF_LOCATION, 'r').read().replace('\n', '')

    queue = deque()
    queue = _message_generator(queue, msg_content)

    return queue
