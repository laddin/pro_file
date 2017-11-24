#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import os
import datetime
import csv
import multiprocessing as mp
import pandas as pd
from sqlalchemy import create_engine
from ipip import IP

# 加载IP库
IP.load(os.path.abspath("17monipdb.dat"))
today_time = datetime.datetime.now().strftime("%Y-%m-%d")
today_name = "/home/data/log_analysis/%s.csv" % today_time
#测试数据
#today_time = "2017-08-27" 
#today_name = "2017-06-09.csv"


# ip地址转换地区
def ip_check(address):
    if len(address.split(".")) == 4:
        try:
            clientip = IP.find(address)
            if clientip not in "中国 钓鱼岛 北京 上海 天津 重庆 黑龙江 吉林 辽宁 内蒙古 河北 新疆 " \
                               "甘肃 青海 陕西 宁夏 河南 山东 山西 安徽 湖南 湖北 江苏 四川 贵州 " \
                               "云南 广西 西藏 浙江 江西 广东 福建 台湾 海南 香港 澳门":
                clientip = "外国"
                return clientip
            return clientip
        except Exception as e:
            return "Null"
    else:
        return "Null"


# log内容处理
def log_process(log):
    if log.count("{") == 1:
        # 换行符处理
        log_coding = log.decode('string_escape').replace("\x09", "")
        log_info = json.loads(log_coding)

        # 需要处理的values
        timestamp = log_info["timestamp"]
        clientip = log_info["clientip"]
        request = log_info["request"]
        http_user_agent = log_info["http_user_agent"]

        # timestamp 格式转换处理
        input_datetime_format = '%d/%b/%Y:%H'
        time_list = timestamp.split(":")[:2]
        timestamp = ":".join(time_list)
        access_time = datetime.datetime.strptime(timestamp, input_datetime_format)

        # clientip ip地址转换地区
        clientip = clientip.encode('utf-8').split(",")
        if clientip[0] == "unknown":
            clientip = clientip[1]
        else:
            clientip = clientip[-1]
        clientip = ip_check(clientip)

        # request 提取url
        request = request.encode('utf-8').split(" ")[1]

        # http_user_agent 提取具体设备
        if ("Linux" or "Android") in http_user_agent:
            http_user_agent = "Android"
        elif "Windows" in http_user_agent:
            http_user_agent = "Windows"
        elif "iPhone" in http_user_agent:
            http_user_agent = "iPhone"
        elif "Mac" in http_user_agent:
            http_user_agent = "Mac"
        else:
            http_user_agent = "other"

        log_info["timestamp"] = str(access_time)
        log_info["clientip"] = clientip
        log_info["request"] = request
        log_info["http_user_agent"] = http_user_agent

        return log_info


# 写csv文件
def save_data(data):
    global today_name
    with open(today_name, 'ab+') as df:
        w = csv.writer(df)
        name = data[0].keys()
        w.writerow(name)
        for x in data:
            if isinstance(x, dict):
                w.writerow(x.values())


def read_log(file_pwd):
    with open(file_pwd) as df:
        for i in df:
            yield i


# 数据统计写入数据库
def pandas_pro(csv_file):
    # 数据库信息
    engine = create_engine(str(r"mysql+pymysql://root:123456@127.0.0.1:3306/nginx_log?charset=utf8"))
    df = pd.read_csv(csv_file)

    # 每小时访问地区
    aaa = df.groupby(["timestamp", "clientip"]).size().reset_index(name='size')
    aaa['logservice'] = 8
    aaa.to_sql('test_time_area', con=engine, if_exists='append', index=False)
    print "time_area is ok"

    # 每个小时CDN
    bbb = df.groupby(["cdnip", "timestamp"]).size().reset_index(name='size')
    bbb['logservice'] = 8
    bbb.to_sql('time_cdn', con=engine, if_exists='append', index=False)
    print "time_cdn is ok"

    # 每小时，最多的域名
    ccc = df.groupby(["timestamp", "domain"]).size().reset_index(name='size')
    ccc['logservice'] = 8
    ccc.to_sql('time_http', con=engine, if_exists='append', index=False)
    print "time_http is ok "

    # 访问状态值异常的查看
    # print df["status"].value_counts()

    # 每个小时的状态值
    ddd = df.groupby(["status", "timestamp"]).size().reset_index(name='size')
    ddd['logservice'] = 8
    ddd.to_sql('time_status', con=engine, if_exists='append', index=False)
    print "time_status is ok "

    # 每个小时设备
    eee = df.groupby(["http_user_agent", "timestamp"]).size().reset_index(name='size')
    eee['logservice'] = 8
    eee.to_sql('time_agent', con=engine, if_exists='append', index=False)
    print "time_agent is ok "

    # 后端响应时间
    fff = df.groupby(["timestamp", "upstream_addr"]).size().reset_index(name='size')
    fff['logservice'] = 8
    fff.to_sql('time_upstream', con=engine, if_exists='append', index=False)
    print "time_upstream is ok"


def main():
    if os.path.isfile(today_name):
        pandas_pro(today_name)
    else:
        file_pwd = '/home/data/wwwlogs/%s_access_log.log' % today_time
        log_info = read_log(file_pwd)
        # 多线程处理
        pool = mp.Pool(processes=(mp.cpu_count() - 1))
        aaa = pool.map(log_process, log_info)
        pool.close()
        pool.join()

        save_data(aaa)
        pandas_pro(today_name)


if __name__ == '__main__':
    main()