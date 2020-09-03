
""" Implementation of my gRPC executor client."""

import threading
import json
import logging
import string
import time
from collections import deque

import grpc
from google.protobuf import json_format

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:

# Assuming that we use the docker VM as the gRPC server:
CHANNEL_ADDRESS = '192.168.1.12:50051'

CONTINUE_SENDING = True
TEST_LENGTH = 45

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


    def message_generator(self, lorem: str, queue: deque):
        words = lorem.split()        
        
        for idx, word in enumerate(words):
            words[idx] = word.upper()
            # queue.append(' '.join(words))
            msg = cmf_pb2.CmfxRequest(contents=str(idx))
            queue.append(msg)
        
        print('put em all!')
            

    def send_stream(self, queue: deque):
        print('in send_stream')
        global logger
        global CONTINUE_SENDING
        sent = 0

        print('starting while:')
        for _ in range(0, 10):
            yield queue.popleft()            
        # while True:
            # print('in while')
            
            # if not CONTINUE_SENDING:
            #     print('\n\nbreaking intentionally\n\n')
            #     break
            
            # print('len(queue): {}'.format(len(queue)))
            # print('dequeuing; coninue_sending: {}'.format(CONTINUE_SENDING))            
            # next_item = queue.popleft()
            # print('next_item, type: {}, {}'.format(next_item, type(next_item)))            
            # yield next_item
            # try:
            #     if postyield:
            #         print('time elapsed: {}'.format(time.time() - postyield))
            #         postyield = time.time()
            # except Exception:
            #     postyield = time.time()
            # sent += 1            
            

        print('\n\nRequest-streaming gRPC sent {} messages.\n\n'.format(str(sent)))


    def run_stream(self, queue: deque):
        global logger

        channel = grpc.insecure_channel(CHANNEL_ADDRESS)
        fut = grpc.channel_ready_future(channel)

        while not fut.done():
            print('channel isnt ready')
            time.sleep(1)

        while CONTINUE_SENDING:
            stub = cmf_pb2_grpc.ExecutorStub(channel)
            print('calling send_stream with queue of length: {}'.format(len(queue)))
            msg_iterator = self.send_stream(queue)
            for summary in channel.stream_unary(stub.HandleStream(msg_iterator)):
                logger.debug('summary: {}'.format(summary.message))

        channel.close()
            
            


def configure_logger(name: str, filepath: str, logLevel: int) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filepath)

        logger.addHandler(handler)
        logger.setLevel(logLevel)

        return logger


def run_for_length_of_time(worker):
    global CONTINUE_SENDING        
    global logger

    print('STOPPING IT NOW')
    logger.debug('STOPPING IT NOW')
    CONTINUE_SENDING = False
    worker.join()
    return


def run():
    global logger

    logger = configure_logger(LOGGER_NAME, LOG_LOCATION, logging.DEBUG)
    msg_content = open('cmf/lorem.txt', 'r').read().replace('\n', '')
    
    client = GRPCClient()

    queue = deque()
    worker = threading.Thread(target=client.message_generator(msg_content, queue))
    worker.start()
    
    try:
        print('The wild run thread is fast asleep... zzz..')
        time.sleep(2)
        print('The wild run thread woke up!!!')
        
        print('The wild run thread used run_stream!')
        test = threading.Thread(target=client.run_stream(queue))

        test.start()
        timer = threading.Timer(TEST_LENGTH, run_for_length_of_time, args=(worker,))
        timer.start()
        
        # (unary_sent, unary_success) = client.run_unary(msg_content)
        # print('\n\nSent: {}\nSuccess: {}'.format(unary_sent, unary_success))


    except KeyboardInterrupt:
        logger.debug('Interrupted by user.')

    except Exception as e:
        logger.exception('Unexpected exception: {}'.format(e))



if __name__ == '__main__':
    run()