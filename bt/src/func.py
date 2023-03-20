import tushare as ts
import pandas  as pd
import numpy  as np
from global_define import *
import re
import os
import datetime

#pd.set_option('display.max_rows',None)
#pd.set_option('display.max_columns',None)
#pd.set_option('display.width',0)

def get_hist(code):
    df = pd.read_csv(HISTDATA_PATH+code+'.csv')
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df = hist_fuquan(df)
    df = hist_reorder(df)
    df = hist_process(df)
    df.set_index(['trade_date'], inplace=True)
    df['idx'] = range(0, len(df))
    return df

def hist_reorder(df):
    df1 = df[::-1].copy()
    df1.reset_index(inplace=True,drop=True)
    #df1.drop(df1.columns[0],axis=1,inplace=True)
    df1.rename(columns={"Unnamed: 0": 'idx'},inplace=True)
    df1['idx'] = df1.index
    return df1

def hist_set(df):
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index(['trade_date'], inplace=True)
    df.rename(columns={"Unnamed: 0": 'idx'},inplace=True)
    df['idx'] = range(0, len(df))
    return df

def get_stock(code, num = -1):
    df = pd.read_csv(RAWSTOCK_PATH+code+'.csv')
    if num != -1:
        df = df.tail(num)
    df = hist_qfq(df)
    #df = hist_hfq(df)
    df = hist_set(df)
    df = hist_process(df)
    return df

def get_stock_with_date(code, st, ed):
    df = pd.read_csv(RAWSTOCK_PATH+code+'.csv')
    df = hist_set(df)
    df = df[(df.index >= st) & (df.index <= ed)]
    df['idx'] = range(0, len(df))
    if len(df) > 0:
        df = hist_qfq(df)
        df = hist_process(df)
    return df

def hist_qfq(df):
    # Note: the date must be from early to latest.
    df.loc[df.index[0], 'pct_chg'] = 0
    df['fuquan_factor'] = (1 + df['pct_chg']/100).cumprod()
    df['_close'] = df['close']
    df['close'] = df['fuquan_factor'] * (df.iloc[-1]['close']/df.iloc[-1]['fuquan_factor'])
    #
    df['open'] = df['open'] * (df['close']/df['_close'])
    df['high'] = df['high'] * (df['close']/df['_close'])
    df['low']  = df['low']  * (df['close']/df['_close'])
    df = df.drop(['_close'], axis=1)
    return df

def hist_hfq(df):
    # Note: the date must be from early to latest.
    df.loc[df.index[0], 'pct_chg'] = 0
    df['fuquan_factor'] = (1 + df['pct_chg']/100).cumprod()
    df['_close'] = df['close']
    df['close'] = df['fuquan_factor'] * df.iloc[0]['close']
    #
    df['open'] = df['open'] * (df['close']/df['_close'])
    df['high'] = df['high'] * (df['close']/df['_close'])
    df['low']  = df['low']  * (df['close']/df['_close'])
    df = df.drop(['_close'], axis=1)
    return df

def hist_fuquan(df):
    df['adjust'] = 0.0
    adjust = 1.0

    for i, row in df.iterrows():
        if i > 0:
            df.at[i, 'adjust'] = adjust
            if df.at[i-1, 'pre_close'] != row['close']:
                adjust *= df.at[i-1, 'pre_close'] / row['close']
                #print("date: {}, close:{}, pre_close:{}, adjust:{}".format(row['trade_date'], row['close'], df.at[i-1, 'pre_close'], adjust))
                #print(i)
            if adjust != 1.0:
                df.at[i, 'open']  *= adjust
                df.at[i, 'high']  *= adjust
                df.at[i, 'low']   *= adjust
                df.at[i, 'close'] *= adjust
    return df

