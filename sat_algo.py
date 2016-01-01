#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_algo.py
# main function is main 
"""
算法
各种算法的目的是提供对下一天和当天的股价波动范围估计。
哪种算法运行效果比较好（准确率60%以上），说明该算法符合实际情况。
1 系统对不同的指标进行扫描，满足该指标的代码保存起来，对每种指标进行标记‘可信度’
2 取不同指标的交集
3 取2的相反代码

建立模拟环境，用历史数据验证指标是否合理，也就是某指标满足该代码的历史数据。
比如说，WR指标对1年前的数据进行模拟，推测1年后的数据是否满足其真实数据。

技术指标的运用技巧可以细分为7个要素：
1、指标的背离：指标的走向与价格走向不一致，这时应多加注意。
2、指标的交叉：指标的快线与慢线发生相交，根据交叉的情况如“金叉”“死叉”来判断未来价格的走向。
3、指标的高低：指标处于什么状态，超买还是超卖？
4、指标的形态：指标是否处于反转形态？还是持续形态？
5、指标的转折：指标是否发生了转向、调头？这种情况有时是一个趋势的结束和另一个趋势的开始。
6、指标的钝化：指标已失去了敏感度？主要发生在持续形态中。
7、指标的适用范围：指标的定义和特性决定了它预测的时间周期和形态，中线预测指标不能用于短线分析，持续形态分析指标不能用于反转形态等等。
"""

"""
假定对数收益率是独立同分布的
"""

""" 2015-03-22
止损方式： 
1 定额（比例5%等）或止平（就是买入价） ---- 这种方式止损建议不采用，
2 技术： 
  ①股价跌破前一个交易日的中间价；
  ②股价跌破前一个交易日的最低价；
  ③股价跌破5日成本均线（反映市场平均持股成本的一种技术指标,代码CYC）；
  ④股价跌破上升趋势线；
  ⑤股价跌破前期横向整理的支撑位；
  ⑥股价跌破前期震荡收敛形成的底部支撑价位。
  ①股价跌穿上升趋势线或下降支撑线；
  ②股价跌破顶部附近的最低价位；
  ③股价跌穿上升通道的下轨；
  ④股价跌穿上涨过程中形成的跳空缺口（即开盘价超过上一日最高价的空间）。
3 无条件止损，必须要撤的情况，一般发生在重大事故，政策，等方面， 不计成本,夺路而逃的止损称为无条件止损。当市场的基本面发生了根本性转折时,投资者应摒弃任何幻想,不计成本地杀出,以求保存实力,择机再战。基本面的变化往往是难以扭转的。基本面恶化时,投资者应当机立断,砍仓出局。
"""
import time

#不同类型算法的文件
from sat_algo_public import *
from sat_algo_random import *
from sat_algo_ta import *


"""
global var
"""
#debug = True
debug = False

#把算法的命名要求： Algo+自命名

"""
algo start here
"""        

#first tan mei jin
def AlgoTMJ(codes):
    print('algo tmj', len(codes))
    lkdj = TestAlgoKDJ(codes)
    if lkdj != None:
        lmacd = TestAlgoMACD(lkdj)
        lrp=GetAllPrice(lmacd)
        ShowSimpleStockInfo(lrp)
    print('algo tmj end')


# 组合算法的公共函数    
def BuildAlgo(code, ldata, lAlgoName=[], dAlgoParams={}):
    larv = []
    args=None
    for i in range(0, len(lAlgoName)):
        args = dAlgoParams.get(lAlgoName[i])
        if None == args:
            args = dBasicAlgo.get(lAlgoName[i]+'Params')
            if (debug):print(lAlgoName[i], 'get default params', args)
        if (debug): print('args', args)
        b, arv = PublicTestAlgo(code, lAlgoName[i], args, ldata)
        #this Optimization
        #if (not arv.isBuy()):
        #    break
        if b :#and (arv.isWait() or arv.isInvalid()):
            if(debug): print('wait or invalid', arv.chance)
            #break
            larv.append(arv)
    return larv


