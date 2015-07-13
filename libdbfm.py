# -*- coding: cp936 -*-
import urllib
import urllib2
import cookielib
import httplib
import json
import re
import random
import contextlib
import os
import sys
from Cookie import SimpleCookie
__all__ = ['DoubanFM', 'DoubanLoginException', 'DoubanFMChannels']

class DoubanTrack(object):
    def __init__(self, **data):
        self.props = {}
        for name in data:
            self.props[name] = data[name]

    def get_start_value(self):
        return "%sg%sg0" % (self.sid, self.ssid)

    def get_uri(self):
        return "http://douban.fm/?start=%s" % (self.get_start_value())

    def __getattr__(self, name):
        if name in self.props:
            return self.props[name]
        else:
            return None

class DoubanFM(object):
    def __init__ (self):
        """Initialize a douban.fm session.
        * username - the user's email on douban.com
        * password - the user's password on douban.com
        """
        self.uid = None
        self.dbcl2 = None
        self.bid = "11111111111"
        self._channel = 0
        self.LoginFlag=1
        self.__load_channels()

    def login2(self,username,password):
        if not self.__login2(username,password):
            print 'b2'
            return False
        self.__load_channels()

    def login(self,username, password):
        if not self.__login(username, password):#如果是false则return False
             print 'b'
             return False
        self.__load_channels()

    def loadConfig(self,config):
            self.dbcl2 = config.get('Cookie', 'dbcl2')
            self.uid = config.get('UserInfo','uid')
            self._channel = config.getint('UserInfo','channel')
            if self.dbcl2 == None or self.uid == None:
                return False
            else:
                return True
    
    def saveConfig(self,config):
        try:
            config.set('Cookie', 'dbcl2',self.dbcl2)
            config.set('UserInfo','uid',self.uid)
            config.set('UserInfo','channel',self._channel)
        except:
            pass

    def __load_channels(self):
        # f = urllib.urlopen('http://www.douban.com/j/app/radio/channels')
        # data = f.read()
        # f.close()
        # channels = json.loads(data)
        # self.channels = {}
        # for channel in channels['channels']:
        #     if not  channel['channel_id']==0:
        #         self.channels[channel['name']] = channel['channel_id']
        f = urllib.urlopen('http://www.douban.com/j/app/radio/channels')
        f = urllib.urlopen('http://www.douban.com/j/app/radio/channels?version=100&app_name=radio_desktop_win')
        data = f.read()
        f.close()
        channels = json.loads(data)
        self.channels = {}
        #red channel
        self.channels['Red Heart'] = -3
        #Personal Radio High
        #self.channels['Personal Radio High'] = -4
        #Personal Radio Easy
        #self.channels['Personal Radio Easy'] = -5
        i=0
        for channel in channels['channels']:
            if not  channel['channel_id']==0:
                self.channels[channel['name']] = channel['channel_id']

    
    def get_channel(self):
        """ current channel """
        return self._channel

    def set_channel(self, value):
        """ setter for current channel 
        * value - channel id, **not channel name**
        """
        self._channel = value

    def get_image(self):
        self.loginurl = 'https://www.douban.com/accounts/login'
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        
    #从首页提交登录
        response=self.opener.open(self.loginurl)#, urllib.urlencode(params))
    #验证成功跳转至登录页
        if response.geturl() == "https://www.douban.com/accounts/login":
            html=response.read()
        #验证码图片地址
            imgurl=re.search('<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>', html)
        if imgurl:
            url=imgurl.group(1)
            #将图片保存至同目录下
            res=urllib.urlretrieve(url, sys.path[0]+'/Image/IDimg.jpg')
            self.captcha=re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>' ,html)
            if self.captcha:
                #self.vcode=raw_input('请输入图片上的验证码:')
                return True
        else:
            return False
    def __login2(self,username,password):#有图片
                params = {"form_email":username,"form_password":password,"source":"index_nav"}
                params["captcha-solution"] =self.vcode
                params["captcha-id"] = self.captcha.group(1)
                params["user_login"] = "登录"
                #获取captcha-id参数            
                contentType = "application/x-www-form-urlencoded"
                print params
                data=urllib.urlencode(params)
                headers = {"Content-Type":contentType}
                with contextlib.closing(httplib.HTTPConnection("www.douban.com")) as conn:
                    conn.request("POST", "/accounts/login", data, headers)                    
                    r1 = conn.getresponse()
                    resultCookie = SimpleCookie(r1.getheader('Set-Cookie'))
                    if not resultCookie.has_key('dbcl2'):#登陆失败
                        print 'a21'
                        self.LoginFlag=0
                        print 'No'
                    else:
                        print 'a22'
                        print 'Yes'
                        self.LoginFlag=1
                        dbcl2 = resultCookie['dbcl2'].value
                        if dbcl2 is not None and len(dbcl2) > 0:
                           self.dbcl2 = dbcl2
                           uid = self.dbcl2.split(':')[0]
                           self.uid = uid
                           bid = resultCookie['bid'].value
                           self.bid = bid
    def __login(self, username, password):
        """
        login douban, get the session token
        """
        self.__get_login_data()
        data = urllib.urlencode({'source':'simple', 
                'form_email':username, 'form_password':password, 'remember':'on'})
        contentType = "application/x-www-form-urlencoded"

        cookie = 'bid="%s"' % self.bid

        headers = {"Content-Type":contentType, "Cookie": cookie }
        with contextlib.closing(httplib.HTTPSConnection("www.douban.com")) as conn:
            conn.request("POST", "/accounts/login", data, headers)        
            r1 = conn.getresponse()
            print r1.read()
            resultCookie = SimpleCookie(r1.getheader('Set-Cookie'))
            if not resultCookie.has_key('dbcl2'):
                print 'a1'
                self.LoginFlag=0

            else:
                print 'a11'
                print 'Yes'
                self.LoginFlag=1
                dbcl2 = resultCookie['dbcl2'].value
                if dbcl2 is not None and len(dbcl2) > 0:
                      self.dbcl2 = dbcl2
                      uid = self.dbcl2.split(':')[0]
                      self.uid = uid
                      bid = resultCookie['bid'].value
                      self.bid = bid
    def __get_login_data(self):
        conn = httplib.HTTPConnection("www.douban.com")
        conn.request("GET", "/")
        resp = conn.getresponse()
        cookie = resp.getheader('Set-Cookie')
        cookie = SimpleCookie(cookie)
        conn.close()
        if not cookie.has_key('bid'):
            #raise DoubanLoginException()
            pass
        else:
            self.bid = cookie['bid']

            return self.bid

    def __format_list(self, sidlist, verb=None):
        """
        for sidlist with ite verb status
        """
        if sidlist is None or len(sidlist) == 0:
            return ''
        else:
            if verb is not None:
                return ''.join(map(lambda s: '|'+str(s)+':'+str(verb), sidlist))
            else:
                return ''.join(map(lambda s: '|'+str(s), sidlist))
   
    def __get_default_params (self, typename=None):
        """
        default request parameters, for override
        """
        params = {}
        for i in ['aid', 'channel', 'du', 'h', 'r', 'rest', 'sid', 'type', 'uid']:
            params[i] = ''
            
        params['r'] = random.random()
        params['uid'] = self.uid
        params['channel'] = self._channel

        if typename is not None:
            params['type'] = typename

        return params

    def __remote_fm(self, params, start=None):
        """
        io with douban.fm
        """
        conn = httplib.HTTPConnection("douban.fm")
        data = urllib.urlencode(params)
        if start is not None:
            cookie = 'dbcl2="%s"; bid="%s"; start="%s"' % (self.dbcl2, self.bid, start)
        else:
            cookie = 'dbcl2="%s"; bid="%s"' % (self.dbcl2, self.bid)
        header = {"Cookie": cookie}
        
        conn.request('GET', "/j/mine/playlist?"+data, None, header)
        result = conn.getresponse().read()
        conn.close()
        
        return result

