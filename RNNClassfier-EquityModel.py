import pandas as pd
import talib
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import math as math
from sklearn import datasets, linear_model
import statsmodels.formula.api as smf
from scipy.optimize import minimize 

#In order to make the program faster, we can try to calculate the Beta first and write to CSV, and then read the csv in
def BPRatio(stock,enddate):
    fundamental_df = fundamental_df = get_fundamentals(
        query(
            fundamentals.balance_sheet.total_assets,
            fundamentals.balance_sheet.total_equity
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate
    )    
    fundamental_df = fundamental_df.T
    AssetPerEquity = fundamental_df.total_assets/fundamental_df.total_equity
    prices = get_price(list(stock), "{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=10)), enddate, frequency='1d', fields=None)['OpeningPx']
    AssetPerEquityPrice = AssetPerEquity/prices.iloc[-1]
    FactorValue = AssetPerEquityPrice
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

def FLeverage(stock,enddate):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.balance_sheet.long_term_liabilities, 
            fundamentals.balance_sheet.total_assets, 
            fundamentals.balance_sheet.total_equity,
            fundamentals.cash_flow_statement.cash_flow_from_operating_activities,
            fundamentals.financial_indicator.return_on_invested_capital,
            fundamentals.financial_indicator.return_on_equity,
            fundamentals.financial_indicator.return_on_asset
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate
    ) 
    fundamental_df = fundamental_df.T
    Asset = fundamental_df.total_assets
    TEquity = fundamental_df.total_equity
    Financial_Leverage = Asset/TEquity
    FactorValue = Financial_Leverage
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

def CMRatio(stock,enddate):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.balance_sheet.total_equity,
            fundamentals.eod_derivative_indicator.market_cap
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate
    ) 
    fundamental_df = fundamental_df.T
    CE = fundamental_df.total_equity
    MC = fundamental_df.market_cap
    CM = CE/MC
    FactorValue = CM.iloc
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

#Just ROEMA is changed now, is correct spread it to other similiar factors
def ROEMA(stock,enddate):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.financial_indicator.return_on_invested_capital,
            fundamentals.financial_indicator.return_on_equity,
            fundamentals.financial_indicator.return_on_asset
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate,interval = '5y'
    )    
    ROE_raw = fundamental_df.return_on_equity
    ROA_raw = fundamental_df.return_on_asset
    ROIC_raw = fundamental_df.return_on_invested_capital
    #print(ROE)
    #ROE_raw = ROE_raw.T
    ROE = 0.5 * ROE_raw.iloc[0] + 0.5 * 0.5 * ROE_raw.iloc[1] + 0.125 * ROE_raw.iloc[2] + 0.5 * 0.125 * ROE_raw.iloc[3] + 0.5 * 0.5 * 0.125 * ROE_raw.iloc[4]
    FactorValue = ROE.T
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

def ROAMA(stock,enddate):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.financial_indicator.return_on_invested_capital,
            fundamentals.financial_indicator.return_on_equity,
            fundamentals.financial_indicator.return_on_asset
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate,interval = '5y'
    )  
    ROE_raw = fundamental_df.return_on_equity
    ROA_raw = fundamental_df.return_on_asset
    ROIC_raw = fundamental_df.return_on_invested_capital
    #print(ROE)
    ROA = 0.5 * ROA_raw.iloc[0] + 0.5 * 0.5 * ROA_raw.iloc[1] + 0.125 * ROA_raw.iloc[2] + 0.5 * 0.125 * ROA_raw.iloc[3] + 0.5 * 0.5 * 0.125 * ROA_raw.iloc[4]
    FactorValue = ROA
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

def ROICMA(stock,enddate):
    fundamental_df = get_fundamentals(
        query(
            fundamentals.financial_indicator.return_on_invested_capital,
            fundamentals.financial_indicator.return_on_equity,
            fundamentals.financial_indicator.return_on_asset
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),enddate,interval = '5y'
    )    
    ROIC_raw = fundamental_df.return_on_invested_capital
    #print(ROE)
    ROIC = 0.5 * ROIC_raw.iloc[0] + 0.5 * 0.5 * ROIC_raw.iloc[1] + 0.125 * ROIC_raw.iloc[2] + 0.5 * 0.125 * ROIC_raw.iloc[3] + 0.5 * 0.5 * 0.125 * ROIC_raw.iloc[4]
    FactorValue = ROIC
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue
    
