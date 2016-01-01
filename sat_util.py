#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

import datetime
import time
 
debug = False
#debug = True 

def ToGB(s):  
    if(debug): print(s)  
    return s.decode('gbk') #gb2312 

def ToUTF8(s):
    if(debug): print(s)
    return s.decode('utf8')

def ToUTF16(s):
    if(debug): print(s)
    return s.decode('utf16')

def suffix2prefix(code):
    if (len(code)>=9):
        fix =code[7:9].lower()
        code = fix + code[0:6]
        return code

def prefix2suffix(code):
    if (len(code)>=8):
        fix =code[0:2].upper()
        code = code[2:8] + '.' + fix
        return code
    
def codeAddPrefix(code):
    if (len(code)<=6):
        if (code[0]=='0'):
            return 'sz'+code
        elif (code[0]=='6'):
            return 'sh'+code
        else:
            return 'sz'+code
    return code    

def codeAddSuffix(code):
    if (len(code)<=6):
        if (code[0]=='0'):
            return code + 'sz'
        elif (code[0]=='6'):
            return code + 'sh'
        else:
            return code + 'sz'
    return code

codesfile="util/A8.csv"

#code source file way 1
def GetAllCodesFromCSV():
    import csv
    c = csv.reader(open(codesfile,encoding='utf8'))
    codes=[]
    for id, code, name in c:
        if id != 'NULL':
            codes.insert(0, id)
        elif code:
            codes.insert(0, code[:6])
        if (debug): print(code)
    return codes

#创建csv文件名称
def CreateFileNameByDate(fPrefix, dtEnd, dtStart):
        return fPrefix + dtEnd.strftime("%Y%m%d")+'_'+dtStart.strftime("%Y%m%d") + '.csv'
    
if __name__ == '__main__':
    start = time.time()
    codes=['601398']
    print(codeAddPrefix(codes[0]))
    codes = GetAllCodesFromCSV()
    print(len(codes), codes)
    end = time.time()
    print("ms %d" %(end - start))
