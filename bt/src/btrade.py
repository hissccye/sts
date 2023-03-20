import pandas as pd
import backtrader as bt

import datetime
import os.path
import sys

import pandas as pd
import backtrader as bt

#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../backup-code/new_sts/")
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../backup-code/sts/")
import func
from global_define import *

import args_lib
import sizer
import analizer
import strategy

def get_data(code='300568.SZ',fd=datetime.datetime(2015, 1, 1),td=datetime.datetime(2021, 8, 31)):
    df = pd.read_csv(RAWSTOCK_PATH+code+'.csv')
    df = func.hist_qfq(df)
    df = func.hist_set(df)

    df.to_csv('logs/'+code+'.csv',columns=df.columns,index=True)

    data = bt.feeds.PandasDirectData(
            dataname=df,
            fromdate=fd,
            todate=td,

            high=4,
            low=5,
            open=6,
            close=3,
            volume=9,
            openinterest=-1
        )

    data._name = df.iloc[0]['ts_code']

    return data

def add_single_data(cerebro, code='000001.SZ'):
    data = get_data(code)
    cerebro.adddata(data)

class Btrade:

    def __init__(self):
        pass

    def start(self):
    
        args = args_lib.parse()
    
        code_list = func.get_code(args.c)
    
        cerebro = bt.Cerebro()
    
        strats = cerebro.addstrategy(strategy.TrendStrategy)
    
        for c in code_list:
            add_single_data(cerebro, c)
    
        cerebro.broker.setcash(args.cash)
    
        cerebro.addsizer(sizer.FullSizer)
    
        cerebro.broker.setcommission(commission=0.0)
    
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    
        res = cerebro.run()
    
        analizer.printTradeAnalysis(res[0].analyzers.ta.get_analysis())
    
        if args.plot:
            cerebro.plot()

if __name__ == '__main__':
    t = Btrade()
    t.start()
