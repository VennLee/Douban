# -*- coding: utf-8 -*-
'''
Created on Sep 27, 2012
@author: Venn
'''

import pygst
pygst.require('0.10')
import gst

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import Image
from random import choice
import webbrowser



import gobject
import urllib
import ConfigParser
import os
import sys
import pango
import libdbfm
class Choose(gtk.Window):
        def __init__(self):
                self.ui_file=sys.path[0]+'/Setting.glade'
                self.wTree=gtk.glade.XML(self.ui_file,'MainWindow')
                self.mainWindow = self.wTree.get_widget("MainWindow")
                self.mainWindow.set_icon_from_file(sys.path[0]+'/Image/DBdialog.png')
                self.pane=self.wTree.get_widget('Hpaned')
                self.Color=self.wTree.get_widget('Color')
                self.Font=self.wTree.get_widget('Font')
                self.ChooseFlag=1
                self.ColorSelection=self.wTree.get_widget('ColorSelection')
                self.FontSelection=self.wTree.get_widget('FontSelection')
                self.fixed1=self.wTree.get_widget('Fixed1')
                self.fixed2=self.wTree.get_widget('Fixed2')
                self.OK=self.wTree.get_widget('OK')
                self.mainWindow.show_all()
                self.FontSelection.hide()
class DBfm(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.playlist = []
        self.cur = None
        self.user = ''
        self.pwd = ''
        self.fm = libdbfm.DoubanFM()
        self.config = ConfigParser.ConfigParser()
        self.likeFlag=0
    def loadConfig(self):
        try:
            self.config.read(sys.path[0]+'/config.ini')
            self.fm.loadConfig(self.config)
            return True
        except ConfigParser.NoSectionError,ConfigParser.NoOptionError:
            self.config.add_section('Cookie')
            self.config.add_section('UserInfo')
            self.config.set('Cookie', 'dbcl2',' ')
            self.config.set('UserInfo','uid',' ')
            self.config.set('UserInfo','channel','')
            #self.saveConfig()
            self.fm.saveConfig(self.config)
            return False
    def saveConfig(self):
        self.fm.saveConfig(self.config)
        self.config.write(open(sys.path[0]+'/config.ini','w'))

    def login(self,name,pwd):
        print 'Logining...'
        self.user = name
        self.pwd = pwd
        if not self.fm.login(name, pwd):
                print 'c1'
                return False
        print 'Login Finished!'
        self.next()
    def login2(self,name,pwd):
        print 'Logining2...'
        self.user = name
        self.pwd = pwd
        self.fm.login2(name, pwd)
        print 'Login Finished!'
        self.next()

    def __del__(self):
        print 'logout'
        del self.fm
        os.remove(sys.path[0]+'/config.ini')
    
    def played(self):
        self.fm.played_song(self.cur.props['sid'], self.cur.props['aid'])
        self.next()
    
    def next(self):
        if len(self.playlist)==0 :
            self.playlist = self.fm.new_playlist()
        self.cur = self.playlist.pop(0)
    
    def get_detail(self,param):
        return self.cur.props[param]
    
    def get_channels(self):
        return self.fm.channels

    def get_channel(self):
        return self.fm.get_channel()
    def set_channel(self,ch):
        self.fm.set_channel(ch)
        self.playlist = self.fm.new_playlist()
    def fav(self):
        if not self.isfav():
            self.likeFlag=1
            print '执行了 fav'
            self.fm.fav_song(self.get_detail('sid'), self.get_detail('aid'))
            self.cur.props['like']=1
    def unfav(self):
        if self.isfav():
            self.likeFlag=0
            print '执行了 unfav'
            self.fm.unfav_song(self.get_detail('sid'), self.get_detail('aid'))
            self.cur.props['like']=0            
    def isfav(self):
        if self.cur.props['like']==0:
            self.likeFlag=0
            return False
        else:
            self.likeFlag=1
            return True
    def del_song(self):
        self.fm.del_song(self.cur.props['sid'],self.cur.props['aid'])
class Channel(gtk.Window):
        def __init__(self):
                self.chList={}
                self.List1=[]
                self.List2=[]
                self.List3=[]
                self.flag=0#从0开始扫描到self.sum
                self.sum=0
                self.chan=0
                self.nextFlag=0
                self.ui_file=sys.path[0]+'/Chan.glade'
                self.wTree=gtk.glade.XML(self.ui_file,'MainWindow')
                self.mainWindow= self.wTree.get_widget("MainWindow")
                self.mainWindow.set_icon_from_file(sys.path[0]+'/Image/DBdialog.png')
                self.mainWindow.set_size_request(440,220)
                self.mainWindow.set_title("频道列表")
                self.mainWindow.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                self.mainWindow.modify_bg(
                        gtk.STATE_NORMAL,gtk.gdk.Color(10000,10000,10000))
                self.pane=self.wTree.get_widget('Hpaned')
                fix1=self.wTree.get_widget('fixed1')
                self.fix2=self.wTree.get_widget('fixed2')
                self.Personlabel=self.wTree.get_widget('personal')
                self.Publiclabel=self.wTree.get_widget('public')
                self.PersonButton=self.wTree.get_widget('Personal')
                self.PublicTable1=self.wTree.get_widget('Table1')
                self.PublicTable2=self.wTree.get_widget('Table2')
                self.PublicTable3=self.wTree.get_widget('Table3')
                self.Next=self.wTree.get_widget('Next')
                self.image_cnext=gtk.Image()
                self.image_cnext.set_from_pixbuf( gtk.gdk.pixbuf_new_from_file_at_size('Image/cnext.png',32,25))
                self.Next.set_image(self.image_cnext)               
                self.Prev=self.wTree.get_widget('Prev')
                self.image_prev=gtk.Image()
                self.image_prev.set_from_pixbuf( gtk.gdk.pixbuf_new_from_file_at_size('Image/cprev.png',32,25))
                self.Prev.set_image(self.image_prev)
                self.Next.set_relief(gtk.RELIEF_NONE)
                self.Next.set_focus_on_click(False)
                self.Prev.set_relief(gtk.RELIEF_NONE)
                self.Prev.set_focus_on_click(False)
                self.Personal=self.wTree.get_widget('Person')
                self.Liked=self.wTree.get_widget('Liked')
                self.attr3=pango.AttrList()
                font_des=pango.FontDescription('Microsoft Yahei')
                font=pango.AttrFontDesc(font_des,0,-1)
                size=pango.AttrSize(11000,0,-1)
                color=pango.AttrForeground(65405,65405,65405,0,-1)          
                self.attr3.insert(size)
                self.attr3.insert(color)
                self.attr3.insert(font)
                self.Personlabel.set_attributes(self.attr3)
                self.Publiclabel.set_attributes(self.attr3)
class MainForm(object):
    '''
    classdocs
    '''
    def __init__(self):
        #setup UI
        #self.gladefile = sys.path[0]+"/dbfm.glade"
        '''self.wTree = gtk.glade.XML(self.gladefile,"mainWindow")
        '''
        self.player = gst.element_factory_make("playbin", "player")
        bus = self.player.get_bus()
        self.player.set_property('volume',1)
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        #setup douban fm
        self.dbfm = DBfm()
        ##Flags登陆标志和暂停标志
        self.pauseFlag=1##1表示播放
        self.loginFlag=0
        self.Chan=Channel()#创建了一个窗口来选台
        self.Chan.chList=self.dbfm.get_channels()
        self.List=[]
        for key in self.Chan.chList.keys():
                self.List.append(key)
        self.ch=choice(self.List)
        self.chname=self.ch
        self.More(self.Chan)
        self.chid=self.Chan.chList[self.ch]
        
        self.ui_file=sys.path[0]+'/dbfm.glade'
        self.wTree=gtk.glade.XML(self.ui_file,'mainWindow')

        dic = { "on_mainWindow_destroy_event" : self.destroy,
               "on_mainWindow_delete_event" : self.delete_event,
               "on_loginWindowButton_clicked" : self.loginWindowButton_clicked
               }

        self.wTree.signal_autoconnect(dic)
        ###控制按钮
        self.pauseButton = self.wTree.get_widget("pauseButton")
        self.pauseButton1=self.wTree.get_widget('pauseButto')
        
            ####下一首按钮
        self.nextButton=self.wTree.get_widget('nextButton')
        self.nextButton.connect('clicked',self.nextButton_clicked)
        self.nextButton.set_relief(gtk.RELIEF_NONE)
        self.nextButton.set_focus_on_click(False)
        self.nextButton.connect('enter',self.nextButton_enter)
        self.nextButton.connect('leave',self.nextButton_leave)
        self.image_next=gtk.Image()
        self.image_next.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/Next.png',40,40))
        self.image_onnext=gtk.Image()
        self.image_onnext.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/onNext.png',40,40))
        self.nextButton.set_image(self.image_next)        
        
                  ###新添加的按钮
                   ####删除按钮
        self.delButton=self.wTree.get_widget('delButton')
        self.delButton.connect('clicked',self.on_del)
        self.delButton.set_relief(gtk.RELIEF_NONE)
        self.delButton.set_focus_on_click(False)
        self.image_disabled=gtk.Image()
        self.image_disabled.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/Disabled.png',40,40))
        self.image_never=gtk.Image()
        self.image_never.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/Never.png',40,40))
        
        self.delBtnState(self.delButton)
        self.delButton.connect('enter',self.enter_del)
        self.delButton.connect('leave',self.leave_del)
        
                   ####暂停按钮
        self.pauseButton1=self.wTree.get_widget('pauseButto')
        self.pauseButton1.set_relief(gtk.RELIEF_NONE)
        self.pauseButton1.set_focus_on_click(False)
        self.pauseButton1.connect('clicked',self.on_pause)
        self.pauseButton1.connect('enter',self.enter_pause)
        self.pauseButton1.connect('leave',self.leave_pause)
        self.image_pause=gtk.Image()
        self.image_pause.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/Pause.png',40,40))
        self.image_play=gtk.Image()
        self.image_play.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/Play.png',40,40))
        self.image_onpause=gtk.Image()
        self.image_onpause.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/onPause.png',40,40))
        self.image_onplay=gtk.Image()
        self.image_onplay.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size('Image/onPlay.png',40,40))
        
        self.pausebtn_image(self.pauseButton1)
              
                    ####like按钮
        self.likeButton=self.wTree.get_widget('likeButton')
        self.likeButton.set_relief(gtk.RELIEF_NONE)
        self.likeButton.set_focus_on_click(False)
        self.likeButton.connect('clicked',self.on_like)
        self.likeButton.connect('enter',self.enter_like)
        self.likeButton.connect('leave',self.leave_like)
        self.image_like=gtk.Image()
        self.image_like.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Like.png',40,40))
        self.image_unlike=gtk.Image()
        self.image_unlike.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Unlike.png',40,40))
        self.image_onlike=gtk.Image()
        self.image_onlike.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/on_like.png',40,40))
        self.leave_like(self.likeButton)
        #######search按钮        
        self.searchButton=self.wTree.get_widget('search')
        self.searchButton.connect('clicked',self.on_search)
        self.searchButton.set_relief(gtk.RELIEF_NONE)
        self.searchButton.set_focus_on_click(False)
        self.image_search=gtk.Image()
        self.image_search.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/search.png',20,20))
        self.searchButton.set_image(self.image_search)
        ######菜单按钮
        self.Menu=self.wTree.get_widget('Menu')
        self.Menu.set_tooltip_text('菜单')
        self.Login=self.wTree.get_widget('Login')
        self.Login.set_tooltip_text('登陆')
        self.Login.connect('clicked',self.on_Login)
        self.Channel=self.wTree.get_widget('Channel')
        self.Channel.set_tooltip_text('选择频道')
        self.Setting=self.wTree.get_widget('Settings')
        self.Setting.set_tooltip_text('设置')
        self.About=self.wTree.get_widget('About')
        self.About.set_tooltip_text('关于')
                    #菜单按钮
        self.MenuFlag=1
        self.image_Menu=gtk.Image()
        self.image_Menu.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Menu.png',28,28))
        self.Menu.set_focus_on_click(False)        
        self.Menu.set_relief(gtk.RELIEF_NONE)
        self.Menu.set_image(self.image_Menu)
        self.Menu.connect('clicked',self.on_Menu)
        
               ###频道按钮
        self.image_Channel=gtk.Image()
        self.image_Channel.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Channel.png',28,28))
        self.Channel.set_focus_on_click(False)        
        self.Channel.set_relief(gtk.RELIEF_NONE)
        self.Channel.set_image(self.image_Channel)
        self.Channel.connect('clicked',self.on_Channel)
             ###设置按钮
        self.image_Setting=gtk.Image()
        self.image_Setting.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Setting.png',28,28))
        self.Setting.set_focus_on_click(False)        
        self.Setting.set_relief(gtk.RELIEF_NONE)
        self.Setting.set_image(self.image_Setting)
        self.Setting.connect('clicked',self.on_Setting)
        
                  #####关于按钮
        self.image_About=gtk.Image()
        self.image_About.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/About.png',28,28))
        self.About.set_relief(gtk.RELIEF_NONE)
        self.About.set_focus_on_click(False)
        self.About.set_image(self.image_About)
        self.About.connect('clicked',self.on_About)        
        #封面
        self.photo = self.wTree.get_widget("photo")
        self.image=gtk.gdk.pixbuf_new_from_file_at_size(sys.path[0]+'/Image/default.png',280,280)
        self.photo.set_from_pixbuf(self.image)
        #歌曲信息
        self.songDetail = self.wTree.get_widget("songDetail")
        self.songDetail.set_text("豆瓣电台")
        self.songDetail.set_justify(gtk.JUSTIFY_LEFT)
        self.songDetail2=self.wTree.get_widget("songDetail2")
        self.songChan=self.wTree.get_widget('channel')
        self.songChan.set_text(self.chname)
        #进度条
        self.playProgress = self.wTree.get_widget('PlayProgress')
        ########歌曲信息###
        attr=pango.AttrList()
        font_des=pango.FontDescription('Microsoft Yahei')
        font=pango.AttrFontDesc(font_des,0,-1)
        size=pango.AttrSize(24000,0,-1)
        color=pango.AttrForeground(65405,65405,65405,0,-1)          
        attr.insert(size)
        attr.insert(color)
        attr.insert(font)
        self.songDetail.set_attributes(attr)
        attr2=pango.AttrList()
        font_des=pango.FontDescription('Sans')
        font=pango.AttrFontDesc(font_des,0,-1)
        size=pango.AttrSize(13000,0,-1)
        color=pango.AttrForeground(65405,65405,65405,0,-1)          
        attr2.insert(size)
        attr2.insert(color)
        attr2.insert(font)
        self.songDetail2.set_attributes(attr2)

        attr3=pango.AttrList()
        font_des=pango.FontDescription('Microsoft Yahei')
        font=pango.AttrFontDesc(font_des,0,-1)
        size=pango.AttrSize(14000,0,-1)
        color=pango.AttrForeground(65405,65405,65405,0,-1)          
        attr3.insert(size)
        attr3.insert(color)
        attr3.insert(font)
        self.songChan.set_attributes(attr3)
        #####################
        self.mainWindow = self.wTree.get_widget("mainWindow")
        self.mainWindow.set_title('豆瓣FM')
        self.mainWindow.set_icon_from_file(sys.path[0]+'/Image/Douban.png')
        self.layout=self.wTree.get_widget("layout1")
        self.layout.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(0,12220,0))        
        self.channelList = self.wTree.get_widget('channelList')
        ####控制播放器音量
        self.volumeScale=gtk.HScale()
        Ad= gtk.Adjustment(2, 0,6,1,1,0)
        self.volumeScale.set_adjustment(Ad)
        self.volumeScale.set_size_request(70,10)       
        self.volumeScale.connect('value-changed',self.on_changed)
        self.volumeScale.set_property('can-focus',False)
        self.volumeScale.set_property('draw-value',False)
        self.layout.put(self.volumeScale,460,160)
        self.volBtn=self.wTree.get_widget('volBtn')
        self.volFlag=0
        self.volBtn.connect('clicked',self.volScaleshow)
        self.volBtn.connect('enter',self.volScalehide)
        self.image_volume=gtk.Image()
        self.image_volume.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/volume.png',20,20))
        self.volBtn.set_image(self.image_volume)
        self.volBtn.set_relief(gtk.RELIEF_NONE)
        self.volBtn.set_focus_on_click(False)
        ####时间
        self.passTimeLabel=self.wTree.get_widget('passTime')
        self.totalTimeLabel=self.wTree.get_widget('totalTime')
        self.attr3=pango.AttrList()
        font_des=pango.FontDescription('Sans')
        font=pango.AttrFontDesc(font_des,0,-1)
        size=pango.AttrSize(11000,0,-1)
        color=pango.AttrForeground(65405,65405,65405,0,-1)          
        self.attr3.insert(size)
        self.attr3.insert(color)
        self.attr3.insert(font)
        self.passTimeLabel.set_attributes(self.attr3)
        self.totalTimeLabel.set_attributes(self.attr3)
        # setup system tray              
        self.mainWindow.show_all()
        self.volumeScale.hide()
        self.Login.hide()
        self.Channel.hide()
        self.Setting.hide()
        self.About.hide()
        
        self.systray=None     
        #set processbar timer
        self.timer = None
        if self.dbfm.loadConfig():
            self.loginFlag=1
            self.delButton.set_sensitive(True)
            self.delBtnState(self.delButton)
            self.dbfm.set_channel(self.chid)
            self.get_next_song()
            self.play()
        else:                
            self.dbfm.set_channel(self.chid)
        #登陆按钮
        self.image_Login=gtk.Image()
        self.image_Login.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Login.png',28,28))
        self.image_Logout=gtk.Image()
        self.image_Logout.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('Image/Logout.png',28,28))
        self.Login.set_focus_on_click(False)        
        self.Login.set_relief(gtk.RELIEF_NONE)
        if self.loginFlag==1:
                self.Login.set_image(self.image_Logout)
        else:
                self.Login.set_image(self.image_Login)
        self.Login.connect('enter',self.enter_Login)
        #setup player
