from bs4 import BeautifulSoup
import requests
import json
import re

class traodoisub():
	def __init__(self):
		self.ses = requests.session()

	def login_tds(self, username, password):
		try:
			url_tds = "https://traodoisub.com/scr/login.php"
			payload = {"username": username , "password": password}
			res = self.ses.post(url_tds, data=payload)
			data = res.json()
			if data == 1: return False
			if "success" in data: return True
		except: return None

	def get_xu(self, username):
		url = f"https://traodoisub.com/scr/test3.php?user={username}"
		res = self.ses.get(url)
		xu = int(res.text)
		return xu

	def get_list_fb(self):
		list_fb = []
		url_ch = "https://traodoisub.com/view/cauhinh/"
		res = self.ses.get(url_ch)
		soup = BeautifulSoup(res.text, "html.parser")
		list_group_item = soup.find_all(class_='list-group-item')
		for group_item in list_group_item:
			nick = {}
			nick["id"] = group_item.input.get("value")
			nick["name"] = group_item.text
			list_fb.append(nick)
		return list_fb	
		
	def cauhinh_nick(self, id_nick_fb):
		url = 'https://traodoisub.com/scr/datnick.php'
		payload = {'iddat[]' : id_nick_fb}
		res = self.ses.post(url, data=payload)
		if int(res.text) == 1: return True
		else: return False

	def get_nv(self, type_nv):
		list_nv = []
		payload = {"key": "dcfcd07e645d245babe887e5e2daa016"}
		if type_nv == "LIKE": url_head = "https://traodoisub.com/ex/like/"
		elif type_nv == "SUB": url_head = "https://traodoisub.com/ex/follow/"
		elif type_nv == "REACT": url_head = "https://traodoisub.com/ex/reaction/"
		url_get = url_head + "load.php"
		self.ses.head(url_head)
		res = self.ses.post(url_get, data = payload)
		soup = BeautifulSoup(res.text, "html.parser")
		list_pt = soup.find_all(class_="form-group text-center")
		for pt in list_pt:
			type_nv = pt.text.replace("\n", "").replace(" ", "")
			link = pt.button.get("title")
			id_nv = re.findall(r'\d+', link)
			if len(id_nv) != 1: continue 
			if type_nv == "Theodõi": type_nv = "SUB"
			if type_nv == "": continue
			nv = {}
			nv["type_nv"] = type_nv.upper()
			nv["id_nv"] = id_nv[0]
			list_nv.append(nv)
		return list_nv
		
	def finish_job(self, id_nv, type_nv):
		payload = {'id':id_nv}
		if type_nv == 'SUB':
			requests_url = 'https://traodoisub.com/ex/follow/nhantien.php'
			xu = 600	
		elif type_nv == 'LIKE':
			requests_url = 'https://traodoisub.com/ex/like/nhantien.php'
			xu = 200
		else:
			payload['loaicx'] = type_nv
			requests_url = 'https://traodoisub.com/ex/reaction/nhantien.php'
			xu = 400
		res = self.ses.post(requests_url, data=payload)
		code = res.text
		return code, xu

