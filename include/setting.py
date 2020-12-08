from datetime import datetime
from time import localtime
import json

class setting():
	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

	def fill_cookie(self, cookie):
		try:
			cookie = cookie.split(';')
			for cookie_tp in cookie:
				if 'c_user' in cookie_tp: c_user = cookie_tp.split('=')[1]
				if 'xs' in cookie_tp: xs = cookie_tp.split('=')[1]
				if 'datr' in cookie_tp: datr = cookie_tp.split('=')[1]
			cookie = f'c_user={c_user};xs={xs};datr={datr};'
			return c_user, cookie
		except: return None

	def show_nick(self):
		list_nick = self.load_file_json('data/nicks.json')
		print("<<<///Danh sách nick chạy:")
		cout = 0
		for nick in list_nick:
			print(f"{cout}.{list_nick[cout]['username']}")
			cout+=1
		print("///>>>")
	
	def add_nick(self, username, password):
		list_nick = self.load_file_json('data/nicks.json')
		nick = {}
		nick['username'] = username
		nick['password'] = password
		list_nick.append(nick)
		self.save_file_json('data/nicks.json', list_nick)

	def edit_nick(self, vt, cookie, list_fb):
		list_nick = self.load_file_json('data/nicks.json')
		if "list_fb" not in list_nick[vt]:
			list_nick[vt]["list_fb"] = list_fb
		else:
			list_fb = list_nick[vt]["list_fb"]
		list_cookie = cookie.split("\n")
		for cookie in list_cookie:
			for pos in range(len(list_fb)):
				if 'cookie' not in list_fb[pos]: list_fb[pos]['cookie'] = ""
				fill = self.fill_cookie(cookie)
				if fill == None: continue
				c_user = fill[0]
				cookie = fill[1]
				if list_fb[pos]["id"] != c_user: continue
				list_fb[pos]['cookie'] = cookie

		list_nick[vt]["list_fb"] = list_fb
		self.save_file_json('data/nicks.json', list_nick)

	def delete_nick(self, vt):
		try:
			list_nick = self.load_file_json('data/nicks.json')
			list_nick.pop(vt)
			self.save_file_json('data/nicks.json', list_nick)
		except: pass

	def time_now(self):
		time_now = datetime.now().strftime("%H:%M:%S")
		return time_now

	def log_current(self, username, sl=None):
		storage_nv = self.load_file_json('data/update.json')
		if username not in storage_nv: storage_nv[username] = 0
		if sl!=None: storage_nv[username] += sl
		self.save_file_json('data/update.json', storage_nv)

	def get_current(self, username):
		storage_nv = self.load_file_json('data/update.json')
		if username not in storage_nv: storage_nv[username] = 0
		sl_current = storage_nv[username]
		return sl_current

	def check_reset(self):
		check = f'{localtime().tm_mday}{localtime().tm_mon}'
		today = open('data/today.txt', 'r').read()
		if today!=check:
			open('data/update.json', 'w').write('{}')
			open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')

	def save_name_fb(self, username, name_fb):
		list_nick = self.load_file_json('data/nicks.json')
		for cout in range(0, len(list_nick)):
			if list_nick[cout]['username'] == username:
				list_nick[cout]['name_fb'] = name_fb
				break
		self.save_file_json('data/nicks.json', list_nick)