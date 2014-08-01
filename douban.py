#!/usr/bin/python
# coding: utf-8
import os
import sys
import json
import md5
import base64
import urllib2
import urllib
import json
import random
import subprocess
import threading
import msvcrt
import time
login_url = 'http://www.douban.com/j/app/login'
channel_url = 'http://www.douban.com/j/app/radio/channels'
playlist_url = 'http://www.douban.com/j/app/radio/people?&app_name=radio_desktop_win&version=100'
search_url = 'http://music.163.com/api/search/get'
f = 'config.ini'
userinfo = None
reload(sys)
sys.setdefaultencoding('utf-8')
def add_userinfo(url):
	global userinfo
	if userinfo != None:
		user = json.loads(userinfo)
		user_id = user['user_id']
		token = user['token']
		expire = user['expire']
		return url + '&user_id='+user_id +'&token='+token +'&expire='+expire
	else:
		return url

def encrypted_id(id):
	byte1 = bytearray('3go8&$8*3*3h0k(2)2')
	byte2 = bytearray(id)
	byte1_len = len(byte1)
	for i in xrange(len(byte2)):
		byte2[i] = byte2[i]^byte1[i%byte1_len]
	m = md5.new()
	m.update(byte2)
	result = m.digest().encode('base64')[:-1]
	result = result.replace('/', '_')
	result = result.replace('+', '-')
	return result

def post_data(url, data,cookie):
	data = urllib.urlencode(data)
	if(cookie == None):
		cookie = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	urllib2.install_opener(cookie)
	return urllib2.urlopen(url, data).read()

def get_data(url):
	return urllib.urlopen(url).read()
	
def login_douban(email,password):
	if(email ==None) or (password == None):
		return None
	data ={
	'app_name':'radio_desktop_win', 
	'version':'100', 
	'email':email, 
	'password':password
	}
	return post_data(login_url,data,None).decode('utf-8')


# 获取播放列表
def get_play_list(channel='0',type='n',sid =None):
	url = add_userinfo(playlist_url) +'&channel='+ channel+'&type='+type
	if sid is not None:
		url = url +'&sid='+sid
	return get_data(url)

def get_palyback_url(channel,sid,like):
	url = add_userinfo(playlist_url)
	if url == playlist_url:
		return u'[INFO]:你还没登陆！'
	if like == '1':
		return u'[INFO]:Aready Rated this song'
	if channel is '-3':
		return u'[INFO]:正在播放红心歌单'
	return url +'&channel='+ channel +'&sid='+sid
	
def search_song_by_name(title):
	#set cookie
	cookie = urllib2.build_opener()
	cookie.addheaders.append(('Cookie', 'appver=2.0.2'))
	cookie.addheaders.append(('Referer', 'http://music.163.com'))
	data = {
			's': title.encode('utf-8'),
			'type': 1,
			'offset': 0,
			'sub': 'false',
			'limit': 20
	}
	resp_json = json.loads(post_data(search_url,data,cookie))
	if resp_json['code'] == 200 and resp_json['result']['songCount'] > 0:
		return resp_json['result']
	else:
		return None
def get_163_url_by_id(song_id):
	if song_id == None:
		return None
	detail_url = 'http://music.163.com/api/song/detail?ids=[%d]' % song_id
	resp = urllib2.urlopen(detail_url)
	song_js = json.loads(resp.read())
	song_dfsId = str(song_js['songs'][0]['bMusic']['dfsId'])
	return 'http://m%d.music.126.net/%s/%s.mp3' % (random.randrange(1, 3), encrypted_id(song_dfsId), song_dfsId)

def find_matched_url(result,artist,album):
	#if mode == '0':
	#	song_id = result['songs'][0]['id']
	#else:
	song_id = None
	if result['songCount'] > 1:
		for i in range(len(result['songs'])):
			tmp_artists =  result['songs'][i]['artists'][0]['name']
			tmp_album = result['songs'][i]['album']['name']
			#print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,tmp_song['name'], tmp_artists, tmp_album)
			if (tmp_artists.lower() == artist.lower()):
				song_id = result['songs'][i]['id']
				if(tmp_album.lower() == album.lower()):
					print '[*]',
				print '[*]',
				break
	return get_163_url_by_id(song_id)

def find_first_url(result,artist,album):
	song_id = result['songs'][0]['id']
	return get_163_url_by_id(song_id)

def run_callback(callback_url,type):
	if '[INFO]' not in callback_url:
		callback_url = callback_url+'&type='+type
		th = threading.Thread(target = get_data,args = (callback_url,))
		th.start()
		return 'Rated !'
	else:
		return callback_url
	
