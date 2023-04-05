MM Tester
=========

This repository contains a very crude (hacked) market making backtester with a sample AS strategy that I later intend to calibrate using RL.

The sample strategy tries to build a target inventory of 100% long perpetual swap and 100% short weekly future on Deribit exchange.

Preliminary results with fixed parameters (without calibration) using tardis.dev data are promising.

Assumptions:

1. Orders are filled with ask < buy order price or bid > sell order price
2. 500 millisecond network latency to receive market data.
3. 500 millisecond network latency to submit orders/cancel orders.
4. Negative maker fee of 1 bps on weekly futures on Deribit.

Results
=======
Instrument: ETH perpetual swap

backtest days: 4.0000

Ending balance: 2.17

Sharpe ratio: 15.1

Sortino ratio: 21.4

Total return: 7.92 %

Total fees: 0.0000

Max. draw down: 2.35 %

The number of trades per 15min: 16.60

Avg. 15 minutes trading volume: 0.6039

Max leverage: 1.74

Median leverage: 0.87

.. image:: https://github.com/satyapravin/mm_tester/blob/master/perp.png


Instrument: ETH weekly future

backtest days: 4.0000

Ending balance: 2.20

Sharpe ratio: 15.8

Sortino ratio: 20.0

Total return: 11.20 %

Total fees: -0.0209

Max. draw down: 3.59 %

The number of trades per 15min: 16.54

Avg. 15 minutes trading volume: 0.6016

Max leverage: 2.21

Median leverage: 1.10


.. image:: https://github.com/satyapravin/mm_tester/blob/master/future.png
