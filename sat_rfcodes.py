#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import sat_down

#debug = True
debug = False

if __name__ == '__main__':
    debug = True
else:
    debug = False

def getCodeInRange(min, max):
    codes = []
    for code in range(min, max+1):
        codestr = "%06d" %code
        codes.append(codestr)
    return codes

def getAllCodes():
    codes = []
    codes.extend(getCodeInRange(0, 999))
    codes.extend(getCodeInRange(2000, 2999))
    codes.extend(getCodeInRange(300000, 300999))
    codes.extend(getCodeInRange(600000, 600999))
    codes.extend(getCodeInRange(601000, 601999))
    codes.extend(getCodeInRange(603000, 603999))

    if(debug): print('codes:', codes)
    return codes
    
def getCodesInfo(codes):
    ldic = []
    curdate = time.strftime("%d/%m/%Y")
    ldic = sat_down.DownMulti(codes)
    print('local code info', ldic)
    wstr = ''
    for i in range(0, len(ldic)):
        if (ldic[i]['cur'] == '0.00'):
            continue
        if(debug): print('code seq, code', i, ldic[i]['code'])
        wstr += ldic[i]['code'] + ',' + ldic[i]['code'] + '.' + ldic[i]['locate'] +',' + ldic[i]['name'] + '\n'
    return wstr

def refreshAllCodesIntoCSV(str):
    f = open('util/latest_codes.csv', 'w', encoding='utf8')
    f.writelines(str)
    f.close()

def getAllCodesInfo():
    codes = getAllCodes()
    wstr = ''
    start = 0
    step = 30
    while (start < len(codes)):
        if(start + step < len(codes)):
            end = start + step
        else:
            end = len(codes)
        if(debug): print('query codes:', codes[start:end])
        wstr += getCodesInfo(codes[start:end])
        start += step
    return wstr

if __name__ == "__main__":
    start = time.time()
    refreshAllCodesIntoCSV(getAllCodesInfo())
    #curdate = time.strftime("%Y%m%d")
    end = time.time()
    print("total seconds %d" %(end - start))
