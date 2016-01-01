#include <iostream>
#include <string>
//#include <socket>

using namespace std;

enum enumDATA_SINA_STOCK_ITEM_INDEX
{
    DATA_SINA_STOCK_ITEM_INDEX_StockCode,
    DATA_SINA_STOCK_ITEM_INDEX_StockName,
    DATA_SINA_STOCK_ITEM_INDEX_OpenPrice,
    DATA_SINA_STOCK_ITEM_INDEX_YesterdayClosePrice,
    DATA_SINA_STOCK_ITEM_INDEX_CurrentPrice,
    DATA_SINA_STOCK_ITEM_INDEX_HighPrice,
    DATA_SINA_STOCK_ITEM_INDEX_LowPrice,
    DATA_SINA_STOCK_ITEM_INDEX_BuyPrice,
    DATA_SINA_STOCK_ITEM_INDEX_SellPrice,
    DATA_SINA_STOCK_ITEM_INDEX_Amount,
    DATA_SINA_STOCK_ITEM_INDEX_Turnover,
    DATA_SINA_STOCK_ITEM_INDEX_B1Vol,
    DATA_SINA_STOCK_ITEM_INDEX_B1Price,
    DATA_SINA_STOCK_ITEM_INDEX_B2Vol,
    DATA_SINA_STOCK_ITEM_INDEX_B2Price,
    DATA_SINA_STOCK_ITEM_INDEX_B3Vol,
    DATA_SINA_STOCK_ITEM_INDEX_B3Price,
    DATA_SINA_STOCK_ITEM_INDEX_B4Vol,
    DATA_SINA_STOCK_ITEM_INDEX_B4Price,
    DATA_SINA_STOCK_ITEM_INDEX_B5Vol,
    DATA_SINA_STOCK_ITEM_INDEX_B5Price,
    DATA_SINA_STOCK_ITEM_INDEX_S1Vol,
    DATA_SINA_STOCK_ITEM_INDEX_S1Price,
    DATA_SINA_STOCK_ITEM_INDEX_S2Vol,
    DATA_SINA_STOCK_ITEM_INDEX_S2Price,
    DATA_SINA_STOCK_ITEM_INDEX_S3Vol,
    DATA_SINA_STOCK_ITEM_INDEX_S3Price,
    DATA_SINA_STOCK_ITEM_INDEX_S4Vol,
    DATA_SINA_STOCK_ITEM_INDEX_S4Price,
    DATA_SINA_STOCK_ITEM_INDEX_S5Vol,
    DATA_SINA_STOCK_ITEM_INDEX_S5Price,
    DATA_SINA_STOCK_ITEM_INDEX_Date,
    DATA_SINA_STOCK_ITEM_INDEX_Time,
    DATA_SINA_STOCK_ITEM_INDEX_AddData,        //+100,(103表示停牌)
    DATA_SINA_STOCK_ITEM_INDEX_Max
};
extern const wchar_t* DATA_SINA_STOCK_ITEM_Strings[DATA_SINA_STOCK_ITEM_INDEX_Max];

typedef struct tagSINA_STOCK_DATA 
{
    unsigned long long llVal[DATA_SINA_STOCK_ITEM_INDEX_Max];
    int iVip[DATA_SINA_STOCK_SECOND_INDEX_Max];
    CString stockName;
    void ProcessVipData();

    bool GetChangeBit(tagSINA_STOCK_DATA& obj, IntBoolMap& chgBit);
    bool IsStopTrading();
}SINA_STOCK_DATA;