def SixMonthsPriceReversal(stock,enddate):
    startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=180))
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        SixMonthsPriceReversal = pd.Series()
        for i in list(range(1,len(stock)+1)):
            SixMonthsPriceReversal = SixMonthsPriceReversal.append(pd.Series((prices.iloc[np.shape(prices)[0]-1][[stock[i-1]]]/prices.iloc[0][[stock[i-1]]])))
        returnv = (SixMonthsPriceReversal)
        FactorValue = returnv
        FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
        return FactorValue
    else:
        return pd.Series(-1000, index = ['000001.XSHE'])
        
def OneMonthsPriceReversal(stock,enddate):
    startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=30))
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        OneMonthsPriceReversal = pd.Series()
        for i in list(range(1,len(stock)+1)):
            OneMonthsPriceReversal = OneMonthsPriceReversal.append(pd.Series((prices.iloc[np.shape(prices)[0]-1][[stock[i-1]]]/prices.iloc[0][[stock[i-1]]])))
        returnv = (OneMonthsPriceReversal)
        FactorValue = returnv
        FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
        return FactorValue
        
def MACD10dayMA(stock,enddate):
    startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=10))
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        MACDMA = prices.iloc[0]
        count = 0
        for eachstock in stock:
            close = prices[eachstock].values
            #print(close)
            if sum(np.isnan(close)) == len(close):
                MACDMA[count] = np.nan
                count = count + 1
            else:
                macd,macdsignal,macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
                MACDMA[count] = pd.rolling_mean(macd,10)[-1]
                count = count + 1
        FactorValue = MACDMA
        FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
        return FactorValue


def HighLow(stock,enddate):
    startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=30))
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        ratio = prices.iloc[0]
        ratio = (prices.max(axis = 0) - prices.iloc[-1])/abs((prices.min(axis = 0) - prices.iloc[-1]))
        return ratio

#Not done yet
def Low130(stock,startdate,enddate):
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None, adjusted=True)['OpeningPx']
        ratio = prices.iloc[0]
        ratio = (prices.max(axis = 0) - prices.iloc[-1])/abs((prices.min(axis = 0) - prices.iloc[-1]))
        FactorValue = ratio
        FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
        return FactorValue


############################Define our factors####################################### 
def RSIIndividual(stock,end):
    window_length = 14
    start = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=window_length))
    data = get_price(list(stock), start, end_date=end, frequency='1d', fields=None)['OpeningPx']
    close = data
    delta = close.diff()
    delta = delta[1:]
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up1 = pd.stats.moments.ewma(up, window_length)
    roll_down1 = pd.stats.moments.ewma(down.abs(), window_length)
    RS1 = roll_up1 / roll_down1
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))
    FactorValue = RSI1.iloc[-1]
    FactorValue = (FactorValue - np.mean(FactorValue))/np.std(FactorValue)
    return FactorValue

def Min130Day(stock,enddate): 
    startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=130))
    if len(stock) != 0 :
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        returns = np.log(prices/prices.shift(1)).iloc[1:-1]
        MinReturn = returns.min()
        FactorValue = MinReturn
        FactorValue = (FactorValue - np.mean(FactorValue))/np.std(FactorValue)
        return FactorValue
    else:
        return pd.Series(1000, index = ['000001.XSHE'])

    
#Thing is that sometimes the date that we input is not working day, if so, we select the most recent working day's value as the value for this
def EquitySize(stock,enddate):
    date = enddate
    fundamental_df = get_fundamentals(
        query(
            fundamentals.eod_derivative_indicator.market_cap 
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),entry_date = enddate
    )
    
    fundamental_df = fundamental_df.T
    #print(fundamental_df)
    FactorValue = fundamental_df['market_cap']
    #print(FactorValue)
    #(FactorValue.iloc[0])
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue
    
def EquityOCFP(stock,enddate):
    date = enddate
    fundamental_df = get_fundamentals(
        query(
            fundamentals.financial_indicator.operating_cash_flow_per_share 
        ).filter(
            fundamentals.income_statement.stockcode.in_(stock)
        ),entry_date = enddate
    )
    prices = get_price(list(stock), "{:%Y-%m-%d}".format(datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=10)), date, frequency='1d', fields=None)['OpeningPx']
    #print(prices.iloc[-1])
    fundamental_df = fundamental_df.T
    FactorValue = fundamental_df['operating_cash_flow_per_share']/prices.iloc[-1]
    FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
    return FactorValue