def kbfunc(): 
	ret = 'p'
	x = msvcrt.kbhit()
	if x: 
		ret = msvcrt.getch()
	else:
		time.sleep(1)
	return ret

def play(msg,url,callback_url):
	os.system('cls')
	print msg.encode('gbk')
	os.system("title [*]nowplaying...")
	playing = subprocess.Popen('mpg123 -qv '+url, shell = False)
	while playing.poll() is None:
		cmd = kbfunc()
		type = None
		if(cmd is 'r'):
			os.system('cls')
			print msg.encode('gbk')
			print run_callback(callback_url,'r')
		if(cmd is 'b'):
			playing.kill()
			run_callback(callback_url,'b')
			os.system("title [*]find a new song...")
			break
		if(cmd is 'n'):
			playing.kill()
			run_callback(callback_url,'s')
			os.system("title [*]find a new song...")
			break
		if(cmd is 'q'):
			playing.kill()
			run_callback(callback_url,'s')
			print '\n\nBye Bye!'
			sys.exit()
		if(cmd is 'c'):
			run_callback(callback_url,'s')
			playing.kill()
			os.system('cls')
			start()
	run_callback(callback_url,'e')
	os.system('cls')
	print u'\t正在载入下一曲...'

# 播放douban.fm
def play_channel(channel='0',type='n',mode ='0'):
	playlist = json.loads(get_play_list(channel,type,sid=None))
	for i in range(len(playlist['song'])):
		msg = None
		url = None
		title = playlist['song'][i]['title']
		artist = playlist['song'][i]['artist']
		album = playlist['song'][i]['albumtitle']
		douban_url = playlist['song'][i]['url']
		sid = playlist['song'][i]['sid']
		like = playlist['song'][i]['like']
		#print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,title, artist, album)
		if(album == u'豆瓣FM'):
			return
		if mode == '2':
			msg  = u'[@] 64K '
			url = douban_url
		else:
			result = search_song_by_name(title)
			if result == None:
				return
			url = find_matched_url(result,artist,album)	
			if url == None:
				if mode == '0':
					msg  = u'[@] 64K '
					url = douban_url
				if mode == '1':
					msg = u' [@] 320K '
					url = find_first_url(result,artist,album)
			else:
				msg = u' [*] 320K '
		msg = msg + u'[正在播放]:%s [艺术家]:%s [专辑]:%s\n' % (title, artist, album)
		callback_url = get_palyback_url(channel,sid,like)
		play(msg,url,callback_url)
		#print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,tmp_title, tmp_artists, tmp_album)
	print u'\t正在读取新播放列表...'

def start():
	global userinfo
	channel = '0'
	mode = '0'
	msg = u'\n[ q ] \t系统退出\t\t'
	if len(sys.argv) < 3:
		if os.path.isfile(f):
			data = file(f).read().split(' ### ')
			userinfo = data[0]
			res = json.loads( userinfo)
			msg = msg+ u'[-3]\t%s的红心收藏'% ( res['user_name'])
			mode = data[1]
	else:
		email = sys.argv[1]
		password = sys.argv[2]
		try:
			mode = sys.argv[3]
		except:
			pass
		userinfo = login_douban(email,password)
		res = json.loads( userinfo)
		if res['r'] != 1:
			msg = msg + u'[-3]\tchannel:%s的红心收藏'% ( res['user_name'])
			data = userinfo +" ### "+mode
			fp = open(f,'wb')
			fp.write(data.encode('utf-8'))
			fp.close()
		else:
			userinfo = None
	#
	channels = json.loads(get_data(channel_url))
	os.system("cls")
	os.system("title Douban320k player")
	print u'\t\t----------豆瓣FM频道列表------------'
	for i in range(len(channels['channels'])):
		id = int(channels['channels'][i]['channel_id'])
		name = channels['channels'][i]['name']
		if(i%2 == 0):
			print '[%2d]\tchannel:%s' % (id,name),
			if(len(name)<=3):
				print '\t',
		else:
			print '\t[%2d]\tchannel:%s' % (id,name)
		if(id ==16) or (id == 78):
			print '\t',
	#
	print msg
	channel = raw_input('Select Channel:')
	try:
		int(channel)
	except:
		print '\nBYE BYE!'
		sys.exit(0)
	os.system("cls")
	#播放开始
	type = 'n'
	while True:
		play_channel(channel,type,mode)

	
if __name__ == '__main__':
	try:
		start()
	except KeyboardInterrupt:
		os.system("cls")
		print '\nBYE!'
		sys.exit(0)
