# Alpharius

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/zhengwang1990/alpharius/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/zhengwang1990/alpharius/tree/main)
[![codecov](https://codecov.io/gh/zhengwang1990/alpharius/branch/main/graph/badge.svg?token=R8RUFJJ1CV)](https://codecov.io/gh/zhengwang1990/alpharius)

## Install

```shell
$ make
```

## Run

### Run tests
```shell
$ python -m unittest discover
```

### Run backtesting
```shell
$ python alpharius/trade.py --mode backtest --start_date 2017-01-01 --end_date 2022-06-01
```

## Run realtime trading
```shell
$ python alpharius/trade.py --mode trade
```