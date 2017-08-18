# -*- coding: utf-8 -*-

from concurrent import futures
import time

import grpc

from util.ctr.dsp.grpc.ctr_predict_pb2 import OutputReply
from util.ctr.dsp.grpc.ctr_predict_pb2_grpc import DSPCtrServicer, add_DSPCtrServicer_to_server
from util.ctr.dsp.dsp_predict import OnlineService

#_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_ONE_DAY_IN_SECONDS = 120

class DSPCtr(DSPCtrServicer):

    def Predict(self, request, context):
        data = request.data
        predict_service = OnlineService.getInstance()
        predict = predict_service.predict(data)
        print(predict)
        return OutputReply(result=predict)


def serve():
    predict_service = OnlineService.getInstance()
    print('begin load weights')
    predict_service.load_w('/home/laomie/projects/python/data/dsp_model.csv')
    predict_service.load_learner(.1, .4, .08)
    print('end load weights')
    rpc_service = DSPCtr()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_DSPCtrServicer_to_server(rpc_service, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
            print("reload weights")
            #predict_service.load_learner(.1, .4, .08)

    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
