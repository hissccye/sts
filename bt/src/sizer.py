import backtrader as bt
class FullSizer(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        v = 0
        position = self.broker.getposition(data)
        if isbuy:
            v = cash//data.close[0]
            print(v)
        else:
            v = position.size
            print(v)

        return v


