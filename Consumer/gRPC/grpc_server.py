""" Implementation of my gRPC executor server.  """

from concurrent import futures

import grpc
import logging
from google.protobuf.json_format import MessageToJson, MessageToDict

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:
LOGGER_NAME = 'server_logger'
LOG_LOCATION = 'log/gRPC_Server.log'
LOG_LEVEL = logging.INFO
logger = logging.getLogger(LOGGER_NAME)

class Executor(cmf_pb2_grpc.ExecutorServicer):
    def HandleCmfxMsg(self, request, context):
        messagedict = MessageToDict(request)
        message = messagedict['contents']

        if message.startswith('Lorem') and message.endswith('Cur'):
            return cmf_pb2.ChangeReply(message='success')
        else:
            return cmf_pb2.ChangeReply(message='Received, but contents incorrect.')


def configure_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    handler = logging.FileHandler(LOG_LOCATION)

    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)

    return logger


def serve():
    global logger
    
    logger = configure_logger()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cmf_pb2_grpc.add_ExecutorServicer_to_server(Executor(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('Started server.')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