### playlist related

    def json_to_douban_tracks(self, item):
        return DoubanTrack(**item)
            
    def new_playlist(self, history=[]):
        """
        retrieve a new playlist
        * history -  history song ids. optional.
        """
        params = self.__get_default_params('n')
        params['h'] = self.__format_list(history, True)

        results = self.__remote_fm(params)

        return map(self.json_to_douban_tracks, json.loads(results)['song'])
                
    def del_song(self, sid, aid, rest=[]):
        """
        delete a song from your playlist
        * sid - song id
        * aid - album id
        * rest - rest song ids in current playlist
        """
        params = self.__get_default_params('b')
        params['sid'] = sid
        params['aid'] = aid
        params['rest'] = self.__format_list(rest)

        results = self.__remote_fm(params)
        return map(self.json_to_douban_tracks, json.loads(results)['song'])

    def fav_song(self, sid, aid):
        """
        mark a song as favorite
        * sid - song id
        * aid - album id
        """
        params = self.__get_default_params('r')
        params['sid'] = sid
        params['aid'] = aid

        self.__remote_fm(params)
        ## ignore the response

    def unfav_song(self, sid, aid):
        """
        unmark a favorite song
        * sid - song id
        * aid - album id
        """
        params = self.__get_default_params('u')
        params['sid'] = sid
        params['aid'] = aid

        self.__remote_fm(params)
    def skip_song(self, sid, aid, history=[]):
        """
        skip a song, tell douban that you have skipped the song.
        * sid - song id
        * aid - album id
        * history - your playlist history(played songs and skipped songs)
        """
        params = self.__get_default_params('s')
        params['h'] = self.__format_list(history[:70])
        params['sid'] = sid
        params['aid'] = aid
    
        results = self.__remote_fm(params)
        return map(self.json_to_douban_tracks, json.loads(results)['song'])

    def played_song(self, sid, aid, du=0):
        """
        tell douban that you have finished a song
        * sid - song id
        * aid - album id
        * du - time your have been idle
        """
        params  = self.__get_default_params('e')
        params['sid'] = sid
        params['aid'] = aid
        params['du'] = du

        self.__remote_fm(params)

    def played_list(self, sid, history=[]):
        """
        request more playlist items
        * history - your playlist history(played songs and skipped songs)
        """
        params = self.__get_default_params('p')
        params['h'] = self.__format_list(history[:50])
        params['sid'] = sid
        
        results = self.__remote_fm(params)
        return map(self.json_to_douban_tracks, json.loads(results)['song'])

