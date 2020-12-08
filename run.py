import os
import random
from time import sleep, localtime
from include.traodoisub import traodoisub
from include.fb import fb
from include.setting import setting

class Auto_traodoisub():
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('data/nicks'): os.mkdir('data/nicks')
	if not os.path.exists('cookie.txt'): open('cookie.txt', 'w').close()
	if not os.path.exists('data/nicks.json'): open('data/nicks.json', 'w').write('[]')
	if not os.path.exists('data/today.txt'): open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('data/update.json'): open('data/update.json', 'w').write('{}')
	green = '\33[32m'
	red = '\33[31m'
	yellow = '\33[33m'
	white = '\33[37m'
	blue   = '\33[34m'
	def __init__(self):
		self.tds = traodoisub()
		self.fb = fb()
		self.st = setting()
		self.list_fb_out = []
		self.list_fb_run = []
		self.list_id_nv_error = []
		self.cout_all = 0
		self.list_type_nv = {}
		self.xu = None
		self.max_job = 2000
		self.cout_stop = 30
		self.time_stop = 30
		self.delay = 5

	def make_nv(self, cookie_fb, type_nv, id_nv):
		if type_nv == "SUB":
			res = self.fb.follow_id(cookie_fb, id_nv)
		else:
			res = self.fb.reaction_post(id_nv, cookie_fb, type_nv)
		return res

	def operations(self, nick):
		username = nick['username']
		password = nick['password']
		list_fb = nick['list_fb']
		self.st.check_reset()
		self.st.log_current(username)
		self.cout_all = self.st.get_current(username)
		while True:
			for fbook in list_fb:
				name_fb = fbook["name"]
				id_fb = fbook["id"]
				cookie_fb = fbook["cookie"]
				if cookie_fb == "": continue
				if id_fb not in self.list_fb_run:
					self.list_type_nv[id_fb] = ["LIKE", "SUB", "REACT"]
					self.list_fb_run.append(id_fb)

				if len(self.list_type_nv[id_fb]) == 0:
					print(f"{self.red}[{name_fb}|BLOCK ALL]{self.white}")
					self.list_fb_out.append(id_fb)
				if id_fb in self.list_fb_out:
					if len(self.list_fb_out) >= len(self.list_fb_run): return 0
					continue
				self.tds.cauhinh_nick(id_fb)
				cout_failed = 0
				cout_local = 0
				loai_nv = random.choice(self.list_type_nv[id_fb])
				print(f"\t>>>[{name_fb} | {loai_nv} ] <<<")
				list_nv = []
				while True:
					if len(list_nv) == 0:
						print("[get nv]")
						self.xu = self.tds.get_xu(username)
						list_nv = self.tds.get_nv(loai_nv)
						if len(list_nv) < 10:
							print("[Het nv]")
							break
					nv = list_nv.pop(0)
					type_nv = nv["type_nv"]
					id_nv = nv["id_nv"]

					if id_nv in self.list_id_nv_error:continue
					res = self.make_nv(cookie_fb, type_nv, id_nv)
					if res == 2:
						print(f"{self.red}[COOKIE DIE]{self.white}")
						self.list_fb_out.append(id_fb)
						break
					elif res == 0:
						print(f"{self.red}xxx{self.white}")
						self.list_id_nv_error.append(id_nv)
					elif res == 1:
						ht = self.tds.finish_job(id_nv, type_nv)
						code = ht[0]
						xxuu = ht[1]
						if code != "2":
							cout_failed += 1
							print(f"{self.red}...{self.white}")
							if cout_failed >= 3:
								check = self.fb.check_cookie_fb(cookie_fb)
								if check == True: 
									print(f"{self.red}[BLOCK {loai_nv}]{self.white}")
									self.list_type_nv[id_fb].remove(loai_nv)
								else: 
									print(f"{self.red}[COOKIE DIE]{self.white}")
									self.list_fb_out.append(id_fb)
								break
						else:
							cout_failed = 0
							cout_local += 1
							self.cout_all += 1
							self.xu += xxuu

							time_now = f"{self.yellow}[{self.st.time_now()}]{self.white}"
							print(time_now, end=' ')
							sssss = f"{self.green}[{self.cout_all}] |{name_fb} | {type_nv} | {xxuu} | {self.xu} xu{self.white}"
							print(sssss, end=' ')

							if self.cout_all % 3 == 0:
								self.st.log_current(username, 3)

							if cout_local > self.cout_stop: break
							if self.cout_all > self.max_job:
								print(f"\n[HOAN THANH {self.cout_all} NHIEM VU]")
								return 0
							s = random.randint(self.delay-2, self.delay+2)
							print(f"{self.blue}[wait {s}s]{self.white}")
							sleep(s)
				print(f"\n[CHUYEN NICK FACEBOOK {self.time_stop}S]")
				sleep(self.time_stop)

	def clear_console(self, cl):
		os.system(cl)
		self.st.show_nick()

	def run(self):
		color = 1
		if color==0:
			self.yellow=self.red=self.green=self.white=self.blue=''
			cl = 'cls'
		elif color==1: cl = 'clear'
		while True:
			self.clear_console(cl)
			print('\t1.Thêm\n\t2.Xóa\n<><><><><><><>')
			check = input("***Nhập lựa chọn: ")
			if check == '1':
				username = input("+username: ")
				password = input("+password: ")
				tool.st.add_nick(username, password)
			elif check == '2':
				vt = int(input("+Chọn nick cần xóa: "))
				self.st.delete_nick(vt)
			else:
				list_nick = self.st.load_file_json("data/nicks.json")
				while True:
					try:
						vt = int(input('>>>>>Nhập nick chạy: '))
						nick = list_nick[vt]
						username = nick["username"]
						password = nick["password"]
						break
					except:
						self.clear_console(cl)
				check = self.tds.login_tds(username, password)
				if check == None: print(f"{self.red}[LỖI MẠNG]{self.white}")
				elif check == False: print(f"{self.red}[Tài khoản, mật khẩu không chính xác]{self.white}")
				else:
					list_fb = self.tds.get_list_fb()
					while True:
						self.clear_console(cl)
						print(f"\n\t{self.blue}[{username} login success]{self.white}")
						self.xu = self.tds.get_xu(username)
						print(f"\t{self.yellow}[Số xu: {self.xu}]{self.white}\n")
						print('[OPTION]')
						print('\t1.Chạy\n\t2.Chỉnh sửa\n<><><><><><><>')
						check = input("***Nhập lựa chọn: ")
						if check=='2':
							input('+Cho cookie vào file "cookie.txt"!!!')
							cookie = open('cookie.txt', 'r').read()
							self.st.edit_nick(vt, cookie, list_fb)
							open('cookie.txt', 'w').close()
							self.clear_console(cl)
						elif check=='1':
							print('[SETTING]')
							print("\t+Giới hạn NV: 2000")
							print("\t+Nghỉ khi làm được: 30")
							print("\t+Nhập thời gian nghỉ(s): 30")
							print("\t+Delay(>3s): 5 ")
							check = input("+Mặc định?(y/n): ")
							if check=='n':
								os.system(cl)
								self.st.show_nick()
								print('[SETTING]')
								self.max_job = int(input("\t+Giới hạn NV: "))
								self.cout_stop = int(input("\t+Nghỉ khi làm được: "))
								self.time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
								self.delay = int(input("\t+Delay(>3s): "))
							print('[START]')
							list_nick = self.st.load_file_json("data/nicks.json")
							nick = list_nick[vt]
							self.operations(nick)
							print("[Kết thúc tool]")
							return 0		

if __name__ == '__main__':
	tool = Auto_traodoisub()
	tool.run()