def JudgeMulti(larv):
    FlagBuy = 0
    FlagSell = 0
    FlagWait = 0
    size = len(larv)
    if size == 0:
        return 
    for i in range(0, size):
        if larv[i].isWait():
            larv[0].chance = 'wait'
            return
        if larv[i].isBuy():
            FlagBuy += 1
            continue
        if larv[i].isSell():
            FlagSell += 1
            continue
        if larv[i].isInvalid():
            larv[0].chance = 'invalid'
            return
    if size == FlagBuy:
        larv[0].chance = 'buy'
    elif size == FlagSell:
        larv[0].chance = 'sell'
    else:
        larv[0].chance = 'wait'

def TestAlgoMulti(code, ldata, lAlgoName, algoFunc, dAlgoParams={}):
    larv = BuildAlgo(code, ldata, lAlgoName, dAlgoParams)
    if algoFunc and len(larv) > 0:
        if (debug): print('larv', len(larv), larv)
        algoFunc(larv)
        return True, larv[0]
    return False, None

##############################################################################
# start: judge+Algo+Test
 
#wr+kdj
def JudgeWR_KDJ(larv):
    JudgeMulti(larv)

def AlgoWR_KDJ(larv):
    JudgeMulti(larv)

def TestAlgoWR_KDJ(code, ldata, dAlgoParams={}):
    lalgoName = ['wr', 'kdj']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoWR_KDJ, dAlgoParams)

#macd+kdj
def JudgeMACD_KDJ(larv):
    JudgeMulti(larv)

def AlgoMACD_KDJ(larv):
    JudgeMulti(larv)

def TestAlgoMACD_KDJ(code, ldata, dAlgoParams={}):
    lalgoName = ['macd','kdj']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoMACD_KDJ, dAlgoParams)


#http://wenku.baidu.com/link?url=yp2OIKR-TqZyubGNGQRdD6zKtOIb0Dk-a4bVLdVvSI6bHGMrgTrXtmjuGS8PlxfabBdqo6K37GTuFUUJgC0mjQAf3dhZrIJoF1HBOCiwicC
# 以下是根据这个链接搞的短线技术指标最佳组合
# 1 kdj+dmi
def JudgeKDJ_DMI(larv):
    JudgeMulti(larv)
    
def AlgoKDJ_DMI(larv):
    JudgeMulti(larv)
    
def TestAlgoKDJ_DMI(code, ldata, dAlgoParams={}):
    lalgoName=['kdj','dmi']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoKDJ_DMI, dAlgoParams)

# 2 dmi+ma+vol -> ma->bbi
def JudgeDMI_BBI_VOL(larv):
    JudgeMulti(larv)
    
def AlgoDMI_BBI_VOL(larv):
    JudgeMulti(larv)
    
def TestAlgoDMI_BBI_VOL(code, ldata, dAlgoParams={}):
    lalgoName=['dmi','bbi', 'vol']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoDMI_BBI_VOL, dAlgoParams)

# 3 macd+ma+vol -> ma->bbi
def JudgeMACD_BBI_VOL(larv):
    JudgeMulti(larv)
    
def AlgoMACD_BBI_VOL(larv):
    JudgeMulti(larv)
        
def TestAlgoMACD_BBI_VOL(code, ldata, dAlgoParams={}):
    lalgoName=['macd','bbi', 'vol']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoMACD_BBI_VOL, dAlgoParams)

# 4 kdj+rsi+macd #kdj, rsi, macd 短线操作，并且寻求中线支持 
def JudgeKDJ_RSI_MACD(larv):
    # 如果judge函数的逻辑和judgeMulti不一样，则需要自己做判断
    JudgeMulti(larv)
    
def AlgoKDJ_RSI_MACD(larv):
    JudgeMulti(larv)
    
def TestAlgoKDJ_RSI_MACD(code, ldata, dAlgoParams={}):
    lalgoName=['kdj','rsi', 'macd']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoKDJ_RSI_MACD, dAlgoParams)

# 5 wr+kdj+rsi+macd
def JudgeWR_KDJ_RSI_MACD(larv):
    JudgeMulti(larv)
    
def AlgoWR_KDJ_RSI_MACD(larv):
    JudgeMulti(larv)
    