def hist_process(df):
    df['ma5']   = df.close.rolling(window=5).mean()
    df['ma10']  = df.close.rolling(window=10).mean()
    df['ma20']  = df.close.rolling(window=20).mean()
    df['ma30']  = df.close.rolling(window=30).mean()
    df['ma50']  = df.close.rolling(window=50).mean()
    df['ma60']  = df.close.rolling(window=60).mean()
    df['ma120'] = df.close.rolling(window=120).mean()
    df['ma150'] = df.close.rolling(window=150).mean()
    df['ma200'] = df.close.rolling(window=200).mean()
    df['ma240'] = df.close.rolling(window=240).mean()
    
    #df['pre_close'] = df['close'].shift()

    for i, row in df.iterrows():
        idx = row['idx']
        max_v = max(row['high'], df.iloc[row['idx']-1]['close']) if (row['idx'] > 0) else np.nan
        min_v = min(row['low'],  df.iloc[row['idx']-1]['close']) if (row['idx'] > 0) else np.nan
        df.loc[i, 'vibra'] = max_v/min_v - 1
        df.loc[i, 'TR'] = max_v - min_v
        if idx == 20:
            df.loc[i, 'N'] = df.iloc[0:20]['TR'].mean()
        elif idx > 20:
            df.loc[i, 'N'] = (19*df.iloc[idx-1]['N'] + df.loc[i, 'TR'])/20

    df['atr5']  = df.vibra.rolling(window=5).mean()
    df['atr10'] = df.vibra.rolling(window=10).mean()
    df['atr20'] = df.vibra.rolling(window=20).mean()

    df = df.round(3)

    return df

def set_p(idx, df):
    if idx >= len(df):
        print(df)
    x = df.index[idx]
    df.loc[x, 'p5']   = round(df.iloc[idx+5  ]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+5   < len(df)) else np.nan
    df.loc[x, 'p10']  = round(df.iloc[idx+10 ]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+10  < len(df)) else np.nan
    df.loc[x, 'p20']  = round(df.iloc[idx+20 ]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+20  < len(df)) else np.nan
    df.loc[x, 'p30']  = round(df.iloc[idx+30 ]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+30  < len(df)) else np.nan
    df.loc[x, 'p60']  = round(df.iloc[idx+60 ]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+60  < len(df)) else np.nan
    df.loc[x, 'p120'] = round(df.iloc[idx+120]['close'] / df.iloc[idx]['close'] - 1, 4) if (idx+120 < len(df)) else np.nan

def set_price(df):
    for i, row in df.iterrows():
        idx = row['idx']
        set_p(idx, df)
        #df.loc[i, 'p5']   = round(df.loc[i+5  ,'close'] / row['close'] - 1, 4) if (i+5   in df.index) else np.nan
        #df.loc[i, 'p10']  = round(df.loc[i+10 ,'close'] / row['close'] - 1, 4) if (i+10  in df.index) else np.nan
        #df.loc[i, 'p20']  = round(df.loc[i+20 ,'close'] / row['close'] - 1, 4) if (i+20  in df.index) else np.nan
        #df.loc[i, 'p30']  = round(df.loc[i+30 ,'close'] / row['close'] - 1, 4) if (i+30  in df.index) else np.nan
        #df.loc[i, 'p60']  = round(df.loc[i+60 ,'close'] / row['close'] - 1, 4) if (i+60  in df.index) else np.nan
        #df.loc[i, 'p120'] = round(df.loc[i+120,'close'] / row['close'] - 1, 4) if (i+120 in df.index) else np.nan

def get_classes(arg):
    classes = []
    clsmembers = inspect.getmembers(arg, inspect.isclass)
    for (name, _) in clsmembers:
        classes.append(name)
    return classes

