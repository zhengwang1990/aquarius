import bs4
import requests
import textwrap


WIKI_PAGE = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'


def main():
    response = requests.get(WIKI_PAGE)

    symbols = []
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    constituents = soup.find('table', {'id': 'constituents'})
    constituent_trs = constituents.find_all('tr')
    for tr in constituent_trs:
        td = tr.find('td')
        if not td:
            continue
        symbols.append("'" + td.get_text().strip() + "'")
    sp500_line = ', '.join(symbols)
    lines = textwrap.wrap(sp500_line, width=80)
    sp500 = '\n'.join(['    ' + line for line in lines])
    print('SP500_SYMBOLS = [')
    print(sp500)
    print(']')

    print('\n')
    print('def get_sp500(view_time):')
    print('    sp500_set = set(SP500_SYMBOLS)')
    print('    view_date = pd.Timestamp(view_time.date())')
    changes = soup.find('table', {'id': 'changes'})
    change_trs = changes.find_all('tr')
    date_col = 0
    added_col = 1
    removed_col = 3
    for tr in change_trs:
        td = tr.find_all('td')
        if not td:
            continue
        date = td[date_col].get_text().strip()
        added = td[added_col].get_text().strip()
        removed = td[removed_col].get_text().strip()
        print(f"    if view_date < pd.to_datetime('{date}'):")
        if added:
            print(f"        sp500_set.discard('{added}')")
        if removed:
            print(f"        sp500_set.add('{removed}')")
    print('    return list(sp500_set)')


if __name__ == '__main__':
    main()