def TestAlgoWR_KDJ_RSI_MACD(code, ldata, dAlgoParams={}):
    lalgoName=['wr','kdj''rsi''macd']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoWR_KDJ_RSI_MACD, dAlgoParams)

# 6 kdj+rsi+dmi
def JudgeKDJ_RSI_DMI(larv):
    JudgeMulti(larv)
    
def AlgoKDJ_RSI_DMI(larv):
    JudgeMulti(larv)
    
def TestAlgoKDJ_RSI_DMI(code, ldata, dAlgoParams={}):
    lalgoName=['kdj','rsi', 'dmi']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoKDJ_RSI_DMI, dAlgoParams)

# 7 ma+bias+36bias ma->bbi
def JudgeBBI_BIAS_BIAS36(larv):
    JudgeMulti(larv)
    
def AlgoBBI_BIAS_BIAS36(larv):
    JudgeMulti(larv)
     
def TestAlgoBBI_BIAS_BIAS36(code, ldata, dAlgoParams={}):
    lalgoName=['bbi','bias', 'bias36']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoBBI_BIAS_BIAS36, dAlgoParams)

# 8 obv+wvad+vol+ma ma->bbi
def JudgeOBV_WVAD_VOL_BBI(larv):
    JudgeMulti(larv)
    
def AlgoOBV_WVAD_VOL_BBI(larv):
    JudgeMulti(larv)
    
def TestAlgoOBV_WVAD_VOL_BBI(code, ldata, dAlgoParams={}):
    lalgoName=['obv','wvad', 'vol','bbi']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoOBV_WVAD_VOL_BBI, dAlgoParams)

# 9 dmi+wr
def JudgeDMI_WR(larv):
    JudgeMulti(larv)
    
def AlgoDMI_WR(larv):
    JudgeMulti(larv)
    
def TestAlgoDMI_WR(code, ldata, dAlgoParams={}):
    lalgoName=['dmi','wr']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoDMI_WR, dAlgoParams)

# 10 dmi+rsi
def JudgeDMI_RSI(larv):
    JudgeMulti(larv)
    
def AlgoDMI_RSI(larv):
    JudgeMulti(larv)
    
def TestAlgoDMI_RSI(code, ldata, dAlgoParams={}):
    lalgoName=['dmi','rsi']
    return TestAlgoMulti(code, ldata, lalgoName, AlgoDMI_RSI, dAlgoParams)

"""
#2015-04-04 采用最简单的止损方式， 短期最高点的大致黄金比例点
simple sell algo: stop loss
1. cur price
2. highest price in N days
3. lowest price in N days
4. stop loss point
5. cur price vs stop loss point
"""
arrStopLoss = [(15/16), (7/8), (3/4)]

def AlgoStopLoss(code, ldata, N=10, level=0):
    if (level < 0) or (level > len(arrStopLoss)):
        level = 0
    if len(ldata) >= 3:
       c,h,l = ldata[0], ldata[1], ldata[2]
       curPrice = c[0]
       highestPrice = h[:N].max()
       lowPrice = l[:N].min()
       stopLoss = highestPrice * arrStopLoss[level] # key point
       diffValue = curPrice - stopLoss
       diffRate = ((curPrice - stopLoss) / curPrice)
       print('code: stopLoss, diffValue, diffRate, curPrice, highestPrice, lowPrice')
       print(code,':', stopLoss, diffValue, diffRate, curPrice, highestPrice, lowPrice)


def SelectCodes(totalCodes, delCodes):
    dTotalCodes={}
    for i in range(0, len(totalCodes)):
        dTotalCodes[totalCodes[i]]=totalCodes[i]
    for i in range(0, len(delCodes)):
        if delCodes[i] in dTotalCodes:
            del dTotalCodes[delCodes[i]]
    codes=[]
    for i in dTotalCodes:
        codes.append(dTotalCodes[i])
    print('save codes:', len(codes), codes)
    return codes

