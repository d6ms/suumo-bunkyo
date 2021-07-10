from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import DataFrame
import time


# ページ数を取得
def get_n_pages(soup):
    body = soup.find("body")
    pages = body.find_all("div", {'class': 'pagination pagination_set-nav'})
    pages_text = str(pages)
    pages_split = pages_text.split('</a></li>\n</ol>')
    return int(pages_split[0][-3:].replace('>', ''))


def extract(url):
    data = []

    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, 'lxml')
    summary = soup.find("div", {'id': 'js-bukkenList'})

    # マンション名、住所、立地（最寄駅/徒歩~分）、築年数、建物高さが入っているcassetteitemを全て抜き出し
    cassetteitems = summary.find_all("div", {'class': 'cassetteitem'})

    # 各cassetteitemsに対し、以下の動作をループ
    for cassetteitem in cassetteitems:
        try:
            name = None  # マンション名
            address = None  # 住所
            locations0 = None  # 立地1つ目（最寄駅/徒歩~分）
            locations1 = None  # 立地2つ目（最寄駅/徒歩~分）
            locations2 = None  # 立地3つ目（最寄駅/徒歩~分）
            age = None  # 築年数
            height = None  # 建物高さ

            # 各建物から売りに出ている部屋数を取得
            tbodies = cassetteitem.find_all('tbody')

            # マンション名取得
            subtitle = cassetteitem.find_all("div", {
                'class': 'cassetteitem_content-title'})
            subtitle = str(subtitle)
            subtitle_rep = subtitle.replace(
                '[<div class="cassetteitem_content-title">', '')
            subtitle_rep2 = subtitle_rep.replace(
                '</div>]', '')

            # 住所取得
            subaddress = cassetteitem.find_all("li", {
                'class': 'cassetteitem_detail-col1'})
            subaddress = str(subaddress)
            subaddress_rep = subaddress.replace(
                '[<li class="cassetteitem_detail-col1">', '')
            subaddress_rep2 = subaddress_rep.replace(
                '</li>]', '')

            # 部屋数だけ、マンション名と住所を繰り返しリストに格納（部屋情報と数を合致させるため）
            for y in range(len(tbodies)):
                name = subtitle_rep2
                address = subaddress_rep2

            # 立地を取得
            sublocations = cassetteitem.find_all("li", {
                'class': 'cassetteitem_detail-col2'})

            # 立地は、1つ目から3つ目までを取得（4つ目以降は無視）
            for x in sublocations:
                cols = x.find_all('div')
                for i in range(len(cols)):
                    text = cols[i].find(text=True)
                    for y in range(len(tbodies)):
                        if i == 0:
                            locations0 = text
                        elif i == 1:
                            locations1 = text
                        elif i == 2:
                            locations2 = text

            # 築年数と建物高さを取得
            tbodies = cassetteitem.find_all('tbody')
            col3 = cassetteitem.find_all("li", {'class': 'cassetteitem_detail-col3'})
            for x in col3:
                cols = x.find_all('div')
                for i in range(len(cols)):
                    text = cols[i].find(text=True)
                    for y in range(len(tbodies)):
                        if i == 0:
                            age = text
                        else:
                            height = text

            for tr in cassetteitem.find_all("tr", {'class': 'js-cassette_link'}):
                try:
                    floor = None  # 階
                    rent = None  # 賃料
                    admin = None  # 管理費
                    others = None  # 敷/礼/保証/敷引,償却
                    floor_plan = None  # 間取り
                    area = None  # 専有面積
                    for j, td in enumerate(tr.find_all('td')):
                        text = td.text.strip()
                        if j == 2:
                            floor = text
                        elif j == 3:
                            rent = text.split('\n')[0]
                            admin = text.split('\n')[1]
                        elif j == 4:
                            others = text.replace('\n', ',')
                        elif j == 5:
                            floor_plan = text.split('\n')[0]
                            area = text.split('\n')[1]
                    data.append({
                        'name': str(name),  # マンション名
                        'address': str(address),  # 住所
                        'locations0': str(locations0),  # 立地1つ目（最寄駅/徒歩~分）
                        'locations1': str(locations1),  # 立地2つ目（最寄駅/徒歩~分）
                        'locations2': str(locations2),  # 立地3つ目（最寄駅/徒歩~分）
                        'age': str(age),  # 築年数
                        'height': str(height),  # 建物高さ
                        'floor': str(floor),  # 階
                        'rent': str(rent),  # 賃料
                        'admin': str(admin),  # 管理費
                        'others': str(others),  # 敷/礼/保証/敷引,償却
                        'floor_plan': str(floor_plan),  # 間取り
                        'area': str(area)  # 専有面積
                    })
                except:
                    continue
        except:
            continue
    return data


def main():
    url = 'http://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13105&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1'

    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, 'lxml')

    n_pages = get_n_pages(soup)
    print('fetches ' + str(n_pages) + ' pages')
    data = []
    for i in range(1, n_pages + 1):
        try:
            data.extend(extract(url + '&page=' + str(i)))
            print('processed page ' + str(i))
            time.sleep(5)
        except:
            print('error in page ' + str(i))
            continue

    suumo_df = DataFrame(data)
    suumo_df.columns = ['マンション名', '住所', '立地1', '立地2', '立地3', '築年数', '建物高さ', '階', '賃料', '管理費', '敷/礼/保証/敷引,償却', '間取り',
                        '専有面積']
    suumo_df.to_pickle('suumo_bunkyo.pkl')


main()
