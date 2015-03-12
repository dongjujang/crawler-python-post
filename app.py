

#-*- coding: utf-8 -*-   
import time
import os
import requests
import BeautifulSoup
import pymongo

TORRENT_URLS = os.environ.get('TORRENT_URL', None)
SLEEP_TIME = os.environ.get('SLEEP_TIME', 60 * 10)
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
host = 'http://www.torrentbest.net'

keys = ['subject',
        'id_num',
        'magnet',
        'size',
        'number']
docs = []
doc = {}

def post_webhook(doc, url):
  if not WEBHOOK_URL:
    return
  split_url = url.split('torrent_');
  collection_name = split_url[1];
  requests.post(WEBHOOK_URL + '/' + collection_name, data=doc)

def get_torrent(post_url):
  session = requests.Session()
  headers = { 'User-Agent': USER_AGENT, 'referer': post_url }
  response = session.get(post_url, headers=headers)
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

def get_posts(url_with_page, torrent_url):
  session = requests.Session()
  headers = { 'User-Agent': USER_AGENT, 'referer': url_with_page }
  response = session.get(url_with_page, headers=headers)
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

    if doc:
      post_webhook(doc, torrent_url)    
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
        get_posts(TORRENT_URL + '&page=' + str(num), TORRENT_URL)
        num = num - 1
    time.sleep(SLEEP_TIME)

if __name__ == '__main__':
    main()
