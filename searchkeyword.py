# coding=utf-8

import sys, time, re, os, csv
from datetime import date

list = [
    'http://ip:port/info.',
    'http://ip:port/info.',
]

now = time.strftime("%Y-%m-%d", time.localtime())
print 'now is: ' + now

argvs = sys.argv

def validate_args():
    ''' 参数校验 '''
    usage = 'platform: linux; python version: 2.7.0 or newer; require: first arg is keywords, and second argvs is date that format is: yyyy-MM-dd, example: python searchkeyword.py keyword 2017-04-21 2017-04-22'
    if len(argvs) < 3:
        print usage
        return False
    else:
        for arg in argvs[2:]:
            result = re.search(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})', arg)
            if not result:
                print arg + ' is not right, the format is: yyyy-MM-dd'
                return False
        return True

def gen_url():
    ''' url 生成器 '''
    for uri in list:
        for arg in argvs[2:]:
            now_date = date.today()
            log_date = date(int(arg[0:4]), int(arg[5:7]), int(arg[8:]))
            if now_date > log_date:
                url = uri + arg + '.0.log.gz'
                yield url
            elif now_date == log_date:
                url = uri + arg + '.0.log'
                yield url
            
def parse_data():
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
        os.system('grep ' + argvs[1] + ' '+ file_name + ' >> temp.txt')
        os.system('rm -rf ' + file_name)
    print '########## all done. ##########'
    os.system('cat temp.txt')
    os.system('rm -rf temp.txt')
    
if __name__ == '__main__':
    if validate_args():
        parse_data()
