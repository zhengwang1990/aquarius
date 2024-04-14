import os

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def mock_pandas(mocker):
    mocker.patch.object(pd.DataFrame, 'to_pickle')


@pytest.fixture(autouse=True)
def mock_matplotlib(mocker):
    mocker.patch.object(plt, 'savefig')
    mocker.patch.object(plt, 'tight_layout')
    mocker.patch.object(fm.FontManager, 'addfont')
    mocker.patch.object(fm.FontManager, 'findfont')


@pytest.fixture(autouse=True)
def mock_os(mocker):
    mocker.patch('builtins.open', mocker.mock_open(read_data='data'))
    mocker.patch.object(os.path, 'isfile', return_value=False)
    mocker.patch.object(os, 'makedirs')