if __name__ == '__main__':
    start = time.time()
    c,qcodes=GetCodesBySingleKeyLimit('*cur',2, 100)
    codes=[]
    for i in range(0, len(qcodes)):
        if qcodes[i][0] != '3':
            codes.append(qcodes[i])
    print('query codes size', len(codes))

    codes=['600703', '000802', '603009', '000719', '002604', '600010', '600680', '002703', '002015', '601798', '002187', '000970', '600189', '002498', '000803', '601890', '000958', '600225', '600379', '200030']

    dParams={'kdj':[19,3,3]}
    lbuys=[]
    lsells=[]
    b = False
    arv = None
    ldata=[]
    for i in range(0, len(codes)):
        ldata = GetSrcDataByIndi(codes[i], 'kdj')
#        b,arv = TestAlgoDMI(codes[i], ldata)
        b,arv = TestAlgoKDJ(codes[i], ldata, 9,3,3)
#        b,arv = TestAlgoWR(codes[i], ldata, 13)
#        b,arv = TestAlgoWR_KDJ(codes[i], ldata) 
#        b,arv = TestAlgoMACD_KDJ(codes[i], ldata)
#        b,arv = TestAlgoKDJ_DMI(codes[i], ldata, dParams) #1
#        b,arv = TestAlgoDMI_BBI_VOL(codes[i], ldata)#2
#        b,arv = TestAlgoMACD_BBI_VOL(codes[i], ldata)#3
#        b,arv = TestAlgoMACD(codes[i], ldata)
#        b,arv = TestAlgoKDJ(codes[i], ldata)
#        b,arv = TestAlgoKDJ_RSI_MACD(codes[i], ldata)#4
#        b,arv = TestAlgoWR_KDJ_RSI_MACD(codes[i], ldata)#5
#        b,arv = TestAlgoKDJ_RSI_DMI(codes[i], ldata)#6
#        b,arv = TestAlgoBBI_BIAS_BIAS36(codes[i], ldata)#7
#        b,arv = TestAlgoOBV_WVAD_VOL_BBI(codes[i], ldata)#8
#        b,arv = TestAlgoDMI_WR(codes[i], ldata)
#        b,arv = TestAlgoDMI_RSI(codes[i], ldata)
        if b:
            arv.saveBuySellCode(lbuys, lsells)
    print('buys', len(lbuys), lbuys)
    print('sells', len(lsells), lsells)
    # stop loss point:
    codes=['600692']
    for i in range(0, len(codes)):
        ldata = GetSrcDataByIndi(codes[i], 'kdj')
        AlgoStopLoss(codes[i], ldata)
    
    # query 
    codes= ['000418', '002322', '002671', '002664', '000719', '603003', '000915', '002388', '002460', '000023', '600219', '600485', '600998', '600387', '600693']
    codess=['000418', '002322', '002671', '002664', '000719', '603003', '000915', '002388', '002460', '000023', '600219', '600485', '600998', '600387', '600693']
    delCodes = []
    saveCodes = SelectCodes(codes, delCodes)
    savCodes = ['600298', '600343', '600392', '600187', '600778', '601991', '002499', '600962', '002140', '002069', '002045', '002415', '600879', '600711', '600459', '600398', '000811', '000719', '600104', '600059', '000581', '600754', '002689', '600580', '600891', '603788', '600540', '000998', '600761', '002187', '600501', '002212', '600292', '000901', '600372', '601000', '000910', '600192', '002606', '600505', '002150', '600993', '600566', '002025']

    end = time.time()
    print("total seconds %d" %(end - start))


"""
2015-04-04  记录优化点
核心问题：
1、dmi+kdj算法优化
2、开发新的算法，和dmi+kdj起到配合的作用
3、对盘整，上升，下降的情况，哪些指标能区分这些？换句话说哪些指标适用不同的情况。
其它必须要做的事情：
4、对数据库层和应用层分离，对读写数据库分离，
5、对kdj这些已经计算的值是保存起来，而不是每次都计算，但是会产生新的问题，参数变化之后，这些kdj的值就是变化的，那么存储数据会非常大和增加数据时必须把所有参数都要算一遍，这两个问题怎么解决？ 哪种方式更好？ 先搞出来测试。
6、数据验证，对原始数据验证和对kdj等指标的数据验证，保证数据是对的，数据对比参照同花顺。
7、提供可视化

"""