##############################################
##############Channel
            ####频道频道频道频道#######################################3
            ##########频道
    def More(self,chan):
                for key in chan.chList.keys():
                        if chan.sum<=11:
                                chan.List1.append(key)
                        if chan.sum>=12 and chan.sum<24:
                                chan.List2.append(key)
                        if chan.sum>=24:
                                chan.List3.append(key)
                        chan.sum+=1
                self.insertButton(self.Chan.PublicTable1)
                self.insertButton(self.Chan.PublicTable2)
                self.insertButton(self.Chan.PublicTable3)
                self.Chan.Next.connect('clicked',self.on_cnext)
                self.Chan.Prev.connect('clicked',self.on_prev)
                self.Chan.Personal.connect('clicked',self.on_Personal)
                self.Chan.Liked.connect('clicked',self.on_Liked)
    def Show(self):
                self.Chan.mainWindow.show_all()                
                self.Chan.nextFlag=0
                self.comman()
    def insertButton(self,widget):
            for j in range(3):
                      for i in range(4):

                            if self.Chan.flag<=11:
                                try:
                                    button=gtk.Button(str(self.Chan.List1[self.Chan.flag]))
                                except:
                                    pass
                            elif self.Chan.flag>=12 and self.Chan.flag<24:
                                try:
                                    button=gtk.Button(str(self.Chan.List2[self.Chan.flag-12]))
                                except:
                                    pass
                            elif self.Chan.flag>=24 and self.Chan.flag<self.Chan.sum:
                                try:
                                    button=gtk.Button(str(self.Chan.List3[self.Chan.flag-24]))
                                except:
                                    pass
                            else:
                                pass
                            button.connect('clicked',self.on_Button)
                            self.Chan.flag+=1   
                            if self.Chan.flag<=self.Chan.sum:
                                  widget.attach(button,i,i+1,j,j+1)
                            else:
                                    pass
    def on_cnext(self,widget):
                self.Chan.nextFlag+=1
                self.comman()
    def on_prev(self,widget):
                self.Chan.nextFlag-=1   
                self.comman()                            
    def comman(self):
                print self.Chan.nextFlag
                if self.Chan.nextFlag==0:
                        self.Chan.PublicTable2.hide()
                        self.Chan.PublicTable3.hide()
                        self.Chan.PublicTable1.show()
                        self.Chan.Prev.set_sensitive(False)
                        self.Chan.Next.set_sensitive(True)
                if self.Chan.nextFlag==1:
                        self.Chan.PublicTable1.hide()
                        self.Chan.PublicTable3.hide()
                        self.Chan.PublicTable2.show()
                        self.Chan.Prev.set_sensitive(True)
                        self.Chan.Next.set_sensitive(True)
                if self.Chan.nextFlag==2:
                        self.Chan.PublicTable3.show()
                        self.Chan.PublicTable1.hide()
                        self.Chan.PublicTable2.hide()
                        self.Chan.Prev.set_sensitive(True)
                        self.Chan.Next.set_sensitive(False)
    def on_search(self,widget):
            try:
                    print 'search'
                    url='http://music.douban.com'
                    album=self.dbfm.get_detail('album')
                    url+=album
                    print url
                    webbrowser.open(url)
            except Exception:
                    pass
                        
    def on_Button(self,widget):
                self.songChan.set_text(unicode(widget.get_label()))
                self.dbfm.set_channel((self.Chan.chList[unicode(widget.get_label())]))
                self.get_next_song()
                self.play()
    def on_Personal(self,widget):
                 self.songChan.set_text('私人频道')
                 self.dbfm.set_channel(0)
                 self.get_next_song()
                 self.play()
    def on_Liked(self,widget):
               self.songChan.set_text('红心频道')
               self.dbfm.set_channel(-3)
               self.get_next_song()
               self.play()
               
    def on_Channel(self,widget):
        self.Chan=Channel()#创建了一个窗口来选台
        self.Chan.mainWindow.set_transient_for(self.mainWindow)
        self.Chan.mainWindow.set_destroy_with_parent(True)
        self.Chan.mainWindow.set_modal(True)
        if self.loginFlag==0:
                self.Chan.Personal.set_sensitive(False)
                self.Chan.Liked.set_sensitive(False)
        self.Chan.chList=self.dbfm.get_channels()
        self.More(self.Chan)
        self.Show()
        self.MenuFlag=1
        self.Login.hide()
        self.Channel.hide()
        self.Setting.hide()
        self.About.hide()
    ############################setting
    def on_Setting(self,widget):
        self.MenuFlag=1        
        self.Settingdialog=Choose()
        self.Settingdialog.ChooseFlag=1        
        self.Settingdialog.Color.connect('clicked',self.on_Color)
        self.Settingdialog.OK.connect('clicked',self.on_OK)
        self.font=self.Settingdialog.Font.connect('clicked',self.on_Font)
        self.Login.hide()
        self.Channel.hide()
        self.Setting.hide()
        self.About.hide()

    def on_Font(self,widget):
                self.Settingdialog.ChooseFlag=0
                print 'is 0'
                self.Settingdialog.ColorSelection.hide()
                self.Settingdialog.FontSelection.show()
    def on_Color(self,widget):
                print 'is 1'
                self.Settingdialog.ChooseFlag=1
                self.Settingdialog.FontSelection.hide()
                self.Settingdialog.ColorSelection.show()
    def on_OK(self,widget):
                print self.Settingdialog.ChooseFlag
                if self.Settingdialog.ChooseFlag==1:
                       self.layout.modify_bg(gtk.STATE_NORMAL,self.Settingdialog.ColorSelection.get_current_color())
                else:
                    Font=(self.Settingdialog.FontSelection.get_font_name(),self.Settingdialog.FontSelection.get_size())
                    print Font
                    attr=pango.AttrList()
                    font_des=pango.FontDescription(Font[0])
                    font=pango.AttrFontDesc(font_des,0,-1)
                    size=pango.AttrSize(24000,0,-1)
                    color=pango.AttrForeground(65405,65405,65405,0,-1)          
                    attr.insert(size)
                    attr.insert(color)
                    attr.insert(font)
                    self.songDetail.set_attributes(attr)
