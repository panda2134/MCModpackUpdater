# MCModpackUpdater
# Version:0.2
# Author:panda_2134
# Licence:GNU GPL V2
# 2015/5/3

import tkinter
import tkinter.messagebox
import tkinter.ttk
import shutil
import json
import threading
import time
import urllib
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.error import URLError
from zipfile import *

def log(message,exc,Type="info"):
    f=open("./Updater/log.log","a")
    if(Type=="info"):
        s="[INFO %s]%s"%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),message)
        tkinter.messagebox.showinfo(title="消息",message="%s\n%s"%(message,str(exc)))
        print(s,file=f)
        print(s)
        f.close()
    elif(Type=="err"):
        s="[ERROR %s]%s %s"%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),message,str(exc))
        tkinter.messagebox.showerror(title="错误",message="%s\n%s"%(message,str(exc)))
        print(s,file=f)
        print(s)
        f.close()
        exit()
    else:
        s="[LOG %s]%s"%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),message)
        print(s,file=f)
        print(s)
        f.close()
def getLocalVersion():
    fileHndl=open("./Updater/version.json","r")
    lst=json.load(fileHndl)
    fileHndl.close()
    return lst
def getLocalConfig():
    try:
        fileHndl=open("./Updater/config.json","r")
    except:
        log(message="请正确填写配置文件",exc="",Type="err")
    lst=json.load(fileHndl)
    fileHndl.close()
    if(lst["remote-cfg"]=="http://example.com/example.zip"):
        log(message="请正确填写配置文件",exc="",Type="err")
    return lst
def getRemoteVersion():
    url=getLocalConfig()["remote-cfg"]
    try:
        cfg=urlopen(url).read().decode("gb2312")
    except URLError as e:
        log(message="远端版本获取失败",exc=e,Type="err")
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
            infoString.set("更新中...\n已下载%d%%"%(percent))
            pgPercent.set(percent)
        urlretrieve(url, "Client.zip", reporthook=report)
    except URLError as e:
        infoString.set("下载失败")
        log("下载失败",e,"err")
    infoString.set("下载完成 解压中...")
    try:
        try:
            shutil.rmtree("./.minecraft")
        except:
            pass
        z=ZipFile("Client.zip","r")
        z.extractall()
    except BadZipFile as e:
        infoString.set("解压失败")
        log("解压失败",e,"error")
    remoteVer=getRemoteVersion()
    del remoteVer["url"]
    setLocalVersion(remoteVer)
    ver=getLocalVersion()["version"]
    desc=getLocalVersion()["desc"]
    infoString.set("更新成功\n版本：%.2f\n%s"%(float(ver),desc))
    updateBtn=tkinter.Button(windowHndl,text="检查更新",command=chkUpdate,font=("宋体",20))
    updateBtn.pack()
    pg.destroy()
    return

def chkUpdate():
    remoteVer=getRemoteVersion()
    localVer=getLocalVersion()
    if localVer["version"]<remoteVer["version"]:
        if (tkinter.messagebox.askyesno("发现新版本","是否更新？")==True):
            threading.Thread(target=update,kwargs={"url":remoteVer["url"]}).start()
    else:
        tkinter.messagebox.showinfo("无新版本","本地版本是最新的\nGo And Play!")
    return

#init
windowHndl=tkinter.Tk()
windowHndl.geometry("400x300")
windowHndl.maxsize(400,300)
windowHndl.minsize(400,300)
windowHndl.wm_title("整合包更新器")
windowHndl.iconbitmap("./Updater/icon.ico")
mcImg=tkinter.PhotoImage(file="./Updater/icon.gif")
imgLbl=tkinter.Label(image=mcImg)
imgLbl.image = mcImg # keep a reference!
imgLbl.pack()

#get ver & desc
ver=getLocalVersion()["version"]
desc=getLocalVersion()["desc"]
infoString=tkinter.StringVar(value="版本：%.2f\n%s"%(float(ver),desc))
info=tkinter.Label(windowHndl,textvariable=infoString,font=("微软雅黑",20))
info.pack()
updateBtn=tkinter.Button(windowHndl,text="检查更新",command=chkUpdate,font=("微软雅黑",20))
updateBtn.pack()
windowHndl.mainloop()
log("成功退出",exc=None,Type="log")
