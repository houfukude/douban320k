#!/usr/bin/python
# coding: utf-8
import os
import sys
import json
import md5
import json
import time
import urllib
import urllib2
import signal
import select
import base64
import random
import threading
import subprocess
login_url = 'http://www.douban.com/j/app/login'
channel_url = 'http://www.douban.com/j/app/radio/channels'
playlist_url = 'http://www.douban.com/j/app/radio/people?&app_name=radio_desktop_win&version=100'
search_url = 'http://music.163.com/api/search/get'
cfg = 'config.ini'
try:
    import msvcrt
    clear = 'cls'
    isUnix = False
except:
    isUnix = True
    import termios
    clear = 'clear'
#Unix keyboard Listener
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = old_settings
    #new_settings[3] = new_settings[3] & ~termios.ISIG
    new_settings[3] = new_settings[3] & ~termios.ICANON
    new_settings[3] = new_settings[3] & ~termios.ECHONL
    #print 'old setting %s'%(repr(old_settings))
    termios.tcsetattr(fd,termios.TCSAFLUSH,new_settings)

#set cookie
netsase_cookie = urllib2.build_opener()
netsase_cookie.addheaders.append(('Cookie', 'appver=2.0.2'))
netsase_cookie.addheaders.append(('Referer', 'http://music.163.com'))
#code

reload(sys)
sys.setdefaultencoding('utf-8')

userinfo = None
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

def get_data(url_with_data,cookie=None):
    if(cookie == None):
        cookie = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(cookie)
    return urllib2.urlopen(url_with_data).read()

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

def search_song_by_name(name):
    data = {
            's': name.encode('utf-8'),
            'type': 1,
            'offset': 0,
            'sub': 'false',
            'limit': 20
    }
    resp_json = json.loads(post_data(search_url,data,netsase_cookie))
    if resp_json['code'] == 200 and resp_json['result']['songCount'] > 0:
        return resp_json['result']
    else:
        return None

def get_163_url_by_id(song_id):
    if song_id == None:
        return None
    detail_url = 'http://music.163.com/api/song/detail?ids=[%d]' % song_id
    song_js = json.loads(get_data(detail_url,netsase_cookie))
    song_dfsId = str(song_js['songs'][0]['bMusic']['dfsId'])
    return 'http://m%d.music.126.net/%s/%s.mp3' % (random.randrange(1, 3), encrypted_id(song_dfsId), song_dfsId)

def find_matched_url(result,artist,album):
    song_id = None
    if result['songCount'] > 1:
        for i in range(len(result['songs'])):
            tmp_artists =  result['songs'][i]['artists'][0]['name']
            tmp_album = result['songs'][i]['album']['name']
            #print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,tmp_song['name'], tmp_artists, tmp_album)
            if (tmp_artists.lower() == artist.lower()):
                song_id = result['songs'][i]['id']
                if(tmp_album.lower() == album.lower()):
                    break
    return get_163_url_by_id(song_id)

def find_first_url(result,artist,album):
    song_id = result['songs'][0]['id']
    return get_163_url_by_id(song_id)

def get_palyback_url(channel,sid):
    url = add_userinfo(playlist_url)
    if url == playlist_url:
        return u'\t[INFO]:你还没登陆！'
    return url +'&channel='+ channel +'&sid='+sid

def run_callback(callback_url,t,like = '-1'):
	if int(like) == 1 and t == 'r':
		return u'\t[INFO]:已红心过了！'
	if int(like) == 0 and t == 'u':
		return u'\t[INFO]:未曾红心过！'
	if '[INFO]' not in callback_url:
		callback_url = callback_url+'&type='+t
		th = threading.Thread(target = get_data,args = (callback_url,))
		th.start()
		return {-1:u'\t[INFO]:已完成服务器反馈！',0:u'\t[INFO]:已红心标记！',1:u'\t[INFO]:已取消红心！',}[int(like)]
	else:
		return callback_url

def keyboard_func(): 
    ret = '\x00'
    if isUnix:
        fd = sys.stdin.fileno()
        x = select.select([sys.stdin],[],[],0.01)
        if len(x[0]) >0:
            ret = sys.stdin.read(1)
        else:
            time.sleep(1)
    else:
        x = msvcrt.kbhit()
        if x:
            ret = msvcrt.getch()
        else:
            time.sleep(1)
    return ret

def getChar(): 
    if isUnix :
        return sys.stdin.read(1)
    else:
        return msvcrt.getch()

def kill(p):
    if isUnix:
        os.killpg(p.pid, signal.SIGTERM)
    else:
        p.kill()

