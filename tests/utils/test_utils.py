import datetime

import pandas as pd
import pytest
from alpharius.utils import get_latest_day, compute_drawdown, compute_bernoulli_ci95, hash_str


def test_get_latest_day_returns_previous_day(mocker):
    mocker.patch.object(pd, 'to_datetime',
                        return_value=pd.to_datetime('2022-11-13 06:00:00+0'))

    latest_day = get_latest_day()

    assert latest_day == datetime.date(2022, 11, 12)


def test_compute_drawdown():
    values = [1, 2, 3, 4, 5, 2, 2, 1, 1, 3, 6]

    d, hi, li = compute_drawdown(values)

    assert abs(d + 0.8) < 1E-7
    assert hi == 4
    assert li == 8


def test_compute_bernoulli_ci95():
    assert compute_bernoulli_ci95(0, 1) == 0
    assert compute_bernoulli_ci95(1, 1) == 0
    assert compute_bernoulli_ci95(0.5, 10) == pytest.approx(0.3099, rel=1E-3)


def test_hash_str():
    s = '123' * 100
    h = hash_str(s)
    assert len(h) == 10
