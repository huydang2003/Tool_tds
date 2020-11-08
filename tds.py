import requests
from bs4 import BeautifulSoup
import json
from os import path, mkdir, system
import random
from time import sleep
import re

class tool_tds():
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.ses = requests.session()
		self.xu = None
		self.list_nick = None
		self.path_index = None
		self.list_ct = {}

	def login_tds(self):
		url = 'https://traodoisub.com/scr/login.php'
		payload = {'username': self.username, 'password': self.password}
		try:
			res = self.ses.post(url, data = payload)
			if res.text == '{"success":true}':
				self.path_index = f'nicks/{self.username}'
				if not path.exists(self.path_index): mkdir(self.path_index)
				name_file_cookie = f'cookie/{self.username}.txt'
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
		url = 'https://traodoisub.com/scr/datnick.php'
		payload = {'iddat[]' : id_nick_fb}
		self.ses.post(url, data=payload)

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
	
	def get_info(self, token):
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		path_nick = f'nicks/{self.username}'
		if not path.exists(path_nick): mkdir(path_nick)
		path_data = f'{path_nick}/{data["name"]}_{data["id"]}'
		if not path.exists(path_data): mkdir(path_data)
		path_output = f'{path_data}/info.json'
		self.save_file_json(path_output, data)
		url = 'https://graph.facebook.com/me?fields=friends'
		res = self.ses.get(url, params=params)
		data = res.json()
		data = data['friends']['data']
		path_output = f'{path_data}/list_friend.json'
		self.save_file_json(path_output, data)

	def check_cookie(self, fb_id):
		name_file_cookie = f'cookie/{self.username}.txt'
		data = open(name_file_cookie, 'r').read()
		list_cookie = data.split('\n')
		cout = 1
		check = False
		for cookie in list_cookie:
			if cookie=='': continue
			fc = re.findall(r'c_user=(.*?);', cookie)
			if fc == []: continue
			temp = fc[0]
			for id_nick_fb in self.list_nick:
				if temp==id_nick_fb and temp==fb_id:
					token = self.get_token(cookie)
					if token=='':
						print(f'[cookie DIE (line {cout})]')
						return check
					self.list_ct[fb_id] = {}
					self.list_ct[fb_id]['cookie'] = cookie
					self.list_ct[fb_id]['token'] = token
					print(f'[cookie LIVE (line {cout})]')
					self.get_info(token)
					check = True
					return check
			cout+=1
		print('No have cookie')
		return check

	def get_list_job(self, id_nick_fb):
		list_job = []
		self.cauhinh_nick(id_nick_fb)
		payload = {'key': 'dcfcd07e645d245babe887e5e2daa016'}
		urlst = 'https://traodoisub.com/ex'
		urlen = [
			['/like/', 'LIKE'],
			# ['/fanpage/', 'PAGE'],
			['/follow/', 'SUB'],
			# ['/comment/', 'CMT'],
			['/reaction/', '']
		]
		for url in urlen:
			url_head = urlst + url[0]
			url_request = url_head + 'load.php'
			self.ses.head(url_head)
			res = self.ses.post(url_request, data=payload)
			soup = BeautifulSoup(res.content, 'html.parser')
			if url[0] != '/comment/':
				nvs = soup.find_all(class_='btn-outline-primary')
				for y in nvs:
					title = y.get('title')
					temp = y.get('onclick').split("'")
					id_job = temp[1]
					if '_' in id_job: continue
					name_job = url[1]
					if url[0] == '/reaction/': name_job = temp[5]
					data_job = id_job+'|'+name_job+'|'+title
					list_job.append(data_job)
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

	def make_job_like(self, token, id_ob):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_ob}/likes'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data == True: return 1
		else:
			if data['error']['code'] != 368: return 0
			else: return 2

	def make_job_sub(self, token, id_ob):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_ob}/subscribers'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data == True: return 1
		else:
			if data['error']['code'] != 368: return 0
			else: return 2

	def make_job_comment(self, token, id_ob, content):
		params = {'access_token': token, 'message':content}
		url = f'https://graph.facebook.com/{id_ob}/comments'
		res = self.ses.post(url, params=params)
		data = res.json()
		if 'id' in data: return 1
		else:
			if data['error']['code'] != 368: return 0
			else: return 2

	def make_job_page(self, cookie, link):
		temp = self.ses.head(link).headers
		if 'Location' in temp: link = temp['Location'].replace('/www.', '/mbasic.')
		else: return 0
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		check = 0
		list_table = soup.find_all('table')
		if list_table == []: return check
		for table in list_table:
			if table.get('role') == "presentation":
				list_a = table.find_all('a')
				for a in list_a:
					url = a.get('href')
					if '/profile.php' in url:
						check = 1
						break
				if check == 1: break
		if check == 1:
			link = 'https://mbasic.facebook.com'+url
			self.ses.get(link, headers=headers)
		return check

	def make_job_reaction(self, cookie, token, id_ob, reaction):
		check = self.make_job_like(token, id_ob)
		if check==0: return 0
		elif check==2: return 2
		elif check==1:
			dict_reaction = {'LIKE':0, 'LOVE':1, 'TT':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
			link = 'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id='+id_ob
			headers = self.get_headers(cookie)
			res = self.ses.get(link, headers=headers)
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			list_li = soup.find_all('li')	
			vt = dict_reaction[reaction]
			url = list_li[vt].a.get('href')	
			link = 'https://mbasic.facebook.com' + url
			self.ses.get(link, headers=headers)
			return check

	def make_all_fb(self, cookie, token, job):
		temp = job.split('|')
		id_ob = temp[0]
		name_job = temp[1]
		link = temp[2]
		if name_job == 'SUB':
			check = self.make_job_sub(token, id_ob)
		elif name_job == 'PAGE':
			check = self.make_job_page(cookie, link)
		elif name_job == 'LIKE':
			check = self.make_job_like(token, id_ob)
		elif name_job == 'CMT':
			content = temp[3]
			check = self.make_job_comment(token, id_ob, content)
		else:
			reaction = name_job
			check = self.make_job_reaction(cookie, token, id_ob, reaction)
		return check

	def finish_job(self, id_nick_fb, job):
		self.cauhinh_nick(id_nick_fb)
		temp = job.split('|')
		id_ob = temp[0]
		name_job = temp[1]
		payload = {'id':id_ob}
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
		return res.text, xu

	def run_tool(self):
		print('><><><><>><><><><')
		print('>>>Setting:')

		print('+Faebook max NV(>30 job): ', end='')
		limit_job =  int(input())
		print('+Loop NV: ', end='')
		loop_job = int(input())
		print('+Time change FB(>30s): ', end='')
		time_change = int(input())
		delay = input('+delay: ')
		st = int(delay.split(' ')[0])
		en = int(delay.split(' ')[1])
		print('><><><><>><><\n>>>>Max xu(n x 1000xu): ', end='')
		max_xu = int(input())*1000
		print('><><><><>><><')

		cout_all = 1
		dict_job = {}
		cout_make_fb = {}
		cout_failed = {}
		cout_cookie_die = 0
		check_close = False
		list_job_error = []
		cout_nick_checkpoint = 0
		list_nick_block = []
		
		list_nick = list(self.list_nick.keys())
		random.shuffle(list_nick)
		while True:
			for id_nick_fb in self.list_nick:
				if id_nick_fb not in dict_job: dict_job[id_nick_fb]=[]
				if id_nick_fb not in cout_make_fb: cout_make_fb[id_nick_fb]=1
				if id_nick_fb not in cout_failed: cout_failed[id_nick_fb]=0

			for id_nick_fb in list_nick:
				print(f'\n++>>FB make:', self.list_nick[id_nick_fb])
				check = self.check_cookie(id_nick_fb)
				if check==False:
				    cout_nick_checkpoint+=1
				    list_nick_block.append(id_nick_fb)
				    continue
				if id_nick_fb in list_nick_block: continue
				token = self.list_ct[id_nick_fb]['token']
				cookie = self.list_ct[id_nick_fb]['cookie']
				cout = 0
				while True:
					if cout >= loop_job: break
					try:
						dict_job[id_nick_fb] = self.get_list_job(id_nick_fb)
						if len(dict_job[id_nick_fb])>0:
							print("\033[91m[Hết JOB]\033[37m")
							break
						job = random.choice(dict_job[id_nick_fb])
						dict_job[id_nick_fb].remove(job)
						temp = job.split('|')
						name_job = temp[1]
						link_job = temp[2]
						if link_job in list_job_error: continue
						print(f'\033[32m<{cout_all}|{name_job}|>{cout_make_fb[id_nick_fb]}<|\033[37m', end='')
						check = self.make_all_fb(cookie, token, job)
						if check == 1:
							kq = self.finish_job(id_nick_fb, job)
							type_kq = kq[0]
							xu = kq[1]
							if type_kq != '2': list_job_error.append(link_job)
							else:
								cout_make_fb[id_nick_fb] += 1
								cout+=1
								self.xu+=xu
								cout_all+=1
								print(f'\033[32msuccess|>+{xu}<|{self.xu} xu\033[37m')
								if cout_make_fb[id_nick_fb] > limit_job:
									print(f'\n\033[91m>>>Kịch rồi!!!<<<\033[37m')
									list_nick_block.append(id_nick_fb)
									break
								if self.xu >= max_xu:
									print('\n><><><>><><><><')
									print(f'\033[37m>>>Đã kiếm đủ {max_xu} xu!!!\033[37m')
									print('><><><>><><><><')
									check_close = True
									break
								s = random.randint(st, en)
								sleep(s)
						elif check == 0:
							list_job_error.append(link_job)
						elif check==2:
							list_nick_block.append(id_nick_fb)
							token = self.get_token(cookie)
							if token=="": print("\n\033[91m[COOKIE DIE]\033[37m")
							else: print("\n\033[91m[BLOCK LIKE]\033[37m")
							break
					except:
						while True:
							print(f'\n\033[91m[lỗi mạng đợi 5s!!!]\033[37m')
							sleep(5)
							check = self.login_tds()
							if check != False: break
				if check_close == True: break
				print(f'[Change FB after {time_change}s]')
				sleep(time_change)

			if check_close == True: break
			if len(list_nick_block) >= len(self.list_nick):
				print('Hết nick chạy rồi !!!')
				break
			if cout_nick_checkpoint >= len(self.list_nick):
				print('Die hết nick rồi :(')
				break
	
if __name__ == '__main__':
	if not path.exists('nicks'): mkdir('nicks')
	if not path.exists('cookie'): mkdir('cookie')
	username = input('>>>UserName: ')
	password = input('>>>PassWord: ')
	# system('clear')
	tool = tool_tds(username, password)
	check = tool.login_tds()
	if check == True:
		print('\n>>>Login success!!!\n')
		print('><><><><><><><\n>>>Xu:', tool.xu,'xu\n><><><><><><><\n')
		id_nick_fb = '100037892140704'
		list_job = tool.get_list_job(id_nick_fb)
		print(list_job)
		# tool.run_tool()
	else: print('Login failed!!!')
	print('Kết thúc tool!!!')
		