int CSF_SinaStocker::GetSinaPackets(CString strCodes, int iCnt /* = 1 */)
{
    int i;
    m_iCnt = 0;

    CSF_HttpDataReader httpReader;
    //strCodes内容像这样：【sh600000，sz000002】，。。。最多一次可以抓取900个股票的数据
    CString strSinaUrl = L"http://hq.sinajs.cn/list=" + strCodes;
    int len = httpReader.GetHttpData(strSinaUrl,m_bufHttpRead,iCnt*320);
    if (len > 0)
    {
        m_bufHttpRead[len] = 0;
        CString strData = TF_AnsiToUnicode(m_bufHttpRead);

        wstring sData = strData.GetString();
        //delete the end ;
        sData = sData.substr(0, sData.find_last_of(L';', sData.size()-1));

        vector<wstring> vecItem;
        TF_SplitString(sData,L";",vecItem);

        vector<wstring>::iterator it = vecItem.begin();
        while (it != vecItem.end())
        {
            vector<wstring> vecDetail;
            int iCnt = TF_SplitString(*it, L",", vecDetail);
            if (iCnt == (DATA_SINA_STOCK_ITEM_INDEX_Max-1)) //-1 because the stockCode and StockName at the first wstring
            {
                int vecIndex = 0;
                //for the list number after the first one, there has \n char at the var hq_str_sh
                int iStart = vecDetail[vecIndex].find(L'v');        
                if (iStart == -1) 
　　　　　　　　　　　　continue;

                //Stock Code
                m_stockDataArray[m_iCnt].llVal[DATA_SINA_STOCK_ITEM_INDEX_StockCode] = _wtoi(vecDetail[vecIndex].substr(iStart+13, LEN_STOCK_CODE).c_str());
                m_stockDataArray[m_iCnt].stockName.Format(L"%s",vecDetail[vecIndex].substr(iStart+21, vecDetail[vecIndex].size()-(iStart+21)).c_str());
                vecIndex++;

                //Open Price to S5 Price
                for (i=DATA_SINA_STOCK_ITEM_INDEX_OpenPrice;i<=DATA_SINA_STOCK_ITEM_INDEX_S5Price;i++)
                {
                    if ((i == DATA_SINA_STOCK_ITEM_INDEX_Amount) || (i == DATA_SINA_STOCK_ITEM_INDEX_Turnover)
                        || (i == DATA_SINA_STOCK_ITEM_INDEX_B1Vol) || (i == DATA_SINA_STOCK_ITEM_INDEX_B2Vol)
                        || (i == DATA_SINA_STOCK_ITEM_INDEX_B3Vol) || (i == DATA_SINA_STOCK_ITEM_INDEX_B4Vol)
                        || (i == DATA_SINA_STOCK_ITEM_INDEX_B5Vol) || (i == DATA_SINA_STOCK_ITEM_INDEX_S1Vol)
                        || (i == DATA_SINA_STOCK_ITEM_INDEX_S2Vol) || (i == DATA_SINA_STOCK_ITEM_INDEX_S3Vol)
                        || (i == DATA_SINA_STOCK_ITEM_INDEX_S4Vol) || (i == DATA_SINA_STOCK_ITEM_INDEX_S5Vol))
                    {
                        m_stockDataArray[m_iCnt].llVal[i] = (unsigned long long )(_wtof(vecDetail[vecIndex++].c_str()));
                    }
                    else
                    {
                        m_stockDataArray[m_iCnt].llVal[i] = TF_GetCorrectPriceVar(vecDetail[vecIndex++]);
                    }
                }
                //Stock Date
                m_stockDataArray[m_iCnt].llVal[DATA_SINA_STOCK_ITEM_INDEX_Date] = _wtoi(vecDetail[vecIndex].substr(0,4).c_str())*10000 + _wtoi(vecDetail[vecIndex].substr(5,2).c_str())*100 + _wtoi(vecDetail[vecIndex].substr(8,2).c_str());
                vecIndex++;
                //Stock Time
                m_stockDataArray[m_iCnt].llVal[DATA_SINA_STOCK_ITEM_INDEX_Time] = _wtoi(vecDetail[vecIndex].substr(0,4).c_str())*10000 + _wtoi(vecDetail[vecIndex].substr(3,2).c_str())*100 + _wtoi(vecDetail[vecIndex].substr(6,2).c_str());
                vecIndex++;
                //Stock Additional Code
                m_stockDataArray[m_iCnt].llVal[DATA_SINA_STOCK_ITEM_INDEX_AddData] = _wtoi(vecDetail[vecIndex].c_str()) + 100;
                //Process the vip data
                m_stockDataArray[m_iCnt].ProcessVipData();

                m_iCnt++;
            }
            it++;
        }
    }

    return m_iCnt;
}
