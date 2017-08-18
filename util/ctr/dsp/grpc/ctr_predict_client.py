# -*- coding: utf-8 -*-

from __future__ import print_function

import grpc, gevent, csv, requests
from time import time
from gevent.pool import Pool

from util.ctr.dsp.grpc.ctr_predict_pb2 import InputRequest
from util.ctr.dsp.grpc.ctr_predict_pb2_grpc import DSPCtrStub


def run(test_file: str, submission_file: str):
    data_list = []
    #channel = grpc.insecure_channel('192.168.1.20:50051')
    #stub = DSPCtrStub(channel)
    timeout = 1
    error_count = 0
    pool = Pool(500)

    def predict(line_list: []):
        line_count = len(line_list)
        if line_count > 0:
            # the first column is click value
            click_list = [row[0] for row in line_list]
            query_list = [row[1:] for row in line_list]
            input_list = [','.join(row) for row in query_list]
            input = ';'.join(input_list)

            try:
                with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
                    url = 'http://192.168.1.20:50051/predict/' + input
                    #response = stub.Predict(InputRequest(data=input))
                    #result_list = response.result.split(';') if response is not None else []
                    response = requests.get(url).text
                    result_list = response.split(';') if response is not None else []
                    output_list = result_list if len(result_list) == line_count else [-1] * len(click_list)

            except Exception as e:
                # log(e.args)
                print(e)
                output_list = [-1] * len(click_list)

            for i in range(0, line_count):
                data_list.append([click_list[i], output_list[i]])


    line_list = []
    with open(test_file, 'r') as input:
        reader = csv.reader(input, delimiter=',', lineterminator='\n')
        next(reader)
        for line in reader:
            line_list.append(line)
    line_count = len(line_list)

    start_time = time()

    step = 1
    for i in range(1, line_count + 1):
        remainder = i % step

        if remainder == 0:
            input_list = line_list[i - step : i]
            pool.spawn(predict, input_list)
        else:
            if i == line_count:
                input_list = line_list[i - remainder : i]
                pool.spawn(predict, input_list)

        if i % 2000 == 0:
            print('finish ' + str(i))

    pool.join()

    end_time = time()
    escaped = end_time - start_time
    print("用时:" + str(escaped))
    with open(submission_file, 'w') as submission:
        submission.write('Line,Click,Predicted\n')
        i = 0
        for row in data_list:
            i += 1
            submission.write('%d,%s,%f\n' % (i + 10000000, row[0], float(row[1])))

    print(error_count)


if __name__ == '__main__':
    run('/home/laomie/projects/python/data/show.csv', '/home/laomie/projects/python/data/submission_01.csv')
