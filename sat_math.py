#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_math.py
# main math 
import time
import numpy as np
#import scipy as sp
from scipy import special
from scipy import stats
from scipy import linalg
import matplotlib.pyplot as plt 
import matplotlib.mlab as mlab

""" 
scipy.cluster 	矢量量化 / K-均值
scipy.constants 	物理和数学常数
scipy.fftpack 	傅里叶变换
scipy.integrate 	积分程序
scipy.interpolate 	插值
scipy.io 	数据输入输出
scipy.linalg 	线性代数程序
scipy.ndimage 	n维图像包
scipy.odr 	正交距离回归
scipy.optimize 	优化
scipy.signal 	信号处理
scipy.sparse 	稀疏矩阵
scipy.spatial 	空间数据结构和算法
scipy.special 	任何特殊数学函数
scipy.stats 	统计
它们全依赖numpy,但是每个之间基本独立。
"""

#debug = False
debug = True

#general indicators print
def GenIndiPrint(u):
    ulen=len(u)
    if ulen < 1:
        return None
    print('最近一天的值',u[0])    
    print('期望值(平均值)', u.mean())
    print('标准差(波动率)',u.std())
    print('最大值', u.max())
    print('最小值', u.min())
    print('方差（标准差的平方）',u.var())
    if ulen >= 6:
        print('最近七天的值',u[0],u[1],u[2],u[3],u[4],u[5],u[6]) 

def List2npArray(l):
    return np.array(l)


#使用ln(Si/Si-1)方式 对数收益率
def CalcYield(lp):
    n=len(lp)
    if n < 1:
        print("lp is invalid") #这种判断应该让调用方处理
        return None
    arrRate = np.zeros(n-1)
    for i in range(0, n-1):
        if lp[i] != 0:
            #arrRate[i]=(lp[i+1]/lp[i])
            arrRate[i]=(lp[i]/lp[i+1])#因为data前面为最新数据
        else:
            arrRate[i]=0
    u = np.log(arrRate)
    if (debug): GenIndiPrint(u)
    return u

#使用（Si-Si-1）/Si-1 简单收益率
def CalcYield2(lp):
    n=len(lp)
    if n < 1:
        print("lp is invalid")
        return None
    u = np.zeros(n-1)
    for i in range(0, n-1):
        if lprice[i] != 0:
            u[i]=((lp[i+1]-lp[i])/lp[i])
        else:
            u[i]=0
    if (debug): GenIndiPrint(u)
    return u

#波动率(Volatility)，一般投资者理解的波动率是计算价格或收益率的标准差；波动率也可以指某一资产的一定时期内最高价减去最低价的值再除以最低价所得到的比率。
#将已知或计算得到的历史波动率与隐含波动率做比较，在隐含波动率低(高)于历史波动率的时点买进(卖出)权证。
#历史波动率：一定时期内各期百分比价格或价格对数收益率的标准差
#HL法波动率：一定时期内最高价减去最低价的值再除以最低价所得到的比率。
#隐含波动率：基础的方法是依据B-S期权定价公式推导得出 TODO ： 没有期权数据
#预测波动率：主要是统计推断或模型法得出
#已实现波动率：OHLC法、日内或高频数据的收益率平方和作为估计值
#实际波动率又称作未来波动率
#未来波动率只能是估计，HL法波动率，预测，隐含，已实现波动率 都是对未来（实际）波动率进行估计
#样本（lp)的数量最好是大于30，并且越大越好，实际情况是1000个左右就能满足要求

#历史波动率：一定时期内各期百分比价格或价格对数收益率的标准差
def CalcVByHistory(lp):
    u=CalcYield(lp)
    if u != None:
        if (debug): u.GenIndiPrint(u)
        return u.std()
    return None

#HL法波动率：一定时期内最高价减去最低价的值再除以最低价所得到的比率。
def CalcVByHL(h,l):
    nH=len(h)
    nL=len(l)
    if nH != nL or nH == 0 or nL == 0:
        return None
    u=np.zeros(nH)
    for i in range(0, nH):
        if l[i] != 0:
            u[i] = (h[i]-l[i]/l[i])
        else:
            u[i] = 0
    if (debug): GenIndiPrint(u)
    #求平均
    return u.mean()

