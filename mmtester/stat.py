from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from typing import List
from datetime import datetime
from . import base_instrument

class Stat:
    def __init__(self, instrument: base_instrument.BaseInstrument, unit='ms'):
        self.intrument: base_instrument.BaseInstrument = instrument
        self.unit: str = unit
        self.timestamp: List(pd.DatetimeIndex) = []
        self.mid: List(float) = []
        self.balance: List(float) = []
        self.position: List(float) = []
        self.avg_price: List(float) = []
        self.fee: List(float) = []
        self.trade_num: List(int) = []
        self.trade_qty: List(float) = []


    def record(self, timestamp: pd.DatetimeIndex, mid: float, balance: float, position: float, 
               avg_price: float, fee: float, trade_num: int, trade_qty: float) -> None:
        self.timestamp.append(timestamp)
        self.mid.append(mid)
        self.balance.append(balance)
        self.position.append(position)
        self.avg_price.append(avg_price)
        self.fee.append(fee)
        self.trade_num.append(trade_num)
        self.trade_qty.append(trade_qty)


    def datetime(self) -> datetime:
        return pd.to_datetime(np.asarray(self.timestamp), unit=self.unit)


    def equity(self, resample: str=None, include_fee: bool=True) -> float:
        if include_fee:
            equity = pd.Series(
                self.instrument.equity(
                    np.asarray(self.mid),
                    np.asarray(self.balance),
                    np.asarray(self.position),
                    np.asarray(self.avg_price),
                    np.asarray(self.fee)
                ),
                index=self.datetime()
            )
        else:
            equity = pd.Series(
                self.instrument.equity(
                    np.asarray(self.mid),
                    np.asarray(self.balance),
                    np.asarray(self.position),
                    np.asarray(self.avg_price),
                    0
                ),
                index=self.datetime()
            )
        if resample is None:
            return equity
        else:
            return equity.resample(resample).last()


    def sharpe(self, resample: str, include_fee: bool=True, trading_days=365) -> float:
        pnl = self.equity(resample, include_fee=include_fee).diff().dropna()
        c = (24 * 3600) / (pnl.index[1] - pnl.index[0]).total_seconds
        return pnl.mean() / pnl.std() * np.sqrt(c * trading_days)


    def sortino(self, resample: str, include_fee: bool=True, trading_days=365) -> float:
        pnl = self.equity(resample, include_fee=include_fee).diff().dropna()
        std = pnl[pnl < 0].std()
        c = (24 * 3600) / (pnl.index[1] - pnl.index[0]).total_seconds
        return pnl.mean() / std * np.sqrt(c * trading_days)


    def riskreturnratio(self, include_fee=True) -> float:
        return self.annualised_return(include_fee=include_fee) / self.maxdrawdown(include_fee=include_fee)


    def drawdown(self, resample: str=None, include_fee=True) -> float:
        equity = self.equity(resample, include_fee=include_fee)
        max_equity = equity.cummax()
        drawdown = equity - max_equity
        return drawdown


    def maxdrawdown(self, denom: float=None, include_fee=True) -> float:
        mdd = -self.drawdown(None, include_fee=include_fee).min()
        if denom is None:
            return mdd
        else:
            return mdd / denom


    def trade_num_frequency(self, interval: str) -> float:
        return pd.Series(self.trade_num, index=self.datetime()).diff().rolling(interval).sum().mean()


    def trade_volume_frequency(self, interval: str) -> float:
        return pd.Series(self.trade_qty, index=self.datetime()).diff().rolling(interval).sum().mean()


    def annualised_return(self, denom: float=None, include_fee=True, trading_days=365):
        equity = self.equity(None, include_fee=include_fee)
        c = (24 * 3600) / (equity.index[-1] - equity.index[0]).total_seconds
        if denom is None:
            return equity[-1] * c * trading_days
        else:
            return equity[-1] * c * trading_days / denom
        

    def summary(self, resample='5min', trading_days=365):
        dt_index = self.datetime()
        raw_equity = self.instrument.equity(
            np.asarray(self.mid),
            np.asarray(self.balance),
            np.asarray(self.position),
            np.asarray(self.avg_price),
            np.asarray(self.fee)
        )
        raw_equity_wo_fee = self.instrument.equity(
            np.asarray(self.mid),
            np.asarray(self.balance),
            np.asarray(self.position),
            np.asarray(self.avg_price),
            0
        )
        equity = pd.Series(raw_equity, index=dt_index)
        rs_equity_wo_fee = pd.Series(raw_equity_wo_fee, index=dt_index).resample(resample).last()
        rs_equity = equity.resample(resample).last()
        rs_pnl = rs_equity.diff().dropna()

        c = (24 * 3600) / (rs_pnl.index[1] - rs_pnl.index[0]).total_seconds
        sr = rs_pnl.mean() / rs_pnl.std() * np.sqrt(c * trading_days)

        std = rs_pnl[rs_pnl < 0].std()
        sortino = rs_pnl.mean() / std * np.sqrt(c * trading_days)

        max_equity = rs_equity.cummax()
        drawdown = rs_equity - max_equity
        mdd = -drawdown.min()

        ac = (24 * 3600) / (equity.index[-1] - equity.index[0]).value
        ar = raw_equity[-1] * ac * trading_days
        rrr = ar / mdd

        ftn = pd.Series(self.trade_num, index=dt_index).diff().rolling('15Min').sum().mean()
        ftq = pd.Series(self.trade_qty, index=dt_index).diff().rolling('15Min').sum().mean()

        capital = self.balance[0]
        
        print('=========== Summary ===========')
        print('Sharpe ratio: %.1f' % sr)
        print('Sortino ratio: %.1f' % sortino)
        print('Risk return ratio: %.1f' % rrr)
        print('Annualised return: %.2f %%' % (ar / capital * 100))
        print('Max. draw down: %.2f %%' % (mdd / capital * 100))
        print('The number of trades per 15min: %d' % ftn)
        print('Avg. 15 minutes trading volume: %d' % ftq)


        position = np.asarray(self.position) * np.asarray(self.mid)
        print('Max leverage: %.2f' % (np.max(np.abs(position)) / capital))
        print('Median leverage: %.2f' % (np.median(np.abs(position)) / capital))

        fig, axs = plt.subplots(2, 1, sharex=True)
        fig.subplots_adjust(hspace=0)
        fig.set_size_inches(10, 6)

        mid = pd.Series(self.mid, index=dt_index)

        ((mid / mid[0] - 1).resample(resample).last() * 100).plot(ax=axs[0], style='grey', alpha=0.5)
        (rs_equity / capital * 100).plot(ax=axs[0])
        (rs_equity_wo_fee / capital * 100).plot(ax=axs[0])

        # axs[0].set_title('Equity')
        axs[0].set_ylabel('Cumulative Returns (%)')
        axs[0].grid()
        axs[0].legend(['Trading asset', 'Strategy incl. fee', 'Strategy excl. fee'])

        # todo: this can mislead a user due to aggregation.
        position = pd.Series(self.position, index=dt_index).resample(resample).last()
        position.plot(ax=axs[1])
        axs[1].set_ylabel('Position (Qty)')
        axs[1].grid()
