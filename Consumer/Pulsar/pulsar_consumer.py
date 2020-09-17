from decouple import config

import common
import logging
import pulsar
import sys
import tqdm


LOGGER_NAME = 'pulsar_consumer_logger'
LOG_LOCATION = './log/pulsar_consumer.log'
logger = logging.getLogger(LOGGER_NAME)

LEN_QUEUE = 100980
client = pulsar.Client('pulsar://localhost:6650')
msg_chk = common.MessageChecker()


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.FileHandler(filepath)

    logger.addHandler(handler)
    logger.setLevel(logLevel)

    return logger


# client = pulsar.Client('pulsar://localhost:6650')
# consumer = client.subscribe('my-topic', 'my-subscription')
#
# while True:
#     msg = consumer.receive()
#     print("Received message '%s' id='%s'", msg.data().decode('utf-8'), msg.message_id())
#     consumer.acknowledge(msg)
#
# client.close()


def create_pulsar_consumer():
    return client.subscribe('msgs', 'pulsar-subscription')


def run():
    global logger
    global msg_chk

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)

    consumer = create_pulsar_consumer()

    pbar = tqdm.tqdm(total=LEN_QUEUE)
    count = 0
    try:
        while count < LEN_QUEUE:
            msg = consumer.receive()
            consumer.acknowledge(msg)
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

    finally:
        client.close()
        sys.exit(0)


if __name__ == '__main__':
    run()