# -*- coding: utf-8 -*-

import os, sys, csv, random

# 0:订单ID, 1:广告ID, 2:媒体ID, 3:价格, 4:exchange id, 5:创意ID, 6:占比(20%写为20)
# 7:浮动比
default_list = ["-1", "-1", "-1", "0", "-1", "-1", "100", "5"]

'''
城市ID映射关系
广东-200 -> 广州4865
浙江-180 -> 杭州4353
福建-190 -> 福州4609
江苏-140 -> 南京3329
河北-90  -> 石家庄2049
安徽-130 -> 合肥3073
黑龙江-50-> 哈尔滨1025
辽宁-70  -> 沈阳1537
山东-110 -> 济南2561
吉林 -60 -> 长春1281
'''
city_map = {"-50":"1025", "-60":"1281", "-70":"1537", "-90":"2049", 
    "-110":"2561", "-130":"3073", "-140":"3329", "-180":"4353", 
    "-190":"4609", "-200":"4865"}
city_values = list(city_map.values())
other_city_id = "99999"

def load_map(map_file: str) -> []:
    '''
    将媒体映射数据载入列表
    :param map_file: 媒体映射文件
    :return: 媒体映射数据列表
    '''
    map_list = []

    with open(map_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter='\t')
        for row in reader:
            map_list.append(row)

    return map_list

def init_order_adv_map(map_list: []) -> {}:
    '''
    将媒体映射数据转为哈希结构
    key为订单ID和广告ID的组合
    value为列表, 内容为key相同的媒体映射数据
    :param map_list: 媒体映射数据
    :return: 哈希结构存的数据
    '''
    order_adv_map = {}

    for row in map_list:
        order_adv = row[0] + "_" + row[1]

        list_value = order_adv_map.get(order_adv)
        if (list_value == None):
            list_value = []

        list_value.append(row)
        order_adv_map[order_adv] = list_value

    return order_adv_map

def exchange_range(ranges: []) -> []:
    '''
    随机交换数组的次序
    :param ranges: 数组
    :return: 随机交换次序的数组
    '''
    result = []
    range_size = len(ranges)

    while(range_size > 0):
        index = random.randint(0, range_size - 1)
        result.append(ranges[index])
        del ranges[index]
        range_size = len(ranges)

    return result

def get_extend_range(map_list: []) -> []:
    '''
    取得占比的调整幅度
    :param map_list: 媒体映射规则列表
    :return: 指定范围里的随机幅度列表
    '''
    ranges = []

    sum_range = 0
    map_size = len(map_list)
    for i in range(0, map_size - 1):
        # 产生指定范围里随机且和收敛于0的小数
        row = map_list[i]
        max_range = float(row[7])
        random_num = round(random.uniform(0, max_range), 2)
        if (sum_range > 0):
            random_num = -1 * random_num

        ranges.append(random_num)
        sum_range = sum_range + random_num

    ranges.append(round(-1 * sum_range, 2))

    return exchange_range(ranges)

def init_map_size(log_list: [], map_list: []):
    '''
    根据占比, 计算每个媒体映射广告日志的点击,展示个数
    :param log_list: 日志数据列表
    :param map_list: 媒体映射规则列表
    :return: 无返回,直接在map_list的元素增加以下列
            8:点击映射个数, 9:点击已映射个数, 10:展示映射个数, 11:展示已映射个数
    '''
    if (map_list != None and len(map_list) > 1):
        # 计算点击,展示数
        click, show = 0, 0
        for row in log_list:
            if row[11] == "5":
                click = click + 1
            if row[11] == "4":
                show = show + 1

        # 计算美个媒体的点击,展示数
        click_usage, show_usage = 0, 0
        map_size = len(map_list)
        ranges = get_extend_range(map_list)

        for i in range(0, map_size - 1):
            row = map_list[i]

            percent = (float(row[6]) + ranges[i]) / 100
            map_click = int(round(click * percent))
            click_usage = click_usage + map_click
            map_show = int(round(show * percent))
            show_usage = show_usage + map_show

            row.append(map_click)
            row.append(0)
            row.append(map_show)
            row.append(0)

        # 最后一个媒体的为总的减去其它的
        row = map_list[map_size - 1]
        row.append(click - click_usage)
        row.append(0)
        row.append(show - show_usage)
        row.append(0)

