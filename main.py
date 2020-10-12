import requests
from bs4 import BeautifulSoup
import json
from os import path, mkdir, system
import random
from time import sleep
import sys
import re

class tool_tds():
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.ses = requests.session()
		self.xu = None
		self.list_nick = None
		self.path_index = None
		self.list_cookie = {}

	def login_tds(self):
		url = 'https://traodoisub.com/scr/login.php'
		payload = {'username': self.username, 'password': self.password}
		try:
			res = self.ses.post(url, data = payload)
			if res.text == '{"success":true}':
				self.path_index = f'nicks/{self.username}'
				if not path.exists(self.path_index): mkdir(self.path_index)
				name_file_cookie = f'{self.username}.txt'
				if not path.exists(name_file_cookie):
					open(name_file_cookie, 'w').close()
					input(f'Cookie in file : {name_file_cookie} (1 cookie / 1 line)')
				self.get_xu()
				self.get_ds_nick_fb()
				return True
			else: return False
		except: return False
	def get_xu(self):
		url = 'https://traodoisub.com/scr/test3.php?user='+self.username
		res = self.ses.get(url)
		self.xu = int(res.text)

	def get_ds_nick_fb(self):
		res = self.ses.get('https://traodoisub.com/view/cauhinh/')
		soup = BeautifulSoup(res.text, 'html.parser')
		data = soup.find_all(class_='list-group-item')
		list_nick = {}
		for x in data:
			list_nick[x.input['value']] = x.a.text
		self.list_nick=list_nick

	def cauhinh_nick(self, id_nick_fb):
		url = f'https://traodoisub.com/scr/api_dat.php?user={self.username}&idfb={id_nick_fb}'
		self.ses.get(url)

	def get_headers(self, cookie):
		headers = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'
		}
		headers['cookie'] = cookie
		return headers

	def get_token(self, cookie):
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=self.get_headers(cookie))
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def get_profile(self, cookie):
		params = {'access_token':self.get_token(cookie)}
		url = f'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		return data

	def get_list_friend(self, cookie):
		params = {'access_token':self.get_token(cookie)}
		url = f'https://graph.facebook.com/me?fields=friends'
		res = self.ses.get(url, params=params)
		data = res.json()
		data = data['friends']['data']
		return data

	def get_info(self, cookie, path_file_backup):
		data = self.get_profile(cookie)
		path_output = f'{path_file_backup}/info.json'
		self.save_file_json(path_output, data)
		data = self.get_list_friend(cookie)
		path_output = f'{path_file_backup}/list_friend.json'
		self.save_file_json(path_output, data)

	def check_cookie(self):
		name_file_cookie = f'{self.username}.txt'
		with open(name_file_cookie, 'r') as f:
			cout = 1
			while True:
				cookie = f.readline()
				cookie = cookie.replace('\n', '')
				if cookie=='': break
				c_user = re.findall(r'c_user=(.*?);', cookie)
				if c_user == []: print(f'Line {cout}: cookie sai!!!')
				else:
					user_id = c_user[0]
					check = False
					for id_nick_fb in self.list_nick:
						if user_id == id_nick_fb:
							check = self.get_token(cookie)
							if check=='':
								print(f'Line {cout}: {self.list_nick[user_id]} >> cookie die!!!')
								break
							print(f'Line {cout}: {self.list_nick[user_id]} >> cookie live!!!')
							self.list_cookie[user_id] = cookie
							path_file_backup = f'nicks/{self.username}/{user_id}'
							if not path.exists(path_file_backup):
								mkdir(path_file_backup)
								self.get_info(cookie, path_file_backup)
							check = True
							break
					if check==False: print(f'Line {cout}: TDS no have ID!!!')
				cout+=1
	def get_list_job(self, id_nick_fb):
		list_job = []
		self.cauhinh_nick(id_nick_fb)
		payload = {'key': 'dcfcd07e645d245babe887e5e2daa016'}
		urlst = 'https://traodoisub.com/ex'
		urlen = [
			['/like/', 'LIKE'],
			['/fanpage/', 'PAGE'],
			['/follow/', 'SUB'],
			['/comment/', 'CMT'],
			['/reaction/', '']
		]
		for url in urlen:
			url_head = urlst + url[0]
			url_request = url_head + 'load.php'
			self.ses.head(url_head)
			res = self.ses.post(url_request, data=payload)
			soup = BeautifulSoup(res.content, 'html.parser')
			if url[0] != '/comment/':
				cout = 0
				nvs = soup.find_all(class_='btn-outline-primary')
				for y in nvs:
					title = y.get('title')
					temp = y.get('onclick').split("'")
					id_job = temp[1]
					name_job = url[1]
					if url[0] == '/reaction/': name_job = temp[5]
					data_job = id_job+'|'+name_job+'|'+title
					list_job.append(data_job)
					cout += 1
					if cout >= 7: break
			elif url[0] == '/comment/':
				card = soup.find_all(class_='col-md-3')
				for y in card:
					f1 = y.find(class_='btn-outline-primary')
					f2 = y.find(class_='form-control')
					temp = f1['onclick'].split("'")
					title = f1.get('title')
					id_job = temp[1]
					name_job = url[1]
					cmt = f2.text
					job = id_job+'|'+name_job+'|'+title+'|'+cmt
					list_job.append(job)
		return list_job

	def fill_link(self, link):
		res = self.ses.get(link)
		link = res.url.replace('/www.', '/mbasic.')
		return link

	def make_job_sub(self, cookie, link):
		link = self.fill_link(link)
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		list_a = soup.find_all('a')
		check = False
		for a in list_a:
			url = a.get('href')
			if '/subscribe.php' in url:
				check = True
				break
		if check == True:
			link = 'https://mbasic.facebook.com'+url
			self.ses.get(link, headers=headers)
		return check

	def make_job_page(self, cookie, link):
		link = self.fill_link(link)
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		list_table = soup.find_all('table')
		check = False
		for table in list_table:
			if table.get('role') == "presentation":
				list_a = table.find_all('a')
				for a in list_a:
					url = a.get('href')
					if '/profile.php' in url:
						check = True
						break
				if check == True: break
		if check == True:
			link = 'https://mbasic.facebook.com'+url
			self.ses.get(link, headers=headers)
		return check

	def make_job_reaction(self, cookie, link, reaction):
		link = self.fill_link(link)
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		check = False
		list_a = soup.find_all('a')
		for a in list_a:
			url = a.get('href')
			if '/reactions/' in url:
				check = True
				break
		if check == True:
			link = 'https://mbasic.facebook.com' + url
			res = self.ses.get(link, headers=headers)
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			f = soup.find_all('li')
			dict_reactions = {'LIKE':0, 'LOVE':1, 'TT':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
			vt = dict_reactions[reaction]
			url = f[vt].a.get('href')	
			link = 'https://mbasic.facebook.com' + url
			self.ses.get(link, headers=headers)
		return check

	def make_job_comment(self, cookie, link, content):
		link = self.fill_link(link)
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		check = False
		list_form = soup.find_all('form')
		for form in list_form:
			url = form.get('action')
			if '/comment.php?' in url:
				ls_input = form.find_all('input')
				payload = {'comment_text': content, 'fb_dtsg': '', 'jazoest': ''}
				for i in ls_input:
					if i.get('name') == 'fb_dtsg': payload['fb_dtsg'] = i.get('value')
					if i.get('name') == 'jazoest': payload['jazoest'] = i.get('value')
				check = True
				break
		if check == True:
			link = 'https://mbasic.facebook.com' + url
			self.ses.post(link, data=payload, headers=headers)
		return check

	def make_all_fb(self, cookie, job):
		temp = job.split('|')
		id_job = temp[0]
		name_job = temp[1]
		link = temp[2]
		if name_job == 'SUB':
			check = self.make_job_sub(cookie, link)
		elif name_job == 'PAGE':
			check = self.make_job_page(cookie, link)
		elif name_job == 'CMT':
			content = temp[3]
			check = self.make_job_comment(cookie, link, content)
		else:
			reaction = name_job
			check = self.make_job_reaction(cookie, link, reaction)
		if check==True: return name_job, id_job
		return check

	def finish_job(self, name_job, id_job):
		tool.cauhinh_nick(id_nick_fb)
		payload = {'id':id_job}
		if name_job == 'SUB':
			requests_url = 'https://traodoisub.com/ex/follow/nhantien.php'
			xu = 600
		elif name_job == 'PAGE':
			requests_url = 'https://traodoisub.com/ex/fanpage/nhantien.php'
			xu = 600
		elif name_job == 'CMT':
			requests_url = 'https://traodoisub.com/ex/comment/nhantien.php'
			xu = 600		
		elif name_job == 'LIKE':
			requests_url = 'https://traodoisub.com/ex/like/nhantien.php'
			xu = 200
		else:
			payload['loaicx'] = name_job
			requests_url = 'https://traodoisub.com/ex/reaction/nhantien.php'
			xu = 400
		res = self.ses.post(requests_url, data=payload)
		kq = res.text
		if kq == '2': return xu
		return False

					
if __name__ == '__main__':
	if not path.exists('nicks'): mkdir('nicks')
	system('clear')
	username = input('>>>UserName: ')
	password = input('>>>PassWord: ')
	system('clear')
	tool = tool_tds(username, password)
	check = tool.login_tds()
	if check == True:
		print('\n>>>Login success!!!\n')
		print('><><><><><><><\n>>>Xu:', tool.xu,'xu\n><><><><><><><\n')
		print('>>>Checking cookie...\n><><><><>><><><><')
		tool.check_cookie()
		print('><><><><>><><><><')
		print('>>>Setting:')
		print('+Faebook max job(>30 job): ', end='')
		limit_job = 30 if int(input())=='' else int(input())
		loop_job = int(input('+Loop: '))
		time_change = int(input('+Time change(>30s): '))
		delay_from = int(input('+delay from: '))
		delay_to = int(input('+delay to: '))
		max_xu = int(input('><><><><>><><\n>>>>Max xu(n x 1000xu): '))*1000
		print('><><><><>><><')
		cout_all = 1
		dict_job = {}
		cout_make_fb = {}
		cout_failed = {}
		cout_cookie_die = 0
		check_close = False
		while True:
			try:
				check_cookie_die = True
				for id_nick_fb in tool.list_cookie:
					if id_nick_fb not in dict_job: dict_job[id_nick_fb]=[]
					if id_nick_fb not in cout_make_fb: cout_make_fb[id_nick_fb]=0
					if id_nick_fb not in cout_failed: cout_failed[id_nick_fb]=0
					if tool.list_cookie[id_nick_fb] != '': check_cookie_die = False
				if check_cookie_die == True:
					print('>>>Hết nick chạy!!!<<<')
					break
				list_nick = list(tool.list_cookie.keys())
				random.shuffle(list_nick)
				for id_nick_fb in list_nick:
					cookie = tool.list_cookie[id_nick_fb]
					if cookie=='': continue
					tool.cauhinh_nick(id_nick_fb)
					print('\n++>>FB make:',tool.list_nick[id_nick_fb])
					cout = 0
					while True:
						while True:
							if len(dict_job[id_nick_fb])>0: break
							dict_job[id_nick_fb] = tool.get_list_job(id_nick_fb)
						job = random.choice(dict_job[id_nick_fb])
						dict_job[id_nick_fb].remove(job)
						temp = job.split('|')
						print(f'>>>{cout_all}|{temp[1]}|', end='')
						check = tool.make_all_fb(cookie, job)
						if check == False:
							print('Failed :(')
							cout_failed[id_nick_fb]+=1	
						else:
							name_job = check[0]
							id_job = check[1]
							check = tool.finish_job(name_job, id_job)
							if check == False:
								cout_failed[id_nick_fb]+=1
								print('Failed :(')
								if cout_failed[id_nick_fb] >= 5:
									kt = tool.get_token(cookie)
									if kt!='': print('>>>Block interactive !!!<<<')
									else:
										print('>>>Checkpoint !!!<<<')
										tool.list_cookie[id_nick_fb]==''
										break
								continue
							else:					
								cout_failed[id_nick_fb] = 0
								cout_make_fb[id_nick_fb] += 1
								cout+=1
								tool.xu+=check
								cout_all+=1
								print(f'Success|>+{check}<|{tool.xu} xu', end='')
								if cout_make_fb[id_nick_fb] >= limit_job:
									print('\n>>>kịch rồi!!!<<<')
									tool.list_cookie[id_nick_fb]=''
									break
								if tool.xu >= max_xu:
									print(f'>>>Đã kiếm đủ {max_xu} xu!!!')
									check_close = True
									break
								s = random.randint(delay_from, delay_to)
								print(f' >>delay {s}s')
								sleep(s)
								if cout >= loop_job: break
					print(f'\n>>>Change FB...{time_change}s')
					sleep(time_change)
					if check_close == True: break
				if check_close == True: break
			except:
				while True:
					print('Lỗi mạng đợi 10s!!!')
					sleep(10)
					check = tool.login_tds()
					if check != False: break
	else: print('Login failed!!!')
	print('Kết thúc tool!!!')
