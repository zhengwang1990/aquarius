import bs4
import requests
import textwrap


WIKI_PAGE = 'https://en.wikipedia.org/wiki/Nasdaq-100'


def main():
    response = requests.get(WIKI_PAGE)

    symbols = []
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    constituents = soup.find('table', {'id': 'constituents'})
    constituent_trs = constituents.find_all('tr')
    for tr in constituent_trs:
        tds = tr.find_all('td')
        if not tds:
            continue
        symbols.append("'" + tds[1].get_text().strip() + "'")
    nasdaq100_line = ', '.join(symbols)
    lines = textwrap.wrap(nasdaq100_line, width=80)
    nasdaq100 = '\n'.join(['    ' + line for line in lines])
    print('NASDAQ100_SYMBOLS = [')
    print(nasdaq100)
    print(']')


if __name__ == '__main__':
    main()

