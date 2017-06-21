# coding=utf-8

import sys, time, re, os, csv
from datetime import date

list = [
    'http://ip:port/info.',
    'http://ip:port/info.',
]

now = time.strftime("%Y-%m-%d", time.localtime())
print 'now is: ' + now

input_args = sys.argv
data_file = input_args[1]
args = input_args[2:]

def validate_args():
	''' 参数校验 '''
    if not data_file.endswith('.csv') and not args:
        print '''platform: linux; python version: 2.7.0 or newer; require: argvs is not right, first arg is file name with csv suffix, and second argvs is date that format is: yyyy-MM-dd, example: python exportlogtocsv.py data.csv 2017-04-21 2017-04-22'''
        return False
    else:
        for arg in args:
            result = re.search(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})', arg)
            if not result:
                print arg + ' is not right, the format is: yyyy-MM-dd'
                return False
        return True

def gen_url():
	''' url 生成器 '''
    for uri in list:
        for arg in args:
            now_date = date.today()
            log_date = date(int(arg[0:4]), int(arg[5:7]), int(arg[8:]))
            if now_date > log_date:
                url = uri + arg + '.0.log.gz'
                yield url
            elif now_date == log_date:
                url = uri + arg + '.0.log'
                yield url
            
def parse_data():
	''' 
	下载指定的日志文件，并从文件中解析出所需要的信息
	过滤出的temp.txt文件中的信息类似：
	[INFO ][2017/06/21 05:29:33.097][http-nio-8121-exec-5][1b0bf09e7e3f45f78963c4d653f7367d] SomeServiceImpl - 信息关键字[12345678]单一信息[12345678]原始数据[[12345678, 12345678]]类型[2]对应的指定信息[12345678]操作成功，日志关键字~
	或
	[INFO ][2017/06/21 05:29:33.097][http-nio-8121-exec-5][1b0bf09e7e3f45f78963c4d653f7367d] SomeServiceImpl - 信息关键字[12345678]单一信息[12345678]原始数据[[12:34:56:78, 12:34:56:78]]类型[2]对应的指定信息[12345678]操作成功，日志关键字~
	'''
    with open(data_file, 'w') as csvfile:
        fieldnames = ['field1', 'field2', 'field3', 'field4', 'field5']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
                
        for url in gen_url():
            print 'start download: ' + url
            os.system('wget ' + url)
            start_index = url.find('info')
            if url.endswith('gz'):
                end_index = url.find('.gz')
                gfile_name = url[start_index:]
                file_name = url[start_index:end_index]
                os.system('gzip -dv ' + file_name)
            else:
                file_name = url[start_index:]
                gfile_name = ''

            print 'file_name is: ' + file_name
            os.system('grep "日志文件关键字" ' + file_name + ' > temp.txt')

            print 'write ' + url + ' to csv file...'
            with open('temp.txt', 'r') as f:
                for line in f:
                    data_index = line.find('信息关键字')
                    real_data = line[data_index:]
                    match_result = re.findall(r'([0-9:]+)', real_data)
                    arithmetic_type = match_result[-2]
                    opr_id = match_result[-1]
                    value = match_result[2:-2]
                    first_value = value[0]
                    # field3使用':'区分的原因是原始数据中可能包含这种数据'1:2:3'
                    # 使用长度区分field，可以换用其他方式
                    if first_value.find(':') == 1:
                        writer.writerow({'field1': arithmetic_type, 'field2': '', 'field3': value, 'field4': '', 'field5': opr_id})
                    elif len(first_value) > 5:
                        writer.writerow({'field1': arithmetic_type, 'field2': value, 'field3': '', 'field4': '', 'field5': opr_id})
                    else:
                        writer.writerow({'field1': arithmetic_type, 'field2': '', 'field3': '', 'field4': value, 'field5': opr_id})
                        
            print 'write ' + url + ' to csv file done.'

            os.system('rm -rf ' + file_name)
            os.system('rm -rf ' + gfile_name)
            os.system('rm -rf temp.txt')
            print '********** parse ' + url + ' done. **********'

    print '########## all done ##########'
    
if __name__ == '__main__':
    if validate_args():
        parse_data()
