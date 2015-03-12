
#-*- coding: utf-8 -*-   
import time
import os
import requests
import BeautifulSoup
import pymongo

TORRENT_URLS = os.environ.get('TORRENT_URL', None)
SLEEP_TIME = os.environ.get('SLEEP_TIME', 60 * 10)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
host = 'http://www.torrentbest.net'

keys = ['subject',
        'id_num',
        'magnet',
        'size',
        'number']
docs = []
doc = {}

def post_webhook(data):
  if not WEBHOOK_URL:
    return
  split_url = TORRENT_URL.split('torrent_');
  collection_name = split_url[2]
  request.post(WEBHOOK_URL + '/' + collection_name, data=data)

def get_torrent(post_url):
  response = requests.get(post_url)
  soup = BeautifulSoup.BeautifulSoup(response.text)
  elements = soup.findAll('td', attrs={'class': 'view_file'})
  for element in elements:
    if 'magnet:?xt' in element.text:
      uncut_magnet = element.text
      cut_magnet = uncut_magnet.split(';', 1)
      magnet = cut_magnet[1]
      doc[keys[2]] = magnet 
      docs.append(doc.copy())

      print doc
      break

def get_posts(url_with_page):
  response = requests.get(url_with_page)
  soup = BeautifulSoup.BeautifulSoup(response.text)

  elements = soup.find('table', attrs={'id': 'board_list'}).findAll('tr', attrs={'class': 'list_row'})
  for element in elements:
    data_num = element.find('td', attrs={'class': 'num'}).text
    doc[keys[4]] = int(data_num)

    data_size = element.find('td', attrs={'class': 'hit'}).text
    doc[keys[3]] = data_size

    a_element = element.find('a')
    subject = a_element.text
    doc[keys[0]] = subject
    
    uncut_id_num = a_element['href'].split('=', 2)
    id_num = uncut_id_num[2]
    doc[keys[1]] = id_num

    get_torrent(host + a_element['href'][2:])

  if docs:
    post_webhook(docs)
    del docs[:]
  else:
    return

def main():
  if TORRENT_URLS == None:
    print 'notorrenturl'
    return
  while True:
    for TORRENT_URL in TORRENT_URLS.split(','):
      num = 1
      page_num = range(1, num + 1)
      for i in page_num:
        get_posts(TORRENT_URL + '&page=' + str(num))
        num = num - 1
    time.sleep(SLEEP_TIME)

if __name__ == '__main__':
  main()
