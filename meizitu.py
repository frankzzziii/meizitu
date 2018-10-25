import requests
from lxml import etree
from bs4 import BeautifulSoup
import re
import os,sys
from  concurrent.futures import ThreadPoolExecutor,as_completed
import time
from progressbar import *
"""
爬取妹子图 v2
"""
base_url ='http://www.mmjpg.com/'
header ={
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-CN;q=0.6',
	'Host': 'www.mmjpg.com',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
	}
#增加进度条
progress = ProgressBar()
widgets = ['Progress: ',Percentage(), ' ', Bar('#'),' ', Timer(),
           ' ', '', ' ', '']
def get_albumList_links():
	soup = BeautifulSoup(r.text,'lxml')
	pic_links = set([link['href'] for link in soup.find_all('a',href = re.compile('http://www.mmjpg.com/mm/[\d]+'))])
	#print(pic_links)
	return pic_links

def download_album(album_link):
	r = session.get(album_link)
	soup = BeautifulSoup(r.content,"html.parser")
	album_name = soup.h2.string
	pic_num = int ([num.string for num in soup.find_all('a',href = re.compile('/mm/[\d]+/[\d]*'))][-2])
	pic_urls =[album_link +'/{}'.format(num) for num in range(1,pic_num)]
	#根据相册建立目录
	if not os.path.exists('photo/{}'.format(album_name)):
		os.makedirs('photo/{}'.format(album_name))
	widgets[0] = album_name
	pbar = ProgressBar(widgets=widgets, maxval=10*len(pic_urls)).start()
	downlord_img(pic_urls,album_name,pbar)
	pbar.finish()
	return album_name + '[OK]'

def downlord_img(pic_urls,album_name,pbar):
	for i, pic_url in enumerate(pic_urls):
		pbar.update(10 * i + 1)
		r = session.get(pic_url)
		soup = BeautifulSoup(r.content,"html.parser")
		img_url =[ url['src'] for url in soup.find(id ='content').a][0]
		refer = {'Referer':pic_url}
		header.update(refer)
		html= session.get(img_url,headers = header)
		file_path = 'photo/'+ album_name + '/' + img_url.split('/')[-1]
		with open(file_path, 'wb') as file:
			file.write(html.content)
			file.flush()

if __name__ == '__main__':
	session = requests.Session()
	r = session.get(base_url,headers= header)
	album_links = get_albumList_links()
	with ThreadPoolExecutor(max_workers = 5) as executor:
		for result in executor.map(download_album,album_links):
			print(result)

