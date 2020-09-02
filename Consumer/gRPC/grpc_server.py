""" Implementation of my gRPC executor server.  """

from concurrent import futures

import grpc
import logging
from google.protobuf.json_format import MessageToJson, MessageToDict
import sys

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:
LOGGER_NAME = 'server_logger'
LOG_LOCATION = 'log/gRPC_Server.log'
LOG_LEVEL = logging.INFO
logger = logging.getLogger(LOGGER_NAME)

class Executor(cmf_pb2_grpc.ExecutorServicer):
    """ Executor class to handle RPC service requests. """
    # Count the number of successful on server-side as well as client-side:

    def __init__(self, count = 0):
        self._count = count
        

    def HandleCmfxMsg(self, request, context):
        messagedict = MessageToDict(request)
        message = messagedict['contents']

        if message.startswith('Lorem') and message.endswith('Cur'):
            self._count += 1
            return cmf_pb2.ChangeReply(message='success')
        else:
            return cmf_pb2.ChangeReply(message='Received, but contents incorrect.')


    def HandleStream(self, request, context):
        messagedict = MessageToDict(request)
        message = messagedict['contents']

        if message.startswith('Lorem') and message.endswith('Cur'):
            self._count += 1
            return cmf_pb2.ChangeReply(message='success')
        else:
            return cmf_pb2.ChangeReply(message='Received, but contents incorrect.')

    
    @property # Getter
    def count(self):
        return self._count



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
        print('\n\nSuccessful count: {}'.format(str(executor.count)))
        sys.exit(0)


if __name__ == '__main__':
    serve()
