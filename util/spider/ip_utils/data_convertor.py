# -*- coding: utf-8 -*-

import re, csv
import jieba

from util.spider.ip_utils.db_utils import _clawer_db, create_connection, all_adv_region, all_edu_ip

def init_name_code(region_list: []) -> {}:
    name_code_map = {}
    for row in region_list:
        if row is not None and len(row) > 2:
            code = row[0]
            name = row[1]
            if name_code_map.get(name) is not None:
                print('name:' + name + ' code1:' + name_code_map.get(name) + ' code2:' + code)
            name_code_map[name] = code

    return name_code_map

def init_name_father(region_list: []) -> {}:
    name_father_map = {}
    for row in region_list:
        if row is not None and len(row) > 2:
            name = row[1]
            father = row[2]
            if name_father_map.get(name) is not None:
                print('name:' + name + ' father1:' + name_father_map.get(name) + ' father2:' + father)
            name_father_map[name] = father

    return name_father_map

def region_to_area(region_list: []) -> []:
    name_code_map = init_name_code(region_list)
    name_father_map = init_name_father(region_list)
    area_list = []

    for row in region_list:
        if row is not None and len(row) > 2:
            code = row[0]
            name = row[1]
            father = row[2]
            temp_data = [name]
            while father is not None:
                if father != '全球':
                    temp_data.append(father)
                name = father
                father = name_father_map.get(name)

            # 国家，省，市
            area_data = [code]
            for i in range(0, 3):
                name = temp_data.pop() if len(temp_data) > 0 else None
                if name is not None:
                    code = name_code_map.get(name)
                    area_data.append(code)
                    area_data.append(name)
                    area_data.append(name)
                else:
                    area_data.append('')
                    area_data.append('')
                    area_data.append('')

            # 省简称
            province_brief = area_data[6]
            data = re.findall('(.*?)(省|市|自治区|壮族自治区|回族自治区|维吾尔自治区)', province_brief)
            if (len(data) > 0):
                area_data[6] = data[0][0]
            # 市简称
            city_brief = area_data[9]
            data = re.findall('(.*?)(市|地区)', city_brief)
            if (len(data) > 0):
                area_data[9] = data[0][0]

            area_list.append(area_data)

    return area_list


def init_area(csv_file: str):
    conn = create_connection(_clawer_db)
    with conn:
        try:
            region_list = all_adv_region(conn)
            area_list = region_to_area(region_list)
            with open(csv_file, 'w') as output:
                writer = csv.writer(output, delimiter=',', lineterminator='\n')
                writer.writerows(area_list)
        except Exception as e:
            print(e)

def extract_desc(data_list: []) -> []:
    result_list = []
    # 载入自定义词典
    jieba.load_userdict('/home/laomie/keywords.csv')

    for row in data_list:
        if (len(row) > 6):
            begin_ip_desc = row[5]
            desc_list = str(begin_ip_desc).split(' ')
            if len(desc_list) > 1 :
                area = desc_list[0]
                edu = desc_list[1]
                province = ''
                city = ''
                # 结巴分词提前省份，城市
                terms = jieba.cut(area)
                seg_list = ','.join(terms).split(',')
                if (len(seg_list) > 0):
                    if (seg_list[0] == '中国'):
                        temp_list = seg_list[1:]
                        if (len(temp_list) > 0):
                            province = temp_list[0]
                        if (len(temp_list) > 1):
                            city = temp_list[1]

                result = []
                result += row[:5]
                result += [province, city, edu]
                result += row[5:]
                result_list.append(result)

    return result_list


def extract_edu_ip(csv_file: str):
    conn = create_connection(_clawer_db)
    with conn:
        try:
            data_list = all_edu_ip(conn)
            result_list = extract_desc(data_list)
            with open(csv_file, 'w') as output:
                writer = csv.writer(output, delimiter=',', lineterminator='\n')
                writer.writerows(result_list)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    #init_area('/home/laomie/out.csv')
    extract_edu_ip('/home/laomie/out.csv')
