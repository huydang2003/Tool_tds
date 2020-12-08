import os
import requests
from bs4 import BeautifulSoup
import json
import re

class fb():
	def __init__(self):
		self.ses = requests.session()

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def get_headers_fb(self, cookie_fb):
		headers_fb = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36',
			'cookie': cookie_fb
		}
		return headers_fb

	def get_token_fb(self, cookie_fb):
		headers = self.get_headers_fb(cookie_fb)
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def check_cookie_fb(self, cookie_fb):
		token = self.get_token_fb(cookie_fb)
		if token=='': return False
		else: return True

	def get_save_info(self, token_fb, path_folder):
		params = {'access_token': token_fb}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		if 'error' not in data:
			if not os.path.exists(path_folder): os.mkdir(path_folder)
			path_info = f'{path_folder}/{data["name"]}_{data["id"]}.json'
			self.save_file_json(path_info, data)

	def reaction_post(self, idpost, cookie_fb, reaction):
		dict_reaction = {'LIKE':0, 'LOVE':1, 'THUONGTHUONG':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
		link = f'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id={idpost}&origin_uri=https://mbasic.facebook.com'
		headers = self.get_headers_fb(cookie_fb)
		res = self.ses.get(link, headers=headers)
		link = res.url
		if 'login.php' in link: return 2
		else:
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			list_li = soup.find_all('li')
			if list_li!=[]:	
				vt = dict_reaction[reaction]
				url = list_li[vt].a.get('href')
				link = 'https://mbasic.facebook.com' + url
				self.ses.get(link, headers=headers)
				return 1
			else: return 0

	def follow_id(self, cookie_fb, fb_id):
		url = "https://mbasic.facebook.com/profile.php?id=" + fb_id
		headers = self.get_headers_fb(cookie_fb)
		res = self.ses.get(url, headers=headers)
		check = re.search("login.php", res.text)
		if check != None: return 2
		try:
			soup = BeautifulSoup(res.content, 'html.parser')
			list_a = soup.find_all("a")
			for a in list_a:
				url = a.get("href")
				if "subscribe.php" in url:
					url = "https://mbasic.facebook.com"+url
					self.ses.get(url, headers=headers)
					return 1
			return 0
		except: return 0