#Try some new factors
def PricetoLowest(stock,end):
    start = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=260))
    if len(stock) != 0 :
        prices = get_price(list(stock), start, end, frequency='1d', fields=None)['OpeningPx']
        RatiotoLowest = pd.Series()
        for i in list(range(1,len(stock)+1)):
            RatiotoLowest = RatiotoLowest.append(pd.Series((prices.iloc[np.shape(prices)[0]-1][[stock[i-1]]]/min(prices[stock[i-1]]))))
        returnv = (RatiotoLowest)
        FactorValue = returnv
        FactorValue = (FactorValue - np.mean(FactorValue))/np.std(FactorValue)
        return FactorValue
    else:
        return pd.Series(-1000, index = ['000001.XSHE'])

def Volatility(stock,end): 
    start = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=30))
    if len(stock) != 0 :
        #indexprice = get_price('000001.XSHG', startdate, end_date=enddate, frequency='1d', fields=None, adjusted=True)['OpeningPx']
        prices = get_price(list(stock), start, end, frequency='1d', fields=None)['OpeningPx']
        returns = np.log(prices/prices.shift(1)).iloc[1:-1]
        Volatility = pd.Series()
        for i in list(range(1,len(stock)+1)):
            covmat = np.cov(returns[stock[i-1]])
            Volatility = Volatility.set_value(stock[i-1], covmat)
        FactorValue = Volatility
        #print('fv')#,FactorValue.iloc[0:5])
        FactorValue = (FactorValue - np.mean(FactorValue))/np.std(FactorValue)
        return FactorValue
    else:
        return pd.Series(-1000, index = ['000001.XSHE'])

#Factor from Fangzheng FE
def filter_crossstar_stock(stock_list,enddate):
    stock_list_1 = []
    index_pr = history(240, '1m', 'close')['399905.XSHE']
    index_t = history(2,'1d','close')['399905.XSHE'][0]
    Ri = index_pr/index_t-1
    for stk in stock_list:
        stk_pr = history(240, '1m', 'close')[stk]
        stk_t = history(2,'1d','close')[stk][0]
        Rs = stk_pr/stk_t-1
        Re = Rs - Ri
        High = Re.max()
        Low = Re.min()
        Open = Re.ix[0]
        Close = Re.ix[-1]
        bar = abs(Re.ix[0]-Re.ix[-1])
        if Open>Close:
            upline = High - Open
            downline = Close - Low
        else:
            upline = High - Close
            downline = Open - Low
        if bar < 0.001 and upline > bar*3 and downline > bar*3:
            stock_list_1.append(stk)
    return stock_list_1

def sharpe(stock,end):
    start = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=360))
    if len(stock) != 0 :
        prices = get_price(list(stock), start, end, frequency='1d', fields=None)['OpeningPx']
        returns = pd.DataFrame(columns=(stock))
        for i in list(range(1,np.shape(prices)[0]-1)):
            returns.loc[i] = ((prices.iloc[i]/prices.iloc[i-1]-1))
        #print(returns)
        ave = np.nanmean(returns,axis = 0)
        #print(ave)
        std = np.nanstd(returns,axis = 0)
        #print(std)
        sharpe = ((ave-0.04)/std)*np.sqrt(252)
        #print(sharpe)
        returnv = pd.Series(sharpe,index = [stock])
        #print(returnv)
        FactorValue = returnv
        FactorValue = FactorValue.replace([np.inf, -np.inf], np.nan)
        #print(FactorValue.mean())
        #print(FactorValue.std())
        FactorValue = (FactorValue - FactorValue.mean())/FactorValue.std()
        return FactorValue
    else:
        return pd.Series(-1000, index = ['000001.XSHE'])

def CV90Day(stock,enddate): 
    if len(stock) != 0 :
        end = enddate
        startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=110))
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        #returns = np.log(prices/prices.shift(1)).iloc[1:-1]
        CV = pd.Series()
        for i in list(range(1,len(stock)+1)):
            CV.loc[stock[i-1]] = np.std(prices[stock[i-1]])/np.mean(prices[stock[i-1]])
        return CV
    else:
        return pd.Series(1000, index = ['000001.XSHE'])

