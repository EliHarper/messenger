from bson.json_util import dumps
from collections import deque
from common import load_messages
from decouple import config
from kafka import KafkaProducer
from tqdm import tqdm

import logging
import tqdm
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

    logger.info('Loaded Cmfx Requests!')
    return queue


def print_progress_bar(count, total, pct, prefix="Progress:", suffix="Complete", printEnd="\r\n"):    
    percent = ("{0:.0f}").format(100 * (count / float(total)))
    filledLength = int(100 * count // total)
    blocky = u"\u2588"
    bar = blocky * filledLength + '-' * (100 - filledLength)    
    sys.stdout.buffer.write(f'\r{prefix} |{bar}| {percent}% {suffix} {printEnd}')
    # Print newline on complete:
    if count == total:
        print()


def run():
    global logger

    prep_start = time.time()
    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    
    logger.info('Preparing..')

    queue = load_messages()

    logger.info('Finished preparing; starting send with queue of length: {}'.format(len(queue)))
    prep_time = time.time() - prep_start

    logger.info('Finished preparing; now sending..')
    
    start_time = time.time()
    count = 0

    try:
        exc_info = sys.exc_info()
        
        for msg in queue:
            count += 1
            producer.send('msgs', msg)

    except Exception as e:
        logger.debug('Unexpected exception while sending: {}'.format(e))
        logger.debug('\n***Full trace:\n{}'.format(traceback.print_exc()))
        traceback.print_exception(*exc_info)
        del exc_info

    finally:
        producer.close()
        
    test_time = time.time() - start_time
    logger.debug('Done! Time elapsed preparing: {}. Time elapsed sending: {}. \nTotal: {}'.format(prep_time, test_time, prep_time + test_time))
    logger.info('Sent {} messages.\n'.format(count))



if __name__ == '__main__':
    run()