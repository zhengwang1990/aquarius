from .common import *
from .data import HistoricalDataLoader
import alpaca_trade_api as tradeapi
import datetime
import email.mime.image as image
import email.mime.multipart as multipart
import email.mime.text as text
import io
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pandas_market_calendars as mcal
import smtplib

_SMTP_HOST = 'smtp.163.com'
_SMTP_PORT = 25


def send_email():
    username = os.environ.get('EMAIL_USERNAME')
    password = os.environ.get('EMAIL_PASSWORD')
    receiver = os.environ.get('EMAIL_RECEIVER')
    if not username or not password or not receiver:
        return
    email_client = Email(username, password)
    sender = f'Stock Trading System <{username}@163.com>'
    receiver = receiver
    email_client.send_email(sender, receiver)


class Email:
    def __init__(self, username: str, password: str):
        self._alpaca = tradeapi.REST()
        self._data_loader = HistoricalDataLoader(TimeInterval.DAY, DataSource.POLYGON)
        self._client = self._create_client(username, password)

    @staticmethod
    def _create_client(username: str, password: str) -> smtplib.SMTP:
        client = smtplib.SMTP(_SMTP_HOST, _SMTP_PORT)
        client.starttls()
        client.ehlo()
        client.login(username, password)
        return client

    @staticmethod
    def _create_message(sender, receiver):
        message = multipart.MIMEMultipart('alternative')
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = f'[Summary] [{datetime.datetime.today().strftime("%F")}] Trade summary of the day'
        return message

    @staticmethod
    def _get_color_style(value: float):
        return 'style="color:{};"'.format('green' if value >= 0 else 'red')

    def send_email(self, sender: str, receiver: str):
        message = self._create_message(sender, receiver)
        today = datetime.datetime.today()
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=today - datetime.timedelta(days=40),
                                 end_date=today)
        market_dates = mcal.date_range(schedule, frequency='1D')
        orders = self._alpaca.list_orders(status='closed', after=market_dates[-1].strftime('%F'),
                                          direction='desc')
        orders_html = ''
        for order in orders:
            if order.filled_at is None:
                continue
            filled_at_str = pd.to_datetime(order.filled_at).tz_convert(TIME_ZONE).strftime("%H:%M:%S")
            orders_html += (f'<tr><th scope="row">{order.symbol}</th>'
                            f'<td>{order.side}</td>'
                            f'<td>{order.filled_qty}</td>'
                            f'<td>{order.filled_avg_price}</td>'
                            f'<td>{filled_at_str}</td>'
                            '</tr>\n')
        positions_html = ''
        positions = self._alpaca.list_positions()
        for position in positions:
            change_today = float(position.change_today)
            gain = float(position.unrealized_plpc)
            positions_html += (f'<tr><th scope="row">{position.symbol}</th>'
                               f'<td>{position.qty}</td>'
                               f'<td>{position.avg_entry_price}</td>'
                               f'<td>{position.current_price}</td>'
                               f'<td {self._get_color_style(change_today)}>{change_today * 100:+.2f}%</td>'
                               f'<td {self._get_color_style(gain)}>{gain * 100:+.2f}%</td>'
                               '</td>\n')

        account = self._alpaca.get_account()
        cash_reserve = float(os.environ.get('CASH_RESERVE', 0))
        account_equity = float(account.equity) - cash_reserve
        account_cash = float(account.cash) - cash_reserve
        history_length = 10
        history = self._alpaca.get_portfolio_history(date_start=market_dates[-history_length].strftime('%F'),
                                                     date_end=market_dates[-2].strftime('%F'),
                                                     timeframe='1D')
        for i in range(len(history.equity)):
            history.equity[i] = (history.equity[i] - cash_reserve
                                 if history.equity[i] > cash_reserve else history.equity[i])
        historical_value = [equity / history.equity[0] for equity in history.equity]
        historical_value.append(account_equity / history.equity[0])
        historical_date = [m.date() for m in market_dates[-history_length:]]
        market_symbols = ['DIA', 'SPY', 'QQQ']
        market_values = {}
        for symbol in market_symbols:
            symbol_data = self._data_loader.load_data_list(
                symbol, pd.to_datetime(historical_date[0]),
                pd.to_datetime(historical_date[-1]) + datetime.timedelta(days=1))
            symbol_close = np.array(symbol_data['Close'])
            market_values[symbol] = symbol_close

        intraday_gain = account_equity - history.equity[-1]
        row_style = 'scope="row" class="narrow-col"'
        account_html = (f'<tr><th {row_style}>Equity</th><td>{account_equity:.2f}</td></tr>'
                        f'<tr><th {row_style}>Cash</th><td>{account_cash:.2f}</td></tr>')
        if cash_reserve > 0:
            account_html += f'<tr><th {row_style}>Reserve</th><td>{cash_reserve:.2f}</td></tr>'
        account_html += (f'<tr><th {row_style}>Gain / Loss</th>'
                         f'<td {self._get_color_style(intraday_gain)}>{intraday_gain:+.2f}'
                         f'({(account_equity / history.equity[-1] - 1) * 100:+.2f}%)</td></tr>\n'
                         f'<tr><th {row_style}>Market Change</th>'
                         '<td style="padding: 0px;"><table>')
        for symbol in market_symbols:
            if symbol not in market_values:
                continue
            symbol_value = market_values[symbol]
            symbol_gain = (symbol_value[-1] / symbol_value[-2] - 1) * 100
            account_html += (f'<tr><td style="border: none; padding: 0.5rem;">{symbol}</td>'
                             f'<td style="border: none; padding: 0.5rem;">{symbol_value[-1]:.2f}'
                             f'<span {self._get_color_style(symbol_gain)}>({symbol_gain:+.2f}%)</span>'
                             '</td></tr>')
        account_html += '</table></td></tr>'

        color_map = {'QQQ': '#78d237', 'SPY': '#FF6358', 'DIA': '#aa46be'}
        pd.plotting.register_matplotlib_converters()
        plt.figure(figsize=(10, 4))
        plt.plot(historical_value, marker='o',
                 label=f'My Portfolio ({(historical_value[-1] - 1) * 100:+.2f}%)',
                 color='#28b4c8')
        for symbol in market_symbols:
            if symbol not in market_values:
                continue
            symbol_value = market_values[symbol]
            normalized_value = np.array(symbol_value) / symbol_value[0]
            if len(historical_date) != len(normalized_value):
                continue
            plt.plot(normalized_value, marker='o',
                     label=f'{symbol} ({(normalized_value[-1] - 1) * 100:+.2f}%)',
                     color=color_map[symbol])
        text_kwargs = {'family': 'monospace'}
        plt.xticks(range(len(historical_date)), [date.strftime('%m-%d') for date in historical_date],
                   **text_kwargs)
        plt.xlabel('Date', **text_kwargs)
        plt.ylabel('Normalized Value', **text_kwargs)
        plt.yticks(fontname='monospace')
        plt.grid(linestyle='--', alpha=0.5)
        plt.legend(ncol=len(market_symbols) + 1, bbox_to_anchor=(0, 1),
                   loc='lower left', prop=text_kwargs)
        ax = plt.gca()
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        history_image = image.MIMEImage(buf.read())
        history_image.add_header('Content-Disposition', "attachment; filename=history.png")
        history_image.add_header('Content-ID', '<history>')

        html_template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          'email.html')
        with open(html_template_path, 'r') as f:
            html_template = f.read()
        message.attach(text.MIMEText(html_template.format(
            account_html=account_html, orders_html=orders_html,
            positions_html=positions_html), 'html'))
        message.attach(history_image)
        self._client.sendmail(sender, [receiver], message.as_string())
        self._client.close()