#########################        
    def on_Menu(self,widget):
        if self.MenuFlag==1:
            self.MenuFlag=0
            self.Login.show()
            self.Channel.show()
            self.Setting.show()
            self.About.show()
        else:
            self.MenuFlag=1
            self.Login.hide()
            self.Channel.hide()
            self.Setting.hide()
            self.About.hide()
            
    def enter_Login(self,widget):
         if self.loginFlag==0:
                self.Login.set_tooltip_text('登陆')
         else:
                self.Login.set_tooltip_text('离开')
    def  on_Login(self,widget):
        widget.hide()
        self.MenuFlag=1
        self.Channel.hide()
        self.Setting.hide()
        self.About.hide()
        if self.loginFlag==0:#登陆
            if self.dbfm.fm.get_image():#有图片
                self.login2(widget)
            else:
                self.login(widget)
        else:
            print 'logout'
            self.player.set_state(gst.STATE_NULL)
            self.loginFlag=0
            self.delBtnState(self.delButton)
            self.delButton.set_sensitive(False)
            del self.dbfm
            self.Login.set_image(self.image_Login)#如果退出，相对简单            
            self.dbfm=DBfm()
            self.pauseFlag=1
            self.pausebtn_image(self.pauseButton1)
            self.ch=choice(self.List)
            self.songChan.set_text(self.ch)
            self.dbfm.set_channel(self.dbfm.get_channels()[self.ch])
            self.get_next_song()
            self.play()
    def on_About(self,widget):
        self.MenuFlag=1
        widget.hide()
        self.Channel.hide()
        self.Setting.hide()
        self.Login.hide()
        about=gtk.AboutDialog()
        about.set_transient_for(self.mainWindow)
        about.set_destroy_with_parent(True)
        about.set_modal(True)
        about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        about.set_icon_from_file(sys.path[0]+'/Image/DBdialog.png')
        about.set_program_name('DouBan.FM')
        about.set_position(gtk.WIN_POS_CENTER)
        about.set_version('1.0')
        about.set_copyright('Copyright ©2012-2013 VennLee')
        about.set_comments('此为豆瓣电台第三方软件,电台版权归豆瓣网所有')
        about.set_website('http://www.douban.fm/')
        about.set_authors(['李文强'])
        about.set_logo(gtk.gdk.pixbuf_new_from_file(sys.path[0]+'/Image/DBlogo.png'))
        about.run()
        about.destroy()
            
    def volScaleshow(self,widget):
        self.volumeScale.show()
    def volScalehide(self,widget):
        self.volumeScale.hide()
    def convert(self,length):
        minute=length/60
        second=length%60
        if minute<10:
            x='0'+str(minute)
        else:
            x=str(minute)
        if second<10:
            y='0'+str(second)
        else:
            y=str(second)
        timestr=x+':'+y
        return timestr
    def likebtn_image(self,widget):
        if self.dbfm.likeFlag==1:
            widget.set_image(self.image_like)
        else:
            widget.set_image(self.image_unlike)
    def enter_like(self,widget):
        widget.set_image(self.image_onlike)
        if self.dbfm.likeFlag==0:
            widget.set_tooltip_text('喜欢')
        else:
            widget.set_tooltip_text('取消喜欢')
    def leave_like(self,widget):
        self.likebtn_image(widget)
    def on_like(self,widget):
         if self.dbfm.likeFlag==0:
             self.dbfm.fav()            
         else:
             self.dbfm.unfav()
            
    def delBtnState(self,widget):
            if self.loginFlag==0:
                widget.set_sensitive(False)
                widget.set_image(self.image_disabled)
                self.enter_del(self.delButton)
            else:
                widget.set_image(self.image_never)
    def enter_del(self,widget):
        print  self.loginFlag
        if self.loginFlag==0:
            widget.set_tooltip_text('登陆后可用')
        else:
            widget.set_image(self.image_disabled)
            widget.set_tooltip_text('不再播放')
    def leave_del(self,widget):
        widget.set_image(self.image_never)
    def on_del(self,widget):
        print 'Del this song'
        self.dbfm.del_song()
        self.get_next_song()
        self.play()
    def on_changed(self,widget):
          val=widget.get_value()
          print val
          self.player.set_property('volume',val)
          
    def delete_event(self,widget,data=None):
        self.mainWindow.hide()
        return True
    def destroy(self,widget,data=None):
        self.dbfm.saveConfig()
        gtk.main_quit()

    def loginWindowButton_clicked(self, widget):
        if self.dbfm.fm.get_image():
            self.login(widget)
        else:
            self.login2(widget)
        
    def login(self,widget):#没有图片
        self.loginDialog= gtk.Dialog("登陆到豆瓣",self.mainWindow,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.loginDialog.set_size_request(270,200)
        self.loginDialog.set_icon_from_file(sys.path[0]+'/Image/DBdialog.png')
        
        self.LabelAlert=gtk.Label()
        attr=pango.AttrList()
        color=pango.AttrForeground(65405,0,0,0,-1)          
        attr.insert(color)
        self.LabelAlert.set_attributes(attr)
        
        fixed = gtk.Fixed()
        fixed.put(self.LabelAlert,5,125)
        self.loginDialog.vbox.pack_start(fixed)
        label1 = gtk.Label(u'用户名/邮箱')
        fixed.put(label1,5,10)
        userNameEntry = gtk.Entry()
        fixed.put(userNameEntry,5,30)
        label2 = gtk.Label(u'密码')
        fixed.put(label2,5,60)
        passwordEntry = gtk.Entry()
        passwordEntry.set_visibility(False) #密码不可见
        fixed.put(passwordEntry,5,80)        
        self.loginDialog.show_all()
        while True:
          response = self.loginDialog.run()
          if response == gtk.RESPONSE_ACCEPT:
              if userNameEntry.get_text() is '':
                  self.LabelAlert.set_text('提示:用户名不能为空\n请重新登陆！')
                  self.loginDialog.show_all()
              elif passwordEntry.get_text() is '':
                  self.LabelAlert.set_text('提示:密码不能为空\n请重新登陆！')
                  self.loginDialog.show_all()            
              else:
                  self.dbfm.login(userNameEntry.get_text(),passwordEntry.get_text())
                  if self.dbfm.fm.LoginFlag==0:
                          print '登录失败'
                          self.LabelAlert.set_text('提示:账号或密码错误,请重试!')
                  else:
                          self.loginDialog.destroy()
                          print '登录成功'
                          self.delButton.set_sensitive(True)
                          self.loginFlag=1
                          self.delButton.set_image(self.image_never)
                          self.Login.set_image(self.image_Logout)
                          self.prepare_channelList()
                          self.dbfm.set_channel(0)
                          self.pauseFlag=1
                          self.get_next_song()
                          self.play()                          
                          self.dbfm.saveConfig()
                          break
          else:
            self.loginDialog.destroy()
            break
    def login2(self,widget):#有图片
        print 'loginWindowButton2_clicked'
        self.loginDialog = gtk.Dialog("登陆到豆瓣",
                self.mainWindow,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.loginDialog.set_size_request(270,195)
        self.loginDialog.set_icon_from_file(sys.path[0]+'/Image/DBdialog.png')
        
        self.LabelAlert=gtk.Label()
        attr=pango.AttrList()
        color=pango.AttrForeground(65405,0,0,0,-1)          
        attr.insert(color)
        self.LabelAlert.set_attributes(attr)
        fixed = gtk.Fixed()
        fixed.put(self.LabelAlert,5,135)
        self.loginDialog.vbox.pack_start(fixed)
        
        label1 = gtk.Label(u'用户名/邮箱')
        fixed.put(label1,5,10)
        userNameEntry = gtk.Entry()
        fixed.put(userNameEntry,75,5)
        label2 = gtk.Label(u'密   码')
        fixed.put(label2,5,40)
        passwordEntry = gtk.Entry()
        passwordEntry.set_visibility(False) #密码不可见
        fixed.put(passwordEntry,75,35)
        label3=gtk.Label(u'验证码')
        fixed.put(label3,5,70)
        IDEntry=gtk.Entry()
        fixed.put(IDEntry,75,65)        
        IDimage=gtk.Image()
        IDpix=gtk.gdk.pixbuf_new_from_file_at_size(sys.path[0]+'/Image/IDimg.jpg',200,32)
        IDimage.set_from_pixbuf(IDpix)
        fixed.put(IDimage,15,100)        
        self.loginDialog.show_all()
        while True:
          response = self.loginDialog.run()
          if response == gtk.RESPONSE_ACCEPT:
              if userNameEntry.get_text() is '':
                  self.LabelAlert.set_text('提示:用户名不能为空,请重新登陆！')                  
                  self.loginDialog.show_all()
              elif passwordEntry.get_text() is '':
                  self.LabelAlert.set_text('提示:密码不能为空,请重新登陆！')
                  self.loginDialog.show_all()
              elif IDEntry.get_text() is '':
                  self.LabelAlert.set_text('提示:验证码不能为空')
              else:
                  self.dbfm.fm.vcode=IDEntry.get_text()#验证码输入
                  self.dbfm.login2(userNameEntry.get_text(),passwordEntry.get_text())
                  if  self.dbfm.fm.LoginFlag==0:
                          print '登录失败'
                          self.LabelAlert.set_text('提示:账号或密码错误,请重试!')
                  else:
                          self.loginDialog.destroy()
                          self.LabelAlert.set_text("登录成功")
                          self.delButton.set_sensitive(True)
                          self.loginFlag=1
                          self.delButton.set_image(self.image_never)
                          self.prepare_channelList()
                          self.Login.set_image(self.image_Logout)
                          #self.channelList.set_active(self.dbfm.get_channel())
                          self.dbfm.set_channel(0)
                          self.pauseFlag=1
                          self.get_next_song()
                          self.play()                          
                          os.remove(sys.path[0]+"/Image/IDimg.jpg")
                          self.dbfm.saveConfig()
                          break
          else:
            self.loginDialog.destroy()
            break            
    def logoutButton_clicked(self,widget):
        print 'logout'
        self.player.set_state(gst.STATE_NULL)
        self.loginFlag=0
        self.delBtnState(self.delButton)
        self.delButton.set_sensitive(False)
        del self.dbfm        
        self.dbfm=DBfm()
        self.dbfm.loadConfig()
        self.pauseFlag=1
        self.pausebtn_image(self.pauseButton1)
        if self.songChan.get_text() is u'红心频道' or self.songChan.get_text()=='私人频道':
                self.songChan.set_text('新歌')
                self.dbfm.set_channel(61)
        
        self.get_next_song()
        self.play()
        
    def pausebtn_image(self,widget):
        if self.pauseFlag==1:
            widget.set_image(self.image_pause)
        else:
            widget.set_image(self.image_play)
    def enter_pause(self,widget):
        print self.pauseFlag
        if self.pauseFlag==1:
            widget.set_image(self.image_onpause)
            widget.set_tooltip_text('暂停')
        else:
            widget.set_image(self.image_onplay)
            widget.set_tooltip_text('播放')
    def leave_pause(self,widget):
        self.pausebtn_image(self.pauseButton1)
    def on_pause(self,widget):
        print '暂停按钮按了一下'
        if self.pauseFlag==1:
            print  "暂停"
            self.player.set_state(gst.STATE_PAUSED)
            self.pauseFlag=0
            widget.set_image(self.image_play)
        else:
            print '播放'
            self.player.set_state(gst.STATE_PLAYING)
            self.pauseFlag=1
            widget.set_image(self.image_pause)

    def nextButton_clicked(self,widget):
        self.get_next_song()
        self.leave_like(self.likeButton)
        self.play()
    def nextButton_enter(self,widget):
        widget.set_image(self.image_onnext)
        widget.set_tooltip_text('下一首')
    def nextButton_leave(self,widget):
        widget.set_image(self.image_next)
        
    def hasmpic(self,url):        
        for i in range(0,len(url)-4):
                if url[i]=='m' and url[i+1]=='p' and url[i+2]=='i' and url[i+3]=='c':
                        return True
        return False
    def changeurl(self,url):
        newurl=''
        for i in range(0,len(url)):
            if i!=23:
                newurl+=url[i]
            else:
                newurl+='l'
        return newurl
    def cutImage(self,imgpath):
        im = Image.open(imgpath)
        mini=min(im.size[0],im.size[1])
        album= im.crop((0,0,mini,mini))
        album.save(sys.path[0]+'/Image/Album.jpg')
    def get_next_song(self):
        self.player.set_state(gst.STATE_NULL)
        self.dbfm.next()
        print  self.dbfm.get_detail('album')
        self.player.set_property('uri', self.dbfm.get_detail('url'))
        self.songDetail.set_text("%s" % ( (self.dbfm.get_detail('title'))))
        self.songDetail2.set_text ("%s\n%s" % (self.dbfm.get_detail('albumtitle'),self.dbfm.get_detail('artist')))
        imgurl=self.dbfm.get_detail('picture')
        print imgurl
        if self.hasmpic(imgurl):
            imgurl=self.changeurl(imgurl)
        urllib.urlretrieve(imgurl,sys.path[0]+"/Image/picture.jpg")
        self.cutImage(sys.path[0]+"/Image/picture.jpg")
        os.remove(sys.path[0]+"/Image/picture.jpg")
        FF=gtk.gdk.pixbuf_new_from_file_at_size(sys.path[0]+'/Image/Album.jpg',280,280)        
        self.photo.set_from_pixbuf(FF)
        self.pauseFlag=1
        self.dbfm.likeFlag=self.dbfm.get_detail('like')
        self.leave_like(self.likeButton)
        self.pausebtn_image(self.pauseButton1)

    def play(self):
        self.player.set_state(gst.STATE_PLAYING)
        length=self.dbfm.get_detail('length')
        if type(length) is int:
            self.totalTimeLabel.set_text(self.convert(length))
            self.countlength=-1
        if self.timer:
              gtk.timeout_remove(self.timer)
        self.playProgress.set_fraction(0.0)
        print self.dbfm.get_detail('length')
        self.timer = gtk.timeout_add (1000,self.on_timeout,self.dbfm.get_detail('length'))
    def hide(self,window):
           self.mainWindow.hide()
           return False              
    
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.get_next_song()
            self.play()
        elif t == gst.MESSAGE_EOS:
            self.dbfm.played()
            self.get_next_song()
            self.likebtn_image(self.likeButton)
            self.play()



    def prepare_channelList(self):
        chs = self.dbfm.get_channels()
## Update the value of the progress bar so that we get
## some movement
    def on_timeout(self, length):
        """
        Update value on the progress bar
        """
        increase=1/float(length)
        if self.pauseFlag==0:
            pass
        else:
            self.countlength+=1
        self.passTimeLabel.set_text(self.convert(self.countlength))
        new_value = self.playProgress.get_fraction()+increase
        if new_value <=1:
            self.playProgress.set_fraction(new_value)
            return True
        else:
            return False
