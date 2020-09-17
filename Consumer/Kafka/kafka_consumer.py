from decouple import config
from json import loads
from kafka import KafkaConsumer

import common
import logging
import sys
import tqdm


TEST_LENGTH = 10

LOGGER_NAME =  'kafka_consumer_logger'
LOG_LOCATION = './log/kafka_consumer.log'
logger = logging.getLogger(LOGGER_NAME)

LEN_QUEUE = 100980
msg_chk = common.MessageChecker()


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)

        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def create_kafka_consumer():
    return KafkaConsumer(
        'msgs',
        bootstrap_servers=[config('KAFKA_URL')],
        value_deserializer=lambda x: loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        api_version=(0,10,1)
    )


def run():
    global logger
    global msg_chk

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)    
    
    consumer = create_kafka_consumer()

    pbar = tqdm.tqdm(total=LEN_QUEUE)
    count = 0
    try:
        for msg in consumer:
            count += 1
            msg_chk.check_quickly(msg.value)
            pbar.update(1)
            if count == LEN_QUEUE:
                pbar.close()
        logger.info('Finished receiving messages. Successful: {}, Unsuccessful: {}'
            .format(msg_chk.count, msg_chk.errcount))

    except Exception as e:
        logger.debug('Shit went down: {}'.format(e))

    except KeyboardInterrupt:
        logger.info('Finished receiving messages. Successful: {}, Unsuccessful: {}'
            .format(msg_chk.count, msg_chk.errcount))
        sys.exit(0)

        
if __name__ == '__main__':
    run()