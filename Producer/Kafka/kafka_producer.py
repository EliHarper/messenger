from bson.json_util import dumps
from collections import deque
from decouple import config
from kafka import KafkaProducer

import logging
import sys
import time
import traceback



TEST_LENGTH = 10

LOGGER_NAME =  'kafka_producer_logger'
LOG_LOCATION = './log/kafka_producer.log'
logger = logging.getLogger(LOGGER_NAME)

producer = KafkaProducer(bootstrap_servers=[config('KAFKA_URL')],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'),
                         compression_type='gzip'
)


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)
        formatter = logging.Formatter('%(levelname)s: %(message)s')

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def message_generator(queue: deque, lorem: str):    
        words = lorem.split()
        logger.info('Word count in \"words\": {}'.format(len(words)))
        
        for _ in range(170): # Just a hair over 100,000 msgs..
            for idx, word in enumerate(words):
                words[idx] = word.upper()
                msg = ' '.join(words)
                queue.append(msg)
            # Re-lowercasify:        
            words = lorem.split()

        
        import pdb; pdb.set_trace()
        logger.info('Loaded Cmfx Requests!')
        return queue


def run():
    global logger

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    msg_content = open('cmf/lorem.txt', 'r').read().replace('\n', '')

    queue = deque()
    queue = message_generator(queue, msg_content)

    logger.info('Starting send with queue of length: {}'.format(len(queue)))
    start_time = time.time()

    try:
        exc_info = sys.exc_info()
        count = 0
        for msg in queue:
            producer.send('msgs', msg)
            count += 1

    except Exception as e:
        logger.debug('Unexpected exception while sending: {}'.format(e))
        logger.debug('\n***Full trace:\n{}'.format(traceback.print_exc()))

    finally:
        traceback.print_exception(*exc_info)
        del exc_info
        producer.close()
        
    logger.debug('Done! Time elapsed: {}'.format(time.time() - start_time))
    logger.info('Sent {} messages.\n'.format(count))




if __name__ == '__main__':
    run()