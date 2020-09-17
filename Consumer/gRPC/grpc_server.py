""" Implementation of my gRPC executor server.  """

from concurrent import futures

import common
import grpc
import logging
import re
import sys
import tqdm

from google.protobuf.json_format import MessageToJson, MessageToDict

from pb import cmf_pb2, cmf_pb2_grpc


# Global declarations:
LOGGER_NAME = 'server_logger'
LOG_LOCATION = 'log/gRPC_Server.log'
LOG_LEVEL = logging.INFO
logger = logging.getLogger(LOGGER_NAME)

msg_chk = common.MessageChecker()


class Executor(cmf_pb2_grpc.ExecutorServicer):
    """ Executor class to handle RPC service requests. """    
    def __init__(self):
        self._count = 0
        self._errcount = 0


    # Getter for (successful) count:
    @property 
    def count(self):
        return self._count        


    # Getter for total count:
    @property 
    def errcount(self):
        return self._errcount        
        

    def HandleCmfxMsg(self, request, context):
        messagedict = MessageToDict(request)
        message = messagedict['contents']

        if message.startswith('Lorem') and message.endswith('Cur'):
            self._count += 1
            return cmf_pb2.ChangeReply(message='success')
        else:
            self._errcount +=1
            return cmf_pb2.ChangeReply(message='Received, but contents incorrect.')


    def HandleStream(self, request_iterator, context):     
        global logger
        global msg_chk

        count = 0
        pbar = tqdm.tqdm(total=common.LEN_QUEUE)
        
        try:            
            for msg in request_iterator:
                count += 1                
                msg_chk.check_quickly(msg.contents)                
                pbar.update(1)
                if count == common.LEN_QUEUE:
                    pbar.close()

            logger.debug('About to return; successful: {}, total: {}'.format(msg_chk.count, (msg_chk.errcount + msg_chk.count)))
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
    global msg_chk
    
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
        logger.info('\n\nSuccessful count: {}\n\nTotal count: {}'.format(str(msg_chk.count), str(msg_chk.errcount + msg_chk.count)))
        sys.exit(0)


if __name__ == '__main__':
    serve()
