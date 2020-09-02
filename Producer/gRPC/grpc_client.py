
""" Implementation of my gRPC executor client."""

import asyncio
import json
import logging
import time

import grpc
from google.protobuf import json_format

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:

# Assuming that we use the docker VM as the gRPC server:
CHANNEL_ADDRESS = '192.168.1.12:50051'

CONTINUE_SENDING = True
TEST_LENGTH = 60

LOGGER_NAME =  'client_logger'
LOG_LOCATION = './log/gRPC_Client.log'
logger = logging.getLogger(LOGGER_NAME)



class GRPCClient():
    """ Responsible for the client/producer duties via gRPC. """    

    def send_unary(self, msg, stub):
        response = stub.HandleCmfxMsg(msg)
        return response


    def run_unary(self, msg_content: str) -> (int, int):
        global logger
        global CONTINUE_SENDING

        sent = 0
        success = 0 

        msg_proto = cmf_pb2.CmfxRequest(contents=msg_content)

        with grpc.insecure_channel(CHANNEL_ADDRESS) as channel:
            stub = cmf_pb2_grpc.ExecutorStub(channel)
            while CONTINUE_SENDING:
                response = self.send_unary(msg_proto, stub)
                sent += 1

                if response.message != 'success':
                    print('\n\nA message was lost or unsuccessful.\n\n')
                    logger.error('A message was lost!!!')

        return (sent, success)


    def send_stream(self, msg_content):
        global CONTINUE_SENDING
        sent = 0

        msg_proto = cmf_pb2.CmfxRequest(contents=msg_content)
        while CONTINUE_SENDING:
            yield msg_proto
            sent += 1

        print('\n\nRequest-streaming gRPC sent {} messages.\n\n'.format(str(sent)))


    def run_stream(self, msg_content: str):
        global logger

        with grpc.insecure_channel(CHANNEL_ADDRESS) as channel:
            stub = cmf_pb2_grpc.ExecutorStub(channel)
            msg_iterator = self.send_stream(msg_content)
            summary = stub.HandleStream(msg_iterator)
            logger.debug('summary: {}'.format(summary.message))



def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)

        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def run_for_length_of_time():
    global CONTINUE_SENDING
    
    test_end = time.time() + TEST_LENGTH

    while CONTINUE_SENDING:
        if time.time() < test_end:
            time.sleep(.5)
        else:
            logger.debug("Breaking because of time.")
            CONTINUE_SENDING = False            



async def run():
    global logger

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    msg_content = open('cmf/lorem.txt', 'r').read().replace('\n', '')
    
    client = GRPCClient()
    
    try:
        await asyncio.gather(
            run_for_length_of_time(),
            client.run_stream(msg_content),
        )        
        
        # (unary_sent, unary_success) = client.run_unary(msg_content)
        # print('\n\nSent: {}\nSuccess: {}'.format(unary_sent, unary_success))


    except KeyboardInterrupt:
        logger.debug('Interrupted by user.')

    except Exception as e:
        logger.exception('Unexpected exception: {}'.format(e))



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()