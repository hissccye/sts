import backtrader as bt

class MyStrategy(bt.Strategy):
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

class TrendStrategy(MyStrategy):
    params = (
        ('emaperiod1', 12),
        ('emaperiod2', 50),
        ('printlog', True),
    )

    def __init__(self):
        self.order = None

        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['ema1'] = bt.indicators.SimpleMovingAverage(d.close, period=self.p.emaperiod1)
            self.inds[d]['ema2'] = bt.indicators.SimpleMovingAverage(d.close, period=self.p.emaperiod2)
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['ema1'],self.inds[d]['ema2'])

    def next(self):
        for i, d in enumerate(self.datas):
            self.log('Code: %s, Close, %.2f' % (d._name, d.close[0]))

        if self.order:
            self.log('return by order exists.')
            return

        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:
                if self.inds[d]['cross'][0] > 0:
                    self.log('BUY CREATE, %.2f' % d.close[0])
                    self.order = self.buy(data=d, exectype=bt.Order.Limit)
            else:
                if self.inds[d]['cross'][0] < 0:
                    self.log('BUY CREATE, %.2f' % d.close[0])
                    self.order = self.sell(data=d)
                elif len(self) == (self.datas[0].buflen()-1):
                    self.order = self.sell(data=d)

    def stop(self):
        for i, d in enumerate(self.datas):
            self.log('(EMA Period1 %2d, EMA Period2 %2d) Ending Value %.2f' %
                     (self.params.emaperiod1, self.params.emaperiod2, self.broker.getvalue()), doprint=True)
