import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep, localtime
import re

class Tool_tds():
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('today.txt'): open('today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('update.json'): open('update.json', 'w').write('{}')
	if not os.path.exists('list_nick.txt'): open('list_nick.txt', 'w').write("###Format: username|password|access_token")
	if not os.path.exists('cookie_update.txt'): open('cookie_update.txt', 'w').close()
	def __init__(self, list_nick):
		self.ses = requests.session()
		self.list_nick = list_nick
		self.list_config = {}
		self.cout_all = {}

	def show_info(self, access_token):
		url = f'https://traodoisub.com/api/?fields=profile&access_token={access_token}'
		res = self.ses.get(url)
		data = res.json()
		print("<=====================>")
		for i in data: print(i,':',data[i])
		print("<=====================>")

	def get_xu(self, access_token):
		url = f'https://traodoisub.com/api/?fields=profile&access_token={access_token}'
		res = self.ses.get(url)
		data = res.json()
		xu = int(data['xu'])
		return xu

	def get_nv(self, access_token, idfb, loainv):
		self.cauhinh_nick(idfb)
		list_nv =[]
		url = f'https://traodoisub.com/api/?fields={loainv}&access_token={access_token}'
		res = self.ses.get(url)
		data = res.json()
		for temp in data:
			name_nv = loainv.upper()
			idpost = temp['id']
			if loainv=='reaction': name_nv = temp['type']
			nv = name_nv+'|'+idpost
			list_nv.append(nv)
		return list_nv

	def cauhinh_nick(self, id_nick_fb):
		url = 'https://traodoisub.com/scr/datnick.php'
		payload = {'iddat[]' : id_nick_fb}
		self.ses.post(url, data=payload)

	def finish_job(self, nv):
		id_ob = nv.split('|')[1]
		name_nv = nv.split('|')[0]
		payload = {'id':id_ob}
		if name_nv == 'FOLLOW':
			requests_url = 'https://traodoisub.com/ex/follow/nhantien.php'
			xu = 600	
		elif name_nv == 'LIKE':
			requests_url = 'https://traodoisub.com/ex/like/nhantien.php'
			xu = 200
		else:
			payload['loaicx'] = name_nv
			requests_url = 'https://traodoisub.com/ex/reaction/nhantien.php'
			xu = 400
		res = self.ses.post(requests_url, data=payload)
		code = res.text
		return code, xu
# /////////////////////////////////////
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

	def get_info(self, username, token):
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		path_nick = f'data/{username}'
		if not os.path.exists(path_nick): os.mkdir(path_nick)
		path_data = f'{path_nick}/{data["name"]}_{data["id"]}'
		if not os.path.exists(path_data): os.mkdir(path_data)
		path_output = f'{path_data}/info.json'
		self.save_file_json(path_output, data)

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()
		
# /////////////////////////////////////
	def make_job_like(self, token, id_ob):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_ob}/likes'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data == True: return 1
		else:
			if data['error']['code'] == 368: return 2 # block
			if data['error']['code'] == 190: return 3 #Cookie die
			else: return 0 #Loi link
 
	def make_job_sub(self, token, id_ob):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_ob}/subscribers'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data == True: return 1
		else:
			if data['error']['code'] == 368: return 2 # block
			if data['error']['code'] == 190: return 3 #Cookie die
			else: return 0 #Loi link

	def make_job_reaction(self, cookie, token, id_ob, reaction):
		check = self.make_job_like(token, id_ob)
		if check==0: return 0 
		elif check==2: return 2
		elif check==3: return 3
		elif check==1:
			try:
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
				return 1
			except: return 0
# 1 thanh cong, 0 loi link, 2 block, 3 cookie die
	def making(self, token, cookie, nv):
		id_ob = nv.split('|')[1]
		name_nv = nv.split('|')[0]
		if name_nv=='LIKE':
			check = self.make_job_like(token, id_ob)
		elif name_nv=='FOLLOW':
			check = self.make_job_sub(token, id_ob) 
		else:
			reaction = name_nv
			check = self.make_job_reaction(cookie, token, id_ob, reaction)
		return check
