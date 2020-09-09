from decouple import config
from json import loads
from kafka import KafkaConsumer

import logging
import sys
import time


TEST_LENGTH = 10

LOGGER_NAME =  'kafka_producer_logger'
LOG_LOCATION = './log/kafka_producer.log'
logger = logging.getLogger(LOGGER_NAME)

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
    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)    
    
    consumer = create_kafka_consumer()

    msgCount = 0
    try:
        for msg in consumer:
            msgCount += 1

    except Exception as e:
        logger.debug('Shit went down: {}'.format(e))

    except KeyboardInterrupt:
        logger.info('Received {} messages as the KafkaConsumer.'.format(msgCount))
        sys.exit(0)

        
if __name__ == '__main__':
    run()