# -*- coding: utf-8 -*-

import sys, time
from pykafka import KafkaClient

def produce_msg(topic, lines):
    print("produce " + lines.count() + "lines.", end='\n')
    with topic.get_sync_producer() as producer:
        for line in lines:
            producer.produce(line)

def send(hosts, topics, log_file, bulk_number):
    # 暂存数据的列表
    lines = []
    # kafka主题
    client = KafkaClient(hosts=hosts)
    topic = client.topics['test']

    # 打开文件并遍历每行，将数据暂存列表
    with open(log_file, "r") as input:
        for line in input:
            lines.append(line)
            # 达到发送数则向kafka发送消息
            if (lines.count() == bulk_number):
                produce_msg(topic, lines)
                time.sleep(10)
                lines.clear()

    if (lines.count() > 0):
        produce_msg(topic, lines)


"""
使用: python log_producer.py hosts topics log_file bulk_number

遍历文件[log_file],以10秒间隔将[bulk_number]行数据推送kafak.
"""
if __name__ == '__main__':
    if (len(sys.argv) > 4):
        hosts = sys.argv[1]
        topics = sys.argv[2]
        log_file = sys.argv[3]
        bulk_number = sys.argv[4]
        send(hosts, topics, log_file, bulk_number)
    else:
        print("python log_producer.py hosts topics log_file bulk_number")