def play(msg,url,callback_url,like):
    cmds =  "mpg123 -qv "+url
    os.system(clear)
    if isUnix:
        playing = subprocess.Popen(cmds, shell = True, preexec_fn=os.setsid)
    else:
        msg = msg.encode('gb18030')
        playing = subprocess.Popen(cmds, stdin = subprocess.PIPE, shell = False)
    print msg
    print {1:u'\t[INFO]:已红心！',0:u'\t[INFO]:未红心！',}[int(like)]
    while playing.poll() is None:
        key = keyboard_func()
        if key == '\x00':
            continue
        else :
            if key == '\033': #Esc
                if isUnix:
                    getChar()
                    key = getChar()
                    if key.lower() == 'a': #up
                        key = 'n'
                    elif key.lower() == 'b':
                        key = 'r'
                    elif key.lower() == 'c':
                        key = 'u'
                    elif key.lower() == 'd':
                        key = 'c'
                else:
                    key = 'q'
            if key == '\xe0':#NoneABC
                key = getChar()
                if key.lower() == 'm':
                    key = 'n'
                elif key.lower() == 'h':
                    key = 'r'
                elif key.lower() == 'p':
                    key = 'u'
                elif key.lower() == 'k':
                    key = 'c'
                else:
                    continue
            #run
            os.system(clear)
            print msg
            if key.lower() == 'n':
                kill(playing)
                t = 's'
                break
            if key.lower() == 'r':
                print run_callback(callback_url,key.lower(),like)
                like = 1
            if key.lower() == 'u':
                print run_callback(callback_url,key.lower(),like)
                like = 0
            if key.lower() == 'b':
                kill(playing)
                t = 'b'
                break
            if key.lower() == 'c':
                kill(playing)
                start()
            if key.lower() == 'q':
                kill(playing)
                print '\n\nBye Bye!'
                sys.exit()
    os.system(clear)        
    run_callback(callback_url,t='e')
    print u'\t[INFO]:正在载入下一曲...'

# 播放douban.fm
def play_channel(channel='0',type='n',mode ='0'):
    playlist = json.loads(get_play_list(channel,type))
    for i in range(len(playlist['song'])):
        msg = None
        url = None
        title = playlist['song'][i]['title']
        artist = playlist['song'][i]['artist']
        album = playlist['song'][i]['albumtitle']
        douban_url = playlist['song'][i]['url']
        sid = playlist['song'][i]['sid']
        like = playlist['song'][i]['like']
        #kbps = playlist['song'][i]['kbps']
        #print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,title, artist, album)
        if(album == u'豆瓣FM'):
            return
        if mode == '2':
            msg  = u'\t[@] 64K '
            url = douban_url
        else:
            result = search_song_by_name(title)
            if result == None:
                return
            url = find_matched_url(result,artist,album)    
            if url == None:
                if mode == '0':
                    msg  = u'\t[@] 64K '
                    url = douban_url
                if mode == '1':
                    msg = u'\t[@] 320K '
                    url = find_first_url(result,artist,album)
            else:
                msg = u'\t[*] 320K '
        msg = msg + u'[正在播放]:%s \n\t[艺术家]:%s [专辑]:%s' % (title.encode('utf-8'), artist.encode('utf-8'), album.encode('utf-8'))
        callback_url = get_palyback_url(channel,sid)
        play(msg,url,callback_url,like)
        #print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,tmp_title, tmp_artists, tmp_album)
    os.system(clear)
    print u'\t正在读取新播放列表...'

def start():
    global userinfo
    channel = '0'
    mode = '0'
    msg = u'[ q ] \t系统退出\t\t[-3]\t%s的红心收藏'
    #os.system("title Douban320k player")
    if len(sys.argv) < 3:
        if os.path.isfile(cfg):
            data = file(cfg).read().split(' ### ')
            userinfo = data[0]
            res = json.loads( userinfo)
            msg = msg % ( res['user_name'])
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
        print res
        if res['r'] != 1:
            msg = msg % ( res['user_name'])
            data = userinfo +" ### "+mode
            fp = open(cfg,'wb')
            fp.write(data.encode('utf-8'))
            fp.close()
        else:
            userinfo = None
    #
    channels = json.loads(get_data(channel_url))
    os.system(clear)
    print u'\t\t----------豆瓣FM频道列表------------'
    for i in range(len(channels['channels'])):
        id = int(channels['channels'][i]['channel_id'])
        name = channels['channels'][i]['name']
        if(i%2 == 0):
            print '[%2d]\tchannel:%s' % (id,name),
            if(len(name)<=3):
                print '\t',
            if (i == range(len(channels['channels']))):
                print ''
        else:
            print '\t[%2d]\tchannel:%s' % (id,name)
        if(id ==16) or (id == 77):
            print '\t',
    #
    print msg
    channel = raw_input(u'Select a Channel:')
    try:
        int(channel)
    except:
        print '\nBYE BYE!'
        sys.exit(0)
    os.system(clear)
    #播放开始
    #type = 'n'
    while True:
        play_channel(channel=channel,mode =mode)
    
if __name__ == '__main__':
    try:
        os.system(clear)
        start()
    except KeyboardInterrupt:
        os.system(clear)
        print '\nBYE!'
        sys.exit(0)