def search_map_row(map_list: [], map_row_index: {}, log_row: []) -> []:
    '''
    查找日志数据使用的媒体映射规则
    :param map_list: 媒体映射规则列表, 列表中至少2个元素, 没有或单个的不走此方法
    :param map_row_index: 媒体映射规则索引
    :param log_row: 日志数据
    :return:
    '''
    hash_code = log_row[14]
    map_row = map_row_index.get(hash_code)
    if (map_row == None):
        map_size = len(map_list)
        map_index = int(hash_code) % map_size
        map_row = map_list[map_index]

        # 定位点击媒体映射规则,已满的需要向后查找
        if (log_row[11] == "5"):
            # 查找首个点击未满的媒体映射规则
            while (map_row[8] <= int(map_row[9])):
                map_index = (map_index + 1) % map_size
                map_row = map_list[map_index]
        # 其它为展示数据
        else:
            # 查找首个展示未满的媒体映射规则
            while (map_row[10] <= int(map_row[11])):
                map_index = (map_index + 1) % map_size
                map_row = map_list[map_index]

    return map_row

def map_data(log_list: [], map_list: []) -> []:
    '''
    将媒体,广告,exchange id等映射为新的值
    :param log_list: 日志数据列表
    :param map_list: 媒体映射规则列表
    :return: 转换后的日志数据列表
    '''
    city_size = len(city_values)
    # 根据占比计算媒体映射日志的个数
    init_map_size(log_list, map_list)

    # hash_code到媒体映射规则的索引
    map_row_index = {}

    for row in log_list:
        map_row = default_list
        if (map_list != None and len(map_list) > 0):
            if (len(map_list) == 1):
                map_row = map_list[0]
            else:
                map_row = search_map_row(map_list, map_row_index, row)
                # 点击需要保存媒体映射规则,修改已映射媒体个数
                if (row[11] == "5"):
                    hash_code = row[14]
                    map_row_index[hash_code] = map_row
                    map_row[9] = int(map_row[9]) + 1
                else:
                    map_row[11] = int(map_row[11]) + 1

        # 分别替换媒体,价格,exchange id,创意
        row[4], row[10], row[13], row[5] = map_row[2], map_row[3], map_row[4], map_row[5]
        # 城市ID替换
        city_id = row[3]
        if city_map.get(city_id) != None :
            row[3] = city_map.get(city_id)
        if city_id == other_city_id :
            index = random.randint(0, city_size - 1)
            row[3] = city_values[index]

    return log_list

def map_media(log_file: str, map_file: str, out_file: str):
    '''
    媒体等数据映射处理
    :param log_file:
    :param map_file:
    :param out_file:
    :return:
    '''
    map_list = load_map(map_file)
    order_adv_map = init_order_adv_map(map_list)

    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')

        # 用于区分一批日志的键,由订单和广告的组合组成
        pre_order_adv = None
        # 键值相同的一批数据
        log_list = []

        with open(log_file, "r") as csv_input:
            #reader = csv.reader(csv_input, delimiter='\t')
            reader = csv.reader((line.replace('\0', '') for line in csv_input), delimiter='\t')
            for row in reader:
                order_adv = row[1] + "_" + row[5]
                if pre_order_adv == None :
                    pre_order_adv = order_adv

                # 当变换键值(订单和广告)时,处理上一批订单和广告相同的数据
                if (order_adv != pre_order_adv):
                    map_list = order_adv_map.get(pre_order_adv)
                    data_list = map_data(log_list, map_list)
                    writer.writerows(data_list)
                    pre_order_adv = order_adv
                    log_list.clear()

                log_list.append(row)

        if (len(log_list) > 0):
            map_list = order_adv_map.get(pre_order_adv)
            data_list = map_data(log_list, map_list)
            writer.writerows(data_list)

if __name__ == '__main__':
    '''
    log_file:    0:日志时间戳, 1:订单ID, 2:设备类型, 3:城市ID, 4:媒体ID, 5:广告ID, 6:受众属性项ID, 7:用户ID, 8:结算方式
                 9:成本类型, 10:花费, 11:日志类型, 12:时, 13:adwo exchange id, 14:列哈希值
    map_file:    0:订单ID, 1:广告ID, 2:媒体ID, 3:价格, 4:exchange id, 5:创意ID, 6:占比(20%写为20), 7:浮动比
    out_file:    0:日志时间戳, 1:订单ID, 2:设备类型, 3:城市ID, 4:amnet媒体ID, 5:创意ID, 6:受众属性项ID, 7:用户ID, 8:结算方式
                 9:成本类型, 10:花费, 11:日志类型, 12:时, 13:amnet exchange id, 14:列哈希值
    '''
    if (len(sys.argv) > 3):
        log_file = sys.argv[1]
        map_file = sys.argv[2]
        out_file = sys.argv[3]
        map_media(log_file, map_file, out_file)
    else:
        print("usage: python3 create_media.py [log_file] [map_file] [out_file]")