#隐含波动率：基础的方法是依据B-S期权定价公式推导得出 TODO
def CalcVByBS(lp=None):
    if lp == None:
        lp = np.array([1,2,4,8,16,32,64,128])
    n=len(lprice)
    u = CalcYield2(lp)#
    return u.std() #暂时使用历史波动率作为返回值

#预测波动率：主要是统计推断或模型法得出
#1 移動平均法
#移動平均法是指以過去N天的收益率的方差作為當日波動率的估計值，
#分為簡單移動平均和加權移動平均兩種方法。簡單移動平均法將每天的收益率看成是等權重的，加權移動平均法則對不同時點賦予不同的權重。
#简单移动平均 move average simple
def CalcVByMAS(lp):
    u=CalcYield(lp)
    if u != None:
        return u.var() #收益率的方差
    return None

#2 指數平滑法 TODO
#3 GARCH模型法 TODO


#σt=【0.5×(ln(PtH/PtL))^2-(2ln2-1)(ln(PtC / PtO ))^2】^(1/2)
#σt=【0.5×ln(PtH/PtL )-(2ln2-1)ln(PtC / PtO )】^(1/2)
#已实现波动率：OHLC法 收益率平方和作为估计值 
def CalcVByOHCL(o,h,c,l):
    nH=len(h)
    nL=len(l)
    nC=len(c)
    nO=len(o)
    if (nH != nL and nC != nO and nH != nC):
        return None
    u=np.zeros(nH)
    u1=np.zeros(nH)
    u2=np.zeros(nL)
    for i in range(0, nH):
        if l[i] != 0 and o[i] != 0:
            u1[i] = np.log(h[i]/l[i])
            u2[i] = np.log(c[i]/o[i])
            u[i] = np.sqrt(0.5*u1[i]*u1[i] - ((2*np.log(2) - 1)*u2[i]*u2[i]))
        else:
            u[i] = 0
    if (debug): GenIndiPrint(u)
    #高频，就平均？
    return u.mean()
    
def TestOHCL():
    code='000089'
    indicators = ['highest','lowest', 'cur', 'opening']
    n = 1000
    h=sat_dbop.RSingleNumFromRedis(code,indicators[0], n)
    l=sat_dbop.RSingleNumFromRedis(code,indicators[1], n)
    c=sat_dbop.RSingleNumFromRedis(code,indicators[2], n)
    o=sat_dbop.RSingleNumFromRedis(code,indicators[3], n)
    v = CalcVByOHCL(h,l,c,o)
    print('test ohcl', v)

    
#根据最新值，和历史收益率，计算第二天的期望值
def CalcExpected(newP, u):
    e=newP*(np.e**(u.mean()))
    v=newP*newP*(np.e**(2*u.mean()))*(np.e**(u.std()*u.std()) - 1) 
    r = stats.norm.cdf(e,loc=e,scale=u.std())
    #print('e=',e,'v=',u.std(),'r=',r)
    return e,v,r

def IsNormalDis(l):
    #h,p = stats.kstest(l, 'norm') 
    #x = stats.anderson(l, 'norm')
    #x = stats.wilcoxon(l)
    x = np.random.normal(0,1,1000)
    m=np.e*l
    plt.plot(l,m) 
    plt.show() 
    x = stats.shapiro(l)
    #print(help(stats.anderson))
    #print(help(stats.wilcoxon))
    print(help(stats.shapiro))
    print('normal dis: ', x)
    if (debug): print('avg,std,var',l.mean(),l.std(),l.var())
    #print(help(stats.kstest))
    

def TestKS():
    x = np.random.normal(0,1,1000)
    y = stats.shapiro(x)
    test_stat = stats.kstest(x, 'norm')
    print('random norm: ', y, test_stat)
    beta=np.random.beta(7,5,1000)
    print('beta vs norm: ', stats.ks_2samp(beta, x))
    print("------------")
    print('norm data: ', x.mean(),x.std(),x.var())
    print(help(stats.kstest))