def SixMonthsPriceReversal(stock,enddate):
    if len(stock) != 0 :
        startdate = "{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=180))
        prices = get_price(list(stock), startdate, end_date=enddate, frequency='1d', fields=None)['OpeningPx']
        SixMonthsPriceReversal = pd.Series()
        for i in list(range(1,len(stock)+1)):
            SixMonthsPriceReversal = SixMonthsPriceReversal.append(pd.Series((prices.iloc[np.shape(prices)[0]-1][[stock[i-1]]]/prices.iloc[0][[stock[i-1]]])))
        returnv = (SixMonthsPriceReversal)
        return returnv
    else:
        return pd.Series(-1000, index = ['000001.XSHE'])

#######################Some tools that is used in the previous functions#############
#This function is used in the later function
def lamtotal(lam,h):
    total = 0
    for i in list(range(h,-1,-1)):
        total = total + lam ** (i)
    return total

#input as Series, date of series should be increasing
#We also need to deal with isnan here, modify this part later
def EWMA(Series1,Series2,lam,h):
    Sm1 = np.mean(Series1)
    Sm2 = np.mean(Series2)
    l1 = len(Series1)
    l2 = len(Series2)
    total = 0
    for i in list(range(h,0,-1)):
        #print(Series1.iloc[l1-i])
        #if ~np.isnan(Series1.iloc[l1-i])&~np.isnan(Series1.iloc[l1-i]):
        total = total + ((lam ** i) *(Series1.iloc[l1-i] - Sm1)*(Series2.iloc[l1-i] - Sm2))
    total = total/lamtotal(lam,i)
    return total
    
##########################Get the exposure on factors of indices####################
#######For Hedging purpose, get the number of the factors in our input
def NumberofArgs(*args):
    for i in list(range(0,1000)):
        try:
            args[i]
        except:
            break
    return i

############################Get the exposre on a factor########################
def GetIndSinExp(f,*args):
    return f(*args)

#Get the exposure of all factors
#Here the stock should be the compoment of the index that we want to use to hedge
def GetIndAllExp(stock,enddate,*args):
    OutValue = []
    for arg in args[0]:
        #print(arg)
        temp = arg(stock,enddate)
        #print(temp)
        #print(type(temp))
        OutValue.append(np.mean(temp.values))
    return OutValue

##########################Get the Beta in the history
def GetAllBeta(stock,enddate,*args):
    OutValue = []
    for arg in args[0]:
        OutValue.extend(GetBeta(arg,stock,enddate).tolist()[0])
    return OutValue

##########################This is for getting the expected return from stocks, use all the data in the paste 3 years
def GetBetaHis(f,*args):
    stock = args[0]
    date = args[1]
    LookingBackWindow = 5 #This is the number of months that we want to get the value
    #Get 20 Business day's data
    AllFactorValues = pd.Series()
    AllReturns = pd.Series()
    DataAll = pd.DataFrame()
    for i in list(range(1,(LookingBackWindow+1))):
        tempend = "{:%Y-%m-%d}".format(datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=(i-1)*30))
        #print(tempend)
        tempprice = get_price(list(stock), "{:%Y-%m-%d}".format(datetime.datetime.strptime(tempend, '%Y-%m-%d') - datetime.timedelta(days = 30)),tempend, frequency='1d', fields=None)['OpeningPx']
        tempreturn = np.log(tempprice.iloc[-1]/tempprice.iloc[0])
        #Store the stock returns in this month
        AllReturns = AllReturns.append(tempreturn)
        #print(tempreturn.shape)
        #Store the factor values in the beginning of this date
        tempFactor = f(stock,"{:%Y-%m-%d}".format(datetime.datetime.strptime(tempend, '%Y-%m-%d') - datetime.timedelta(days = 30)))
        #print(tempFactor.shape)
        AllFactorValues = AllFactorValues.append(tempFactor)
        tempAll = pd.concat([tempFactor,tempreturn],axis = 1)
        tempAll.columns = ['f','p']
        DataAll = DataAll.append(tempAll)
        #print(DataAll.shape)
    #DataAll = pd.concat([AllFactorValues,AllReturns],axis = 1)
    DataAll.replace([np.inf, -np.inf], np.nan)
    DataAll = DataAll.dropna()
    DataAll.columns = ['f','p']
    try:
        results = smf.ols('p~f',DataAll).fit()
        tv = results.tvalues[1]
        coef = results.params[1]
        returns = [coef,tv]
    except:
        returns = [0,0]
    return returns
    
