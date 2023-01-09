# Alpharius

[![Unit Test](https://github.com/zhengwang1990/alpharius/actions/workflows/unittest.yml/badge.svg)](https://github.com/zhengwang1990/alpharius/actions/workflows/unittest.yml)
[![codecov](https://codecov.io/gh/zhengwang1990/alpharius/branch/main/graph/badge.svg?token=R8RUFJJ1CV)](https://codecov.io/gh/zhengwang1990/alpharius)

## Install

```shell
$ make
```

## Trade

### Run tests
```shell
$ pytest
```

### Run backtesting
```shell
$ python alpharius/trade.py --mode backtest --start_date 2017-01-01 --end_date 2022-06-01
```

### Run realtime trading
```shell
$ python alpharius/trade.py --mode trade
```

## Web

### Local web service
```shell
flask --app alpharius.web --debug run
```
