from decouple import config

import common
import logging
import pulsar
import sys
import tqdm
import traceback


LOGGER_NAME = 'pulsar_consumer_logger'
LOG_LOCATION = './log/pulsar_consumer.log'
logger = logging.getLogger(LOGGER_NAME)

client = pulsar.Client(config('PULSAR_URL'))
msg_chk = common.MessageChecker()


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.FileHandler(filepath)

    logger.addHandler(handler)
    logger.setLevel(logLevel)

    return logger


def create_pulsar_consumer():
    return client.subscribe('non-persistent://public/default/msgs', 'pulsar-subscription')


def run():
    global logger
    global msg_chk

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)

    consumer = create_pulsar_consumer()

    pbar = tqdm.tqdm(total=common.LEN_QUEUE)
    count = 0

    
    try:
        exc_info = sys.exc_info()

        while count < common.LEN_QUEUE:
            msg = consumer.receive()
            consumer.acknowledge(msg)
            count += 1
            msg_chk.check_quickly(msg.data())
            pbar.update(1)
            if count == common.LEN_QUEUE:
                pbar.close()
        logger.info('Finished receiving messages. Successful: {}, Unsuccessful: {}'
                    .format(msg_chk.count, msg_chk.errcount))

    except Exception as e:
        logger.debug('Shit went down: {}'.format(e))
        logger.debug('\n***Full trace:\n{}'.format(traceback.print_exc()))
        traceback.print_exception(*exc_info)
        del exc_info

    except KeyboardInterrupt:
        logger.info('Finished receiving messages. Successful: {}, Unsuccessful: {}'
                    .format(msg_chk.count, msg_chk.errcount))

    finally:
        client.close()
        sys.exit(0)


if __name__ == '__main__':
    run()