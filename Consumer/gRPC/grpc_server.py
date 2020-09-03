""" Implementation of my gRPC executor server.  """

from concurrent import futures

import grpc
import logging
from google.protobuf.json_format import MessageToJson, MessageToDict
import re
import sys

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:
LOGGER_NAME = 'server_logger'
LOG_LOCATION = 'log/gRPC_Server.log'
LOG_LEVEL = logging.INFO
logger = logging.getLogger(LOGGER_NAME)

class Executor(cmf_pb2_grpc.ExecutorServicer):
    """ Executor class to handle RPC service requests. """    
    def __init__(self):
        self._count = 0
        self._totalcount = 0


    @property # Getter
    def count(self):
        return self._count        


    @property # Getter
    def totalcount(self):
        return self._totalcount        
        

    def HandleCmfxMsg(self, request, context):
        messagedict = MessageToDict(request)
        message = messagedict['contents']

        if message.startswith('Lorem') and message.endswith('Cur'):
            self._count += 1
            return cmf_pb2.ChangeReply(message='success')
        else:
            self._totalcount +=1
            return cmf_pb2.ChangeReply(message='Received, but contents incorrect.')


    def HandleStream(self, request_iterator, context):     
        # global logger
        # logger.debug('In HandleStream')

        # print('type(request_iterator): {}'.format(type(request_iterator)))
        
        try:            
            for msg in request_iterator:                
                print('FUCKING HIII')
                print(msg.contents)
                message = msg.contents                
                
                # lorem = 'Lorem'
                # loremslice = message[:5]
                # cur = 'Cur'
                # curslice = message[len(message)-3:]

                # print('loremslice: {}'.format(loremslice))
                # print('curslice: {}'.format(curslice))

                # if lorem.upper() == loremslice.upper() and cur.upper() == curslice.upper():
                #     self._count += 1
                #     return cmf_pb2.ChangeReply(message='success')
                # else:
                self._totalcount += 1
                return cmf_pb2.ChangeReply(message='success')
        except Exception as e:
            logger.debug('Unexpected exception (type: {}) occurred while going over messages: {}'.format(type(e),e))            
    



def configure_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    handler = logging.FileHandler(LOG_LOCATION)

    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)

    return logger


def serve():
    global logger
    
    try:
        logger = configure_logger()
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        executor = Executor()
        cmf_pb2_grpc.add_ExecutorServicer_to_server(executor, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        logger.info('Started server.')
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('\n\nSuccessful count: {}\n\nTotal count: {}'.format(str(executor.count), str(executor.totalcount)))
        sys.exit(0)


if __name__ == '__main__':
    serve()