def GetAllBetaHis(stock,enddate,*args):
    OutCoef = []
    OutT = []
    print('Here')
    for arg in args[0]:
        print(arg)
        temp = GetBetaHis(arg,stock,enddate)
        print(temp)
        OutCoef.extend([temp[0]])
        OutT.extend([temp[1]])
    OutValue = pd.DataFrame(
    {'OutCoef': OutCoef,
     'OutT': OutT
    })
    return OutValue
########################Get Factor Exposure at a specific date
def GetAllFactorExposure(stock,enddate,*args):  #Output is directly dataframe
    OutValue = []
    flag = 1
    for arg in args[0]:
        if flag == 1:
            OutValue = pd.DataFrame(arg(stock,enddate))
            #print(OutValue.shape)，这块基本上没问题了
            flag = 0
        else:
            OutValue = pd.concat([OutValue,arg(stock,enddate)],axis = 1)
            #print(OutValue.shape)
    OutValue.columns = list(range(1,len(args[0])+1))
    return OutValue

import numpy
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import np_utils
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.layers import SimpleRNN, Activation

def choose_stocks(context,bar_dict):
    #########################Get the exposure of factors on this stock#######
    end = "{:%Y-%m-%d}".format(get_previous_trading_date(context.now)) 
    enddate = end
    
    MyFactors = [RSIIndividual,Min130Day,PricetoLowest,sharpe,OneMonthsPriceReversal]
    
    AllStock = index_components('000300.XSHG') #this is the stock pool for selection
    stock = AllStock

    enddatel = []
    enddatel1 = []
    for i in list(range(1,4)):
        enddatel.append("{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=(31*i))))
        enddatel1.append("{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=(31*i-30))))
    
    AllData = pd.DataFrame()
    for i in list(range(0,len(enddatel))):
        print(i)
        Xinput = GetAllFactorExposure(stock,enddatel[i],MyFactors)
        testp = get_price(list(stock), enddatel[i], enddatel1[i], frequency='1d', fields=None)['OpeningPx']
        testi = get_price('000300.XSHG', enddatel[i], enddatel1[i], frequency='1d', fields=None)['OpeningPx']
        y = np.log(testp.iloc[-1]/testp.iloc[0]) - np.log(testi.iloc[-1]/testi.iloc[0])
        temp = pd.concat([Xinput,y],axis = 1)
        temp = temp.dropna()
        if i == 0:
            AllData = temp
        else:
            AllData = AllData.append(temp)
    size = AllData.shape
    print(size)
    #print(AllData)
    AllData.columns = list(range(0,size[1]))

    #Generate New Data
    size = AllData.shape
    AllData['Newy'] = AllData.ix[1,size[1]-1] 
    #Change the New y to classfier
    AllData['Newy'][AllData.values[:,size[1]-1] < -0.05] = 0
    AllData['Newy'][(AllData.values[:,size[1]-1] >= -0.05)&(AllData.values[:,size[1]-1] < 0)] = 1
    AllData['Newy'][(AllData.values[:,size[1]-1] >= 0)&(AllData.values[:,size[1]-1] < 0.05)] = 2
    AllData['Newy'][(AllData.values[:,size[1]-1] >= 0.05)] = 3
    
    X_input_raw = AllData.ix[:,0:len(MyFactors)]
    
    Y_input_raw = AllData['Newy']
    Y_input_raw.shape
    UniStock = np.unique(X_input_raw.index.values)
    
    AllFacRes = np.array([])
    AllRet = np.array([])
    count = 0
    for stock in UniStock:
        tempAllRes = X_input_raw.loc[stock].values
        if tempAllRes.shape[0] == 3:
            AllFacRes = np.append(AllFacRes,tempAllRes)
            AllRet = np.append(AllRet,Y_input_raw.loc[stock].values[0])
            count = count + 1
    #Already normalized, so no need to normalize agian here
    AllFacRes = np.reshape(AllFacRes, (count, 3, 5))
    
    #Prepare x_train and y_train
    y_train = np_utils.to_categorical(AllRet, nb_classes=4)
    x_train = AllFacRes

    #Define RNN Model
    model = Sequential()
    print(type(model))
    print(len(MyFactors))
    print((3,len(MyFactors)))
    model.add(LSTM(batch_input_shape=(None,3, len(MyFactors)),output_dim=20,))
    model.add(Dense(4)) #Because we have 4 kinds of output
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
    
    print(len(MyFactors),x_train.shape,y_train.shape)
    model.fit(x_train, y_train, nb_epoch=200, batch_size=30, verbose=2)
    
    #Prepare data fro prediction
    AllStock = index_components('000300.XSHG') #this is the stock pool for selection
    stock = AllStock
    enddatel = []
    for i in list(range(1,4)):
        enddatel.append("{:%Y-%m-%d}".format(datetime.datetime.strptime(enddate, '%Y-%m-%d') - datetime.timedelta(days=(31*i-31))))
    
    AllData = pd.DataFrame()
    for i in list(range(0,len(enddatel))):
        print(i)
        Xinput = GetAllFactorExposure(stock,enddatel[i],MyFactors)
        temp = Xinput
        if i == 0:
            AllData = temp
        else:
            AllData = AllData.append(temp)
    
    X_input_raw = AllData
    AllFacRes = np.array([])
    count = 0
    for stock in UniStock:
        tempAllRes = X_input_raw.loc[stock].values
        if tempAllRes.shape[0] == 3:
            AllFacRes = np.append(AllFacRes,tempAllRes)
            count = count + 1
    #Already normalized, so no need to normalize agian here
    NewX = np.reshape(AllFacRes, (count, 3, 5))
    
    trainPredict = model.predict(NewX)
    context.stocks = UniStock[np.argmax(trainPredict, axis=1)==3]
    
    StockNum = len(context.stocks)
    context.weight = np.repeat(1.0/StockNum,StockNum)
    update_universe(context.stocks)

#Get stocks that are currently trading to refine the pool of stock selection
def get_trading_stocks(raw_stocks, bar_dict):
    trading_stocks = []
    for stock in raw_stocks:
        if bar_dict[stock].is_trading:
            trading_stocks.append(stock)
    return trading_stocks
    
def adjust_positions(context, bar_dict):

    for last_stock in context.portfolio.positions:
        if bar_dict[last_stock].is_trading:
            order_target_percent(last_stock,0)
    #firstly we sell out all the stocks in our portfolio to make sure we can get the ideal weight that we need.
    
    to_buy_stocks = context.stocks
    #here in fact we set a limit to how much money we can use
    avail_cash = context.portfolio.cash*context.position_limit
    each_cash = avail_cash/len(to_buy_stocks)
    #logger.info("avail cash is %f, stock num is %d, each stock cash is %f.",avail_cash,len(to_buy_stocks),each_cash )
    for current_stock in to_buy_stocks:
        order_target_value(current_stock, each_cash)    
    portfolio_value = context.portfolio.portfolio_value* context.position_limit 
    order_target_value("510300.XSHG", -(portfolio_value))
    
def init(context):
    context.benchmark = '000300.XSHG'    
    context.stocks = '000300.XSHG'
    context.short_selling_allowed = True
    context.stoplossmultipler= 0.85 #止损 乘数 
    context.stoppofitmultipler= 1000.8 #止盈 乘数
    context.Traded = 0
    context.position_limit  = 0.9
    context.position_num = 10
    context.countdate = 0
    context.holdingperiod = 15
    context.weight = []
    scheduler.run_monthly(choose_stocks, monthday=1, time_rule='before_trading')
    #scheduler.run_monthly(adjust_positions, monthday=1)
    #scheduler.run_weekly(adjust_future, weekday=1)
    
    update_universe([context.stocks])
    
def before_trading(context, bar_dict):
    pass

def handle_bar(context, bar_dict):
    #if context.Traded == 1:
        #stoploss(context,bar_dict)
    #if context.countdate%context.holdingperiod == 1:
    context.average_percent = context.weight
    for i in list(range(0,len(context.weight))):
        order_target_percent(context.stocks[i], context.average_percent[i])
    context.Traded = 1    