def set_stats(df, idx, stat, tag):
    row  = df.loc[idx]
    date = df.loc[idx, 'trade_date']
    stat.loc[date, 'Op']   = tag 
    stat.loc[date, 'Idx']  = idx
    stat.loc[date, 'p1']   = round((df.at[idx+1,'close']   / row['close'] - 1) * 100, 2) if (idx+1   in df.index) else np.nan #'nop'  
    stat.loc[date, 'p3']   = round((df.at[idx+3,'close']   / row['close'] - 1) * 100, 2) if (idx+3   in df.index) else np.nan #'nop'
    stat.loc[date, 'p5']   = round((df.at[idx+5,'close']   / row['close'] - 1) * 100, 2) if (idx+5   in df.index) else np.nan #'nop'
    stat.loc[date, 'p10']  = round((df.at[idx+10,'close']  / row['close'] - 1) * 100, 2) if (idx+10  in df.index) else np.nan #'nop'
    stat.loc[date, 'p20']  = round((df.at[idx+20,'close']  / row['close'] - 1) * 100, 2) if (idx+20  in df.index) else np.nan #'nop'
    stat.loc[date, 'p30']  = round((df.at[idx+30,'close']  / row['close'] - 1) * 100, 2) if (idx+30  in df.index) else np.nan #'nop'
    stat.loc[date, 'p60']  = round((df.at[idx+60,'close']  / row['close'] - 1) * 100, 2) if (idx+60  in df.index) else np.nan #'nop'
    stat.loc[date, 'p120'] = round((df.at[idx+120,'close'] / row['close'] - 1) * 100, 2) if (idx+120 in df.index) else np.nan #'nop'
    stat.loc[date, 'p240'] = round((df.at[idx+240,'close'] / row['close'] - 1) * 100, 2) if (idx+240 in df.index) else np.nan #'nop'


f = open("./log", 'w')

def log(txt):
    print(txt)
    print(txt, file=f)

def get_code_from_file(fname):
    code_list = []
    with open(fname,'r') as f:
        for line in f:
            code = line.rstrip()
            code = re.sub('.[SHZ]{2}', "", code)
            code_list.append(code)
    return code_list

def get_code_from_dir(fpath):
    files = os.listdir(fpath)
    files = list(map(lambda s: re.sub('.csv', "", s), files))
    return files

'''
    return n random code from list_all
'''
def get_randlist(n):
    s = []
    #list_all = get_code_from_file('./histdata/list_all')
    list_all = get_code_from_dir(RAWSTOCK_PATH)
    index = np.arange(len(list_all))
    np.random.shuffle(index)
    for i in index:
        s.append(list_all[i])
        if len(s) >= int(n):
            break
    return s

'''
    return random period of a df, if df.size < n, then shift head
'''
def rand_df(df, n):
    temp_df = df.copy()
    lenth = len(df)
    if lenth <= n:
        st = np.random.randint(1, 10)
        temp_df = df.tail(lenth-st)
    else:
        end = np.random.randint(n,lenth)
        temp_df = df.loc[df.index[end-n]:df.index[end],:]
    #temp_df.loc[:,'idx'] = range(len(temp_df))
    temp_df.idx = range(len(temp_df))
    #temp_df.reset_index(inplace=True,drop=True)
    return temp_df

def remove_consective_stat(df, gap=15):
    temp_df = df.head(1)
    for i, row in df.iterrows():
        if (row['code'] == temp_df.iloc[-1]['code']): # if it's same code, need remove
            if ((row['code_idx'] - temp_df.iloc[-1]['code_idx']) > gap):
                temp_df = temp_df.append(row, ignore_index=True)
        else:
            temp_df = temp_df.append(row, ignore_index=True)
    return temp_df

def select_df(df, date, lenth):
    temp_idx = df[df.trade_date == date].index.to_list()
    print(temp_idx)
    if len(temp_idx) > 1: 
        raise ValueError("Func.select_df, the selected date > 1")
    idx = temp_idx[0]
    return df.loc[idx-lenth+1:idx,:]

def get_gold(gc, gd, gl):
    print("Func.get_gold: gc = {}, gd = {}, gl = {}".format(gc, gd, gl))
    df = get_hist(gc)
    df = select_df(df, gd, gl)
    return df

def get_code(c):
    s = []
    if re.match('\d{6}', c):
        s = [c]
    elif re.match('rand\d+', c):
        n = re.sub('rand', "", c)
        s = get_randlist(n)
    elif re.match('randall', c):
        s = get_code_from_dir(RAWSTOCK_PATH)
    else:
        code_list = get_code_from_file(c)
        s = code_list
    return s