# /////////////////////////////////////
	def time_now(self):
		time_now = f'{localtime().tm_hour}:{localtime().tm_min}:{localtime().tm_sec}'
		return time_now

	def log_current(self, username, sl=None):
		f = open('update.json', 'r')
		storage_nv = json.load(f)
		f.close()
		f = open('update.json', 'w')
		if username not in storage_nv: storage_nv[username] = 0
		if sl!=None: storage_nv[username] += sl
		json.dump(storage_nv, f, indent=4)
		f.close()

	def get_current(self, username):
		f = open('update.json', 'r')
		storage_nv = json.load(f)
		sl_current = storage_nv[username]
		f.close()
		return sl_current

	def check_reset(self):
		check = f'{localtime().tm_mday}{localtime().tm_mon}'
		today = open('today.txt', 'r').read()
		if today!=check:
			open('update.json', 'w').write('{}')
			open('today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')

	def get_list_idfb(self, username, password):
		url = 'https://traodoisub.com/scr/login.php'
		payload = {'username': username, 'password': password}
		res = self.ses.post(url, data = payload)
		if res.text == '{"success":true}':
			path_index = f'data/{username}'
			if not os.path.exists(path_index): os.mkdir(path_index)
			res = self.ses.get('https://traodoisub.com/view/cauhinh/')
			soup = BeautifulSoup(res.text, 'html.parser')
			data = soup.find_all(class_='list-group-item')
			list_idfb = {}
			for x in data: list_idfb[x.input['value']] = x.a.text
			return list_idfb
		else: return False

	def show_nick(self):
		print("<<<<<///Danh sách nick:")
		cout = 1
		for nick in self.list_nick:
			if '###' in nick: continue
			nick = nick.split('|')[0]
			print(f"\t{cout}.{nick}")
			cout+=1
		print("///>>>>>")

	def get_dk(self):
		print("[SETTING]")
		max_job = int(input("\t+Giới hạn NV: "))
		loop = int(input("\t+Nghỉ khi làm được: "))
		time_change = int(input("\t+Nhập thời gian nghỉ(s): "))
		delay = input('\t+Thời gian mỗi nv(vd:5 10): ').split(' ')
		delay[0] = int(delay[0])
		delay[1] = int(delay[1])
		return max_job, loop, time_change, delay

	def update_cookie(self, data, username, list_idfb):
		path_cookie = f'data/{username}/list_cookie.json'
		if not os.path.exists(path_cookie): open(path_cookie, 'w').write('{}')
		f = open(path_cookie, 'r')
		list_cookie = json.load(f)
		temp = data.split('\n')
		for cookie in temp:
			fc = re.findall(r'c_user=(.*?);', cookie)
			if fc==[]: continue
			for idfb in list_idfb:
				if fc[0] == idfb:
					list_cookie[idfb] = cookie
					break	
		f = open(path_cookie, 'w')
		json.dump(list_cookie, f, indent=4)
		f.close()

	def get_cookie(self, username):
		path_cookie = f'data/{username}/list_cookie.json'
		f = open(path_cookie, 'r')
		list_cookie = json.load(f)
		f.close()
		return list_cookie

	def run(self, username, access_token, list_idfb):
		dk = self.get_dk()
		max_job = dk[0]
		loop = dk[1]
		time_change = dk[2]
		delay = dk[3]

		print("[START]")
		list_cookie = self.get_cookie(username)
		list_nick_out = []
		list_job_error = []
		list_config = {}
		check_close = False
		while True:
			for idfb in list_idfb:
				if idfb in list_nick_out: continue
				cookie = list_cookie[idfb]
				token = self.get_token(cookie)
				if token=='':
					print(f"\033[91m[{list_idfb[idfb]}|COOKIE DIE]\033[37m")
					list_nick_out.append(idfb) 
					continue
				if idfb not in list_config:
					self.get_info(username, token)
					list_config[idfb] = ['like', 'reaction', 'follow']

				cout_local = 0
				xu = self.get_xu(access_token)
				cout_all = self.get_current(username)

				loainv = random.choice(list_config[idfb])
				list_nv = self.get_nv(access_token, idfb, loainv)
				for nv in list_nv:
					name_nv = nv.split('|')[0]
					idpost = nv.split('|')[1]

					if idpost in list_job_error: continue

					try: check = self.making(token, cookie, nv)
					except: check = 0

					if check==3:
						self.log_current(username, cout_local)
						print(f"\033[91m[{list_idfb[idfb]}|COOKIE DIE]\033[37m")
						list_nick_out.append(idfb)
						break

					elif check==2:
						self.log_current(username, cout_local)
						list_config[idfb].remove(loainv)
						if len(list_config[idfb])==0:
							print(f"\033[91m[{list_idfb[idfb]}|BLOCK ALL]\033[37m")
							list_nick_out.append(idfb)
							break
						else:
							print(f"\033[91m[{list_idfb[idfb]}|BLOCK {loainv.upper()}]\033[37m")
							break

					elif check==0:
						list_job_error.append(idpost)

					else:
						check = self.finish_job(nv)
						type_kq = check[0]
						gt = check[1]
						if type_kq != '2': list_job_error.append(idpost)
						else:
							cout_block = 0
							cout_local+=1
							xu+=gt
							cout_all+=1
							time_now = self.time_now()
							s1 = f'\033[33m[{time_now}]\033[37m'
							s2 = f'\033[32m [{cout_all}]|{list_idfb[idfb]}|{name_nv}|+{gt}|{xu} xu\033[37m'
							print(s1+s2)
							if cout_local >= loop:
								self.log_current(username, cout_local)
								sleep(time_change)
								break
							if cout_all >= max_job:
								self.log_current(username, cout_local)
								print(f"[HOÀN THÀNH {max_job} JOB]")
								return 0
							s = random.randint(delay[0], delay[1])
							sleep(s)
			if len(list_nick_out)>=len(list_idfb):
				print("\033[91m[HẾT NICK CHẠY]\033[37m")
				return 0	
				

	def run_tool(self):
		tool.show_nick()
		self.check_reset()
		option = input('->>Nhập nick chạy: ')
		temp = self.list_nick[int(option)].split('|')
		
		username = temp[0]
		password = temp[1]
		access_token = temp[2]
		list_idfb = self.get_list_idfb(username, password)
		if list_idfb!=False:
			print('Login success')
			self.show_info(access_token)
			self.log_current(username)
			check = input('>>>>Change cookie?(y/n): ')
			if check=='y':
				data = open("cookie_update.txt", 'r').read()
				self.update_cookie(data, username, list_idfb)
			self.run(username, access_token, list_idfb)
		else:
			print("Login failed!!!")

if __name__ == '__main__':
	list_nick = open('list_nick.txt', 'r').read().split("\n")
	tool = Tool_tds(list_nick)
	tool.run_tool()