#### recommand related
            
    def __parse_ck(self, content):
        """parse ck from recommend form"""
        prog = re.compile(r'name=\\"ck\\" value=\\"([\w\d]*?)\\"')
        finder = prog.search(content)
        if finder:
            return finder.group(1)
        return None
            
    def recommend(self, uid, comment, title=None, t=None, ck=None):
        """recommend a uid with some comment. ck is optional, if
        not provided, we will try to fetch a ck."""
        
        t = t or 'W'
        if ck is None:
        ## get recommend ck
            url = "http://www.douban.com/j/recommend?type=%s&uid=%s&rec=" % (t,uid)
            with contextlib.closing(httplib.HTTPConnection("music.douban.com")) as conn:
                cookie =  'dbcl2="%s"; bid="%s"; ' % (self.dbcl2, self.bid)
                conn.request('GET', url, None, {'Cookie': cookie})
                result = conn.getresponse().read()
                ck = self.__parse_ck(result)
                
        if ck:
            post = {'ck':ck, 'comment':comment, 'novote':1, 'type':t, 'uid':uid}
            if title:
                post['title'] = title
            
            ## convert unicode chars to bytes
            data = urllib.urlencode(post)
            ## ck ?
            cookie = 'dbcl2="%s"; bid="%s"; ck=%s' % (self.dbcl2, self.bid, ck)
            accept = 'application/json'
            content_type= 'application/x-www-form-urlencoded; charset=UTF-8'
            header = {"Cookie": cookie, "Accept": accept,
                    "Content-Type":content_type, }
                    
            with contextlib.closing(httplib.HTTPConnection("www.douban.com")) as conn:
                conn.request('POST', "/j/recommend", data, header)
                conn.getresponse().read()