def get_dirs(path):
    s = []
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path+f):
            s.append(path+f)
    if len(s) == 0:
        s.append(path)
    return s

def get_files(path):
    s = []
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path+f):
            s = s + get_files(path+f+'/')
        else:
            if re.match('\d{6}', f):
                s.append(path+f)
    return s

def chomp_code(code):
    return re.sub('.[SHZ]{2}', "", code)

def chomp_date(date):
    return date.strftime("%Y%m%d")

'''
    Return df which no consective date
'''
def scatter_df(df, gap=15):
    temp_df = df.head(1)
    for i, row in df.iterrows():
        #print("i = {}, index[-1] = {}".format(i, temp_df.iloc[-1]['idx']))
        if ((row['idx'] - temp_df.iloc[-1]['idx']) > gap):
            temp_df = temp_df.append(row, ignore_index=True)
    return temp_df

def get_calendar(st = 'null', ed = 'null'):
    df = pd.read_csv('./histdata/calendar.csv')
    df['cal_date'] = pd.to_datetime(df['cal_date'], format='%Y%m%d')
    if (st != 'null') & (ed != 'null'):
        df = df[(df.cal_date >= st) & (df.cal_date <= ed)]
    return df

def today_date():
    today = datetime.date.today() 
    today = today.strftime('%Y%m%d')
    return today

def tommorow_date():
    date = datetime.date.today()+datetime.timedelta(days=1)
    date = date.strftime('%Y%m%d')
    return date

def rand_calendar(n, op = 'rand'):
    cdf = pd.read_csv('./histdata/calendar.csv')
    if op == 'rand':
        st_idx = np.random.randint(0, len(cdf)-n)
    elif op == 'last':
        st_idx = len(cdf)-n
    st = cdf.iloc[st_idx]['cal_date']
    ed = cdf.iloc[st_idx+n-1]['cal_date']
    print("Start_date = {}, End_date = {}".format(st, ed))
    return str(st),str(ed)

def check_daily(cal):
    error = 0
    for date in cal.cal_date:
        date = chomp_date(date)
        fname = DAILY_PATH+date+'.csv'

        if not os.path.exists(fname):
            error =1
            print("No file: {}".format(fname))
    if error:
        exit()

def get_rand_stocks(num, lenth = -1):
    dfs = {}
    codes = get_randlist(num)
    for c in codes:
        df = get_stock(c, lenth)
        dfs[c] = df
    return dfs

def get_stocks(last_date, number):

    dfs = {}
    fpath = RAWSTOCK_PATH

    files = os.listdir(fpath)
    files = list(map(lambda s: re.sub('.csv', "", s), files))

    for f in files:
        #print("Get Stocks: {}".format(f))
        df = get_stock(f, number)
        dfs[f] = df

    return dfs

#
#    cal = get_calendar()
#
#    idx = cal[cal.cal_date == last_date].index.to_list()[0]
#    cal = cal.iloc[idx-number+1:idx+1]
#
#    check_daily(cal)
#
#    cal = cal.sort_index(ascending=False)
#
#    for date in cal.cal_date:
#
#        date = chomp_date(date)
#        fname = DAILY_PATH+date+'.csv'
#        df = pd.read_csv(fname)
#        print("Read csv file {}".format(fname))
#        df.set_index(['ts_code'], inplace=True)
#
#        for i, row in df.iterrows():
#
#            if not i in dfs:
#                dfs[i] = pd.DataFrame()
#
#            dfs[i] = dfs[i].append(row, ignore_index=True)
#            dfs[i].loc[dfs[i].index[-1], 'ts_code'] = i
#            dfs[i].loc[dfs[i].index[-1], 'trade_date'] = date
#        
#    for c, df in dfs.items():
#        #if len(df) < number:
#        #    print("Warning: skip {}: lenth is {}".format(c, len(df)))
#        #    del dfs[c]
#        #    break
#
#        dfs[c] = hist_fuquan(dfs[c])
#        dfs[c] = hist_reorder(dfs[c])
#        dfs[c] = hist_process(dfs[c])
#        dfs[c].set_index(['trade_date'], inplace=True)
#        dfs[c]['idx'] = range(0, len(dfs[c]))
#
#        dfs[c].to_csv(fpath+c+'.csv',columns=dfs[c].columns,index=True)
#
#        #print(c)
#        #print(dfs[c])
#        #dd = get_hist('000001')
#        #print(dd.tail(3))
#
#    return dfs

