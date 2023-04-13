from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from typing import List
from datetime import datetime
from mmtester import base_instrument

class Stat:
    def __init__(self, length: int, instrument: base_instrument.BaseInstrument, unit='ms'):
        self.instrument: base_instrument.BaseInstrument = instrument
        self.unit: str = unit
        self.length = length
        self.timestamp: List[pd.DatetimeIndex] = [None] * length
        self.mid: List[float] = [None] * length
        self.balance: List[float] = [None] * length
        self.position: List[float] = [None] * length
        self.avg_price: List[float] = [None] * length
        self.fee: List[float] = [None] * length
        self.trade_num: List[int] = [None] * length
        self.trade_qty: List[float] = [None] * length
        self.curr_record = 0


    def record(self, timestamp: pd.DatetimeIndex, mid: float, balance: float, position: float, 
               avg_price: float, fee: float, trade_num: int, trade_qty: float) -> None:
        self.timestamp[self.curr_record] = timestamp
        self.mid[self.curr_record] = mid
        self.balance[self.curr_record] = balance
        self.position[self.curr_record] = position
        self.avg_price[self.curr_record] = avg_price
        self.fee[self.curr_record] = fee
        self.trade_num[self.curr_record] = trade_num
        self.trade_qty[self.curr_record] = trade_qty
        self.curr_record += 1

    def close(self):
        self.timestamp = self.timestamp[:self.curr_record]
        self.mid = self.mid[:self.curr_record]
        self.balance = self.balance[:self.curr_record]
        self.position = self.position[:self.curr_record]
        self.avg_price = self.avg_price[:self.curr_record]
        self.fee = self.fee[:self.curr_record]
        self.trade_num = self.trade_num[:self.curr_record]
        self.trade_qty = self.trade_qty[:self.curr_record]

    def datetime(self) -> datetime:
        return np.asarray(self.timestamp)


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
        c = (24 * 3600) / (pnl.index[1] - pnl.index[0]).total_seconds()
        return pnl.mean() / pnl.std() * np.sqrt(c * trading_days)


    def sortino(self, resample: str, include_fee: bool=True, trading_days=365) -> float:
        pnl = self.equity(resample, include_fee=include_fee).diff().dropna()
        std = pnl[pnl < 0].std()
        c = (24 * 3600) / (pnl.index[1] - pnl.index[0]).total_seconds()
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
        c = (24 * 3600) / (equity.index[-1] - equity.index[0]).total_seconds()
        if denom is None:
            return equity[-1] * c * trading_days
        else:
            return equity[-1] * c * trading_days / denom
        
    
    def summary(self, filename, resample='5min', trading_days=365):
        self.close()
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

        c = (24 * 3600) / (rs_pnl.index[1] - rs_pnl.index[0]).total_seconds()
        sr = rs_pnl.mean() / rs_pnl.std() * np.sqrt(c * trading_days)

        std = rs_pnl[rs_pnl < 0].std()
        sortino = rs_pnl.mean() / std * np.sqrt(c * trading_days)

        max_equity = rs_equity.cummax()
        drawdown = rs_equity - max_equity
        mdd = -drawdown.min()

        ar = (raw_equity[-1] - raw_equity[0])
        ftn = pd.Series(self.trade_num, index=dt_index).diff().rolling('15Min').sum().mean()
        ftq = pd.Series(self.trade_qty, index=dt_index).diff().rolling('15Min').sum().mean()

        capital = self.balance[0]
        backtest_days = (self.timestamp[-1] - self.timestamp[0]).total_seconds() / (24 * 3600)
        '''print('=========== Summary ===========')
        print('backtest days: %.4f' % backtest_days)
        print('Ending balance: %.2f' % self.balance[-1])
        print('Sharpe ratio: %.1f' % sr)
        print('Sortino ratio: %.1f' % sortino)
        print('Hourly return: %.2f %%' % (ar / capital * 100))
        print('Total fees: %.4f' % (np.sum(np.diff(self.fee))))
        print('Max. draw down: %.2f %%' % (mdd / capital * 100))
        print('The number of trades per 15min: %.2f' % ftn)
        print('Avg. 15 minutes trading volume: %.4f' % ftq)'''


        '''position = np.asarray(self.position)
        #print('Max leverage: %.2f' % (np.max(np.abs(position)) / capital))
        #print('Median leverage: %.2f' % (np.median(np.abs(position)) / capital))

        
        fig, axs = plt.subplots(2, 1, sharex=True)
        fig.subplots_adjust(hspace=0)
        fig.set_size_inches(10, 6)

        mid = pd.Series(self.mid, index=dt_index)

        ((mid / mid[0] - 1).resample(resample).last() * 100).plot(ax=axs[0], style='grey', alpha=0.5)
        ((rs_equity / capital - 1.0) * 100).plot(ax=axs[0])
        ((rs_equity_wo_fee / capital - 1.0) * 100).plot(ax=axs[0])

        # axs[0].set_title('Equity')
        axs[0].set_ylabel('Cumulative Returns (%)')
        axs[0].grid()
        axs[0].legend(['Trading asset', 'Strategy incl. fee', 'Strategy excl. fee'])

        # todo: this can mislead a user due to aggregation.
        position = pd.Series(self.position, index=dt_index).resample(resample).last()
        position.plot(ax=axs[1])
        axs[1].set_ylabel('Position (Qty)')
        axs[1].grid()
        fig.savefig(filename + ".png")'''
        return backtest_days, self.balance[-1], sr, sortino, (ar/capital*100), np.sum(np.diff(self.fee)), mdd/capital * 100, ftn, ftq
