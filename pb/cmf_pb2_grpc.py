# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import cmf_pb2 as cmf__pb2


class ExecutorStub(object):
    """The execution service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.HandleCmfxMsg = channel.unary_unary(
                '/Executor/HandleCmfxMsg',
                request_serializer=cmf__pb2.CmfxRequest.SerializeToString,
                response_deserializer=cmf__pb2.ChangeReply.FromString,
                )
        self.HandleStream = channel.stream_unary(
                '/Executor/HandleStream',
                request_serializer=cmf__pb2.CmfxRequest.SerializeToString,
                response_deserializer=cmf__pb2.ChangeReply.FromString,
                )


class ExecutorServicer(object):
    """The execution service definition.
    """

    def HandleCmfxMsg(self, request, context):
        """Sends a request containing a (crude) string repr of "CMFx" 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def HandleStream(self, request_iterator, context):
        """Request-streaming RPC to demonstrate potential difference in speed:
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ExecutorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'HandleCmfxMsg': grpc.unary_unary_rpc_method_handler(
                    servicer.HandleCmfxMsg,
                    request_deserializer=cmf__pb2.CmfxRequest.FromString,
                    response_serializer=cmf__pb2.ChangeReply.SerializeToString,
            ),
            'HandleStream': grpc.stream_unary_rpc_method_handler(
                    servicer.HandleStream,
                    request_deserializer=cmf__pb2.CmfxRequest.FromString,
                    response_serializer=cmf__pb2.ChangeReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Executor', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Executor(object):
    """The execution service definition.
    """

    @staticmethod
    def HandleCmfxMsg(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Executor/HandleCmfxMsg',
            cmf__pb2.CmfxRequest.SerializeToString,
            cmf__pb2.ChangeReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def HandleStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/Executor/HandleStream',
            cmf__pb2.CmfxRequest.SerializeToString,
            cmf__pb2.ChangeReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)