#对数据进行画图，看看该数据是怎样的分布
#对数据进行排序的话，那么时间上的因素就忽略掉了
#rvs：随机变量进行取值，通过size给定大小
#pdf：概率密度函数
#cdf：累计分布函数
#sf：生存函数，1-CDF
#ppf：百分点函数，累计分布函数的反函数
#isf：生存函数的反函数
#stats：返回期望和方差（mean()、var()）
def drawNorm(x):
    x.sort()
    print('x,avg,std=', x.mean(), x.std(),'3a=', x.mean()+x.std()*3)
    #y = mlab.normpdf(x, x.mean(), x.std())
    y = stats.norm.cdf(x, x.mean(), x.std())
    z = mlab.normpdf(x.mean(), x.std(),len(x))
    z.sort()
    print('z,avg,std=', z.mean(), z.std(), '3a=', z.mean()+z.std()*3)
    z1 = mlab.normpdf(z, z.mean(),z.std())
    #z1 = stats.norm.pdf(z, z.mean(),z.std())
    plt.plot(x)
    #plt.plot(x,y)
    #plt.plot(z,z1)
    #plt.plot(x)
    plt.show()

def TestPlt():
    #x = np.linspace(-10, 10, 200)
    #x = np.random.normal(0,1,100)
    beta=np.random.beta(7,5,1000)
    #x.sort()
    #y=mlab.normpdf(x,x.mean(), x.std())
    #z=mlab.normpdf(x,x.mean(),x.std()+1)
    #y1=stats.norm.pdf(x,x.mean(),x.std()+2)
    drawNorm(beta)
#fig = plt.figure()
#ax = fig.add_subplot(111)
#t = ax.scatter(x, x)
#print(ax.collections)
#print(t.get_sizes())
#fig.show()
#plt.show()
##print(x)
    #x.sort()
    #y = np.sin(x)
    #z = np.cos(x)
    #y = np.power(10, x)
    #z = np.power(np.e, x)
    #plt.figure(figsize=(8,4)) # 表示画布大小，长8，宽4
#    plt.xlabel("time(s)")
#    plt.ylabel("volt")
#    plt.title("pyPlot ")
#    plt.ylim(-10, 10)#y range
#    plt.legend()
#    #d = stats.expon(loc=0, scale=5)
    #print(d.stats(), d.pdf(6))
    #plt.plot(x, y)
    #plt.plot(x,z)
    #plt.plot(x,y1)
    #plt.show() 
    #plt.bar(left = 0,height = 1)
    

def TestNorm():
    code ='600586'#'601818'
    ind = 'cur'
    lret = sat_dbop.RSingleNumFromRedis(code, ind, 1000)
    if (len(lret) > 0):
        u = List2npArray(lret)
        uY = CalcYield(lret)
        drawNorm(uY)
    print('done test norm')


def MyHelp():
    print(dir(np))
    print(dir(stats))
    print(help(stats.norm.cdf))
    print(help(stats.kstest))

def Test():
    a = np.array([1,2,3,4])
    b = np.array((5,6,7,8))
    c = np.array([[1,2],[6,7]])
    x = np.arange(0,2,0.1)
    print(a,b,'\n',c)
    print(a.shape, b.shape, c.shape)
    print(x)

    l=[]
    for i in range(0, 10):
        l.append(i)

    y = l
    y = np.logspace(0, 1, 12, base=2, endpoint=False)
    print('y= ', y)
    x = np.linspace(0, 2*np.pi, 10, endpoint=False)
    y = np.sin(x)
    x = special.ellipj(1,1)
    print('x= ', x)
    print('y= ', y)
    print(linalg.det(c))

if __name__ == '__main__':
    start = time.time()
    #Test()
    #BS()
    #TestKS()
    TestPlt()
    end = time.time()
    print("math total seconds %d" %(end - start))

 


