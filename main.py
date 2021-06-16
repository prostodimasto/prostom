import requests
import xml.etree.ElementTree as ET
from settings import row, TOKEN_BOT, user_id, from_limit
from bs4 import BeautifulSoup
import telebot

ft_dict = {}
ht_dict = {}

bot = telebot.TeleBot(TOKEN_BOT)


def get_match_id():
    match_ids = []
    req = requests.get('https://www.nowgoal3.com/gf/data/odds/en/ch_goal8.xml',
                       headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})

    with open('score.xml', 'w') as file:
        file.write(req.text)
    try:
        items = ET.parse('score.xml').getroot().find('match').findall('m')
    except :
        return False
    for item in items:
        match_ids.append(int(item.text.split(',')[0]))

    return match_ids


def parse():
    while True:
        match_ids = get_match_id()
        if match_ids:
            break

    ft_copy = ft_dict.copy()
    for item in ft_copy:
        if not (item in match_ids):
            del ft_dict[item]

    ht_copy = ht_dict.copy()
    for item in ht_copy:
        if not (item in match_ids):
            del ht_dict[item]

    for match_id in match_ids:
        # ------------------------ FT --------------------
        req_1 = requests.get(f'https://data.nowgoal3.com/Ajax.aspx?type=36&ID={match_id}&cid=31&aoh=1',
                             headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})
        items = req_1.json()['totalscore'][:row]
        if match_id in ft_dict.keys():
            for i in ft_dict[match_id]:
                for item in items:
                    if i == item['modifytime']:
                        if item["goal"] == ft_dict[match_id][i][1] and ft_dict[match_id][i][0] - item['upodds'] > from_limit:
                            req = requests.get(f'http://data.nowgoal3.com/3in1odds/31_{match_id}.html',
                                               headers={
                                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})

                            soup = BeautifulSoup(req.text, 'lxml')
                            name_team = soup.find(id='headVs').find_all(class_='sclassName')
                            send_messages(
                                f'FT\n{name_team[0].text.strip()} - {name_team[1].text.strip()}\nDrop Over Odds {item["goal"]}: {ft_dict[match_id][i][0]} --> {item["upodds"]}')
        if items:
            ft_dict[match_id] = dict()
        for item in items:
            ft_dict[match_id][item['modifytime']] = [item['upodds'], item["goal"]]

        # ------------------------ HT --------------------
        req_2 = requests.get(f'https://data.nowgoal3.com/Ajax.aspx?type=36&ID={match_id}&cid=31&aoh=2',
                             headers={
                                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})
        items = req_2.json()['totalscore'][:row]
        if match_id in ht_dict.keys():
            for i in ht_dict[match_id]:
                for item in items:
                    if i == item['modifytime']:
                        if item["goal"] == ht_dict[match_id][i][1] and ht_dict[match_id][i][0] - item['upodds'] > from_limit:
                            req = requests.get(f'http://data.nowgoal3.com/3in1odds/31_{match_id}_2.html',
                                               headers={
                                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})

                            soup = BeautifulSoup(req.text, 'lxml')
                            name_team = soup.find(id='headVs').find_all(class_='sclassName')
                            send_messages(
                                f'HT\n{name_team[0].text.strip()} - {name_team[1].text.strip()}\nDrop Over Odds {item["goal"]}: {ht_dict[match_id][i][0]} --> {item["upodds"]}')
        if items:
            ht_dict[match_id] = dict()
        for item in items:
            ht_dict[match_id][item['modifytime']] = [item['upodds'], item["goal"]]


def send_messages(text):
    bot.send_message(chat_id=user_id, text=text)


if __name__ == '__main__':
    while True:
        parse()
