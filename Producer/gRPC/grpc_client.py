
""" Implementation of my gRPC executor client."""

import common
import concurrent.futures            
import threading
import json
import logging
import string
import time
import sys

from collections import deque
from tqdm import tqdm

import grpc
from google.protobuf import json_format

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:

# Assuming that we use the CentOS VM as the gRPC server:
CHANNEL_ADDRESS = '192.168.1.12:50051'

CONTINUE_SENDING = True
TEST_LENGTH = 10

LOGGER_NAME =  'client_logger'
LOG_LOCATION = './log/gRPC_client.log'
logger = logging.getLogger(LOGGER_NAME)



class GRPCClient():
    """ Responsible for the client/producer duties via gRPC. """    

    def __init__(self):
        self.channel = grpc.insecure_channel(CHANNEL_ADDRESS)
        self.stub = cmf_pb2_grpc.ExecutorStub(self.channel)

    def send_unary(self, msg, stub):
        response = stub.HandleCmfxMsg(msg)
        return response


    def run_unary(self, msg_content: str) -> (int, int):
        global logger
        global CONTINUE_SENDING

        sent = 0
        success = 0 

        msg_proto = cmf_pb2.CmfxRequest(contents=msg_content)

        with self.channel as channel:
            stub = cmf_pb2_grpc.ExecutorStub(channel)
            while CONTINUE_SENDING:
                response = self.send_unary(msg_proto, stub)
                sent += 1

                if response.message != 'success':
                    print('\n\nA message was lost or unsuccessful.\n\n')
                    logger.error('A message was lost!!!')

        return (sent, success)


    def message_generator(self, queue: deque):    
        pbq = deque()

        for msg in queue:
            pbq.append(cmf_pb2.CmfxRequest(contents=(msg)))
        
        logger.info('Converted msgs to pb CmfxRequests!')
        
        return pbq
            

    def send_stream(self, queue: deque):                
        for msg in queue:
            # if idx % 1000 == 0:
            #     print(type(msg))
            # logger.info('sending: {}'.format(msg))
            yield msg
        

    def run_stream(self, queue: deque) -> float:                
        start = time.time()
        logger.info('calling send_stream with queue of length: {}'.format(len(queue)))     
        msg_iterator = self.send_stream(queue)
        summary = self.stub.HandleStream(msg_iterator)        
        logger.debug('summary: {}'.format(summary.message))
        test_time = time.time() - start
        
        return test_time


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)

        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def run_for_length_of_time():
    time.sleep(TEST_LENGTH)
    logger.debug('STOPPING IT NOW') 
    sys.exit(0)


def run():
    global logger

    prep_start = time.time()
    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)

    logger.info('Preparing..')

    queue = common.load_messages()
    
    client = GRPCClient()
    
    pbq = client.message_generator(queue)

    prep_time = time.time() - prep_start

    logger.info('Finished preparing; now sending..')

    try:
        test_time = client.run_stream(pbq)
        
        # (unary_sent, unary_success) = client.run_unary(msg_content)
        # print('\n\nSent: {}\nSuccess: {}'.format(unary_sent, unary_success))

        logger.debug('Prep time: {}, test time: {}, total time elapsed: {}'.format(prep_time, test_time, (prep_time + test_time)))

    except KeyboardInterrupt:
        logger.debug('Interrupted by user.')

    except Exception as e:
        logger.exception('Unexpected exception: {}'.format(e))



if __name__ == '__main__':
    run()