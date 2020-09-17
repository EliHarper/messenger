from decouple import config

import common
import logging
import pulsar
import sys
import time
import traceback


client = pulsar.Client(config('PULSAR_URL'))

LOGGER_NAME =  'pulsar_producer_logger'
LOG_LOCATION = './log/pulsar_producer.log'
logger = logging.getLogger(LOGGER_NAME)


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.FileHandler(filepath)
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logLevel)

    return logger


def run():
    global logger

    prep_start = time.time()
    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)

    logger.info('Preparing..')
    queue = common.load_messages()

    logger.info('Finished preparing; starting send with queue of length: {}'.format(len(queue)))
    prep_time = time.time() - prep_start

    logger.info('Finished preparing; now sending..')

    start_time = time.time()
    count = 0

    try:
        exc_info = sys.exc_info()

        producer = client.create_producer('non-persistent://public/default/msgs', compression_type=pulsar.CompressionType.LZ4)

        for msg in queue:
            count += 1
            producer.send(msg.encode('utf-8'))

    except Exception as e:
        logger.debug('Unexpected exception while sending: {}'.format(e))
        logger.debug('\n***Full trace:\n{}'.format(traceback.print_exc()))
        traceback.print_exception(*exc_info)
        del exc_info

    finally:
        client.close()

    test_time = time.time() - start_time
    logger.debug('Done! Time elapsed preparing: {}. Time elapsed sending: {}. \nTotal: {}'.format(prep_time, test_time,
                                                                                                  prep_time + test_time))
    logger.info('Sent {} messages.\n'.format(count))


if __name__ == '__main__':
    run()