
""" Implementation of my gRPC executor client."""

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

    def send_grpc(self, msg, stub):
        response = stub.HandleCmfxMsg(msg)
        return response

    def run_unary(self, msg_content: str) -> (int, int):
        global logger

        sent = 0
        success = 0 

        start_time = time.time()
        
        msg_proto = cmf_pb2.CmfxRequest(contents=msg_content)

        with grpc.insecure_channel(CHANNEL_ADDRESS) as channel:
            # May need to create a stub for each msg?
            stub = cmf_pb2_grpc.ExecutorStub(channel)
            while CONTINUE_SENDING:
                if (time.time() - start_time) > TEST_LENGTH:
                    logger.debug('Breaking because time.')
                    logger.debug('Current time: {}\nStart + TEST_LENGTH: {}'.format(str(start_time + TEST_LENGTH))
                    break

                response = self.send_grpc(msg_proto, stub)
                sent += 1

                if response.message == 'success':
                    success += 1

        return sent, success            



def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)

        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def run():
    global logger

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    msg_content = open('cmf/lorem.txt', 'r').read().replace('\n', '')
    print(type(msg_content))
    print(msg_content)
    client = GRPCClient()
    
    try:
        unary_sent, unary_success = client.run_unary(msg_content)
        print('\nSent: {}\nSuccess: {}'.format(unary_sent, unary_success))
        

    except KeyboardInterrupt:
        logger.debug('Interrupted by user.')

    except Exception as e:
        logger.exception('Unexpected exception: {}'.format(e))


if __name__ == '__main__':
    run()