def read_daily(date):
    fname = DAILY_PATH+date+'.csv'
    df = pd.read_csv(fname)
    print("Read csv file {}".format(fname))
    df = df.drop(columns=['Unnamed: 0'])
    df.set_index(['ts_code'], inplace=True)
    return df

"""
Extract daily by date
"""
def extract_daily(date, dfs):
    fname = DAILY_PATH+date+'.csv'
    df = pd.read_csv(fname)
    print("Read csv file {}".format(fname))
    df = df.drop(columns=['Unnamed: 0'])
    df.set_index(['ts_code'], inplace=True)
    for i, row in df.iterrows():
        if not i in dfs:
            dfs[i] = pd.DataFrame()

        dfs[i] = dfs[i].append(row, ignore_index=True)
        dfs[i].loc[dfs[i].index[-1], 'ts_code'] = i
        dfs[i].loc[dfs[i].index[-1], 'trade_date'] = date

    return dfs

"""
Publish raw daily, depends on calendar.
"""
def publish_daily_by_calendar():
    dfs = {}

    cal = get_calendar()
    #cal = cal.sort_index(ascending=False)

    check_daily(cal)

    for date in cal.cal_date:
        date = chomp_date(date)
        dfs  = extract_daily(date, dfs)

    for c in dfs.keys():
        code = chomp_code(c)
        dfs[c].to_csv(RAWSTOCK_PATH+code+'.csv',columns=dfs[c].columns,index=False)

    print("Publish daily successful! Total {} stocks.".format(len(dfs)))

def append_daily(dates):
    dfs = {}
    for date in dates:
        dfs = extract_daily(date, dfs)

    for c in dfs.keys():
        fname = RAWSTOCK_PATH+c+'.csv'
        if not os.path.exists(fname):
            df = dfs[c]
        else:
            df = pd.read_csv(fname)
            df = df.append(dfs[c], ignore_index=True)
        print("Append daily for {}".format(c))
        df.to_csv(RAWSTOCK_PATH+c+'.csv',columns=df.columns,index=False)

def get_period_list(start, end, dist):
    l = []
    #number = math.ceil((end-start)/dist)
    print("start = {}, end = {}, dist = {}".format(start, end, dist))
    i = 0
    while(1):
        v = round(start+dist*i, 2)
        l.append(v)
        if v >= end:
            break
        i += 1
    print(l)
    return l

def get_concept():
    ldf = pd.read_csv(CONCEPT_PATH+'list'+'.csv')
    cdfs = {}
    c2s  = {}
    for ts in ldf.code.values:
        df = pd.read_csv(CONCEPT_PATH+ts+'.csv')
        for i, row in df.iterrows():
            code = row['ts_code']
            if code in cdfs.keys():
                cdfs[code]['cl'].append(row['concept_name'])
                cdfs[code]['cid'].append(row['id'])
            else:
                cdfs[code] = {'name': row['name'], 'cl':[row['concept_name']], 'cid':[row['id']]}

            if ts in c2s.keys():
                c2s[ts]['ts_names'].append(row['name'])
                c2s[ts]['ts_codes'].append(row['ts_code'])
            else:
                c2s[ts] = {'name': row['concept_name'], 'ts_names':[row['name']], 'ts_codes':[row['ts_code']]}
    #print(cdfs)
    return cdfs,c2s
