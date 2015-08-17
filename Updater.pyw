#-*- coding: utf-8 -*-

# MCModpackUpdater
# Version:1.1
# Author:panda_2134
# Licence:GNU GPL V2
# 2015/5/3

import tkinter
import tkinter.messagebox
import tkinter.ttk
import shutil
import os
import json
import threading
import time
import urllib
import locale
import logging

from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.error import URLError
from zipfile import *

#----------------------Language----------------------#
def langInit():
    currLangName=locale.getdefaultlocale()[0];
    langPath="./Updater/lang/";
    global currLang;
    glb={};
    #LanguageFile Exists
    if(os.path.exists(langPath+currLangName+'.py')):
        exec(open(langPath+currLangName+'.py',encoding='utf-8').read(),glb)
    else:
        exec(open(langPath+'en_US.py',encoding='utf-8').read(),glb)
    currLang=glb["lang"]

def loggerInit():
	global logger
	logger = logging.getLogger('MCModpackUpdater')
	hdlr = logging.FileHandler('./Updater/log.log')
	formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)

loggerInit()
langInit()

def getLangRegistry(name):
    return currLang[name]

def log(message,exc,Type="info"):
    if(Type=="info"):
        logger.info(message)
        tkinter.messagebox.showinfo(title=getLangRegistry("info"),message="%s\n%s"%(message,str(exc)))
    elif(Type=="err"):
        logger.error(message)
        tkinter.messagebox.showerror(title=getLangRegistry("error"),message="%s\n%s"%(message,str(exc)))
        exit()
    else:
        logger.debug(message)

def getLocalVersion():
    fileHndl=open("./Updater/version.json","r")
    lst=json.load(fileHndl)
    fileHndl.close()
    if(lst["version"]==0 and lst["desc"]==''):
        lst["desc"]=getLangRegistry("localVerError")
    return lst
def getLocalConfig():
    try:
        fileHndl=open("./Updater/config.json","r")
    except:
        log(message=getLangRegistry("configNeedsCorrect"),exc="",Type="err")
    lst=json.load(fileHndl)
    fileHndl.close()
    if(lst["remote-cfg"]=="http://example.com/example.json"):
        log(message=getLangRegistry("configNeedsCorrect"),exc="",Type="err")
    return lst
def getRemoteVersion():
    url=getLocalConfig()["remote-cfg"]
    try:
        cfg=urlopen(url).read().decode("gb2312")
    except URLError as e:
        log(message=getLangRegistry("remoteVerGetError"),exc=e,Type="err")
    return json.loads(cfg)
def setLocalVersion(lst):
    fileHndl=open("./Updater/version.json","w")
    s=json.dumps(lst)
    fileHndl.write(s)
    fileHndl.close()
def update(url):
    global infoString
    infoString.set("")
    global updateBtn
    updateBtn.destroy()
    global windowHndl
    pgPercent=tkinter.IntVar()
    pg=tkinter.ttk.Progressbar(windowHndl,variable=pgPercent)
    pg.pack()
    try:
        def report(count, blockSize, totalSize):
            percent = int(count*blockSize*100/totalSize)
            infoString.set(getLangRegistry("updatingInfo")%(percent))
            pgPercent.set(percent)
        urlretrieve(url, "Client.zip", reporthook=report)
    except URLError as e:
        infoString.set(getLangRegistry("downloadFailed"))
        log(getLangRegistry("downloadFailed"),e,"err")
    infoString.set(getLangRegistry("unzipping"))
    try:
        try:
            shutil.rmtree("./.minecraft")
        except:
            pass
        z=ZipFile("Client.zip","r")
        z.extractall()
    except BadZipFile as e:
        infoString.set(getLangRegistry("unzipFailed"))
        log(getLangRegistry("unzipFailed"),e,"error")
    remoteVer=getRemoteVersion()
    del remoteVer["url"]
    setLocalVersion(remoteVer)
    ver=getLocalVersion()["version"]
    desc=getLocalVersion()["desc"]
    infoString.set(getLangRegistry("updatedSuccessfully")%(float(ver),desc))
    updateBtn=tkinter.Button(windowHndl,text=getLangRegistry("chkUpdate"),command=chkUpdate,font=(getLangRegistry("fontSerif"),20))
    updateBtn.pack()
    pg.destroy()
    return

def chkUpdate():
    remoteVer=getRemoteVersion()
    localVer=getLocalVersion()
    if localVer["version"]<remoteVer["version"]:
        if (tkinter.messagebox.askyesno(getLangRegistry("updateFound"),getLangRegistry("updateFoundTip"))==True):
            threading.Thread(target=update,kwargs={"url":remoteVer["url"]}).start()
    else:
        tkinter.messagebox.showinfo(getLangRegistry("noUpdate"),getLangRegistry("noUpdateTip"))
    return



#init
windowHndl=tkinter.Tk()
windowHndl.geometry("500x400")
windowHndl.maxsize(500,400)
windowHndl.minsize(500,400)
windowHndl.wm_title(getLangRegistry("title"))
windowHndl.iconbitmap("./Updater/icon.ico")
mcImg=tkinter.PhotoImage(file="./Updater/icon.png")
imgLbl=tkinter.Label(image=mcImg)
imgLbl.image = mcImg # keep a reference!
imgLbl.pack()

#get ver & desc
ver=getLocalVersion()["version"]
desc=getLocalVersion()["desc"]
infoString=tkinter.StringVar(value=getLangRegistry("verInfo")%(float(ver),desc))
info=tkinter.Label(windowHndl,textvariable=infoString,font=("微软雅黑",20))
info.pack()
updateBtn=tkinter.Button(windowHndl,text=getLangRegistry("chkUpdate"),command=chkUpdate,font=(getLangRegistry("font"),20))
updateBtn.pack()
windowHndl.mainloop()
log(getLangRegistry("exitSuccessfully"),exc=None,Type="log")
