# -*- coding: utf-8 -*-

"""
mysql类型转换为hive类型
"""
def mysql_to_hive(mysql_type) :
    temp_type = str(mysql_type).upper()
    hive_type = temp_type

    if (temp_type.startswith("LONGBLOB")):
        hive_type = "BINARY"
    elif (temp_type.startswith("CHAR")):
        hive_type = "STRING"
    elif (temp_type.startswith("VARCHAR")):
        hive_type = "STRING"
    elif (temp_type.startswith("INTEGER")):
        hive_type = "INT"
    elif (temp_type.startswith("DOUBLE")):
        hive_type = "DOUBLE"
    elif (temp_type.startswith("FLOAT")):
        hive_type = "FLOAT"
    elif (temp_type.startswith("DECIMAL")):
        hive_type = "DECIMAL"
    elif (temp_type.startswith("TIMESTAMP")):
        hive_type = "TIMESTAMP"
    elif (temp_type.startswith("DATE")):
        hive_type = "DATE"
    else:
        hive_type = "STRING"

    return hive_type

