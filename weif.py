#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import urllib,urllib2,sys,os,cookielib,re,time,random,traceback,getopt,libnets

loginRE   = re.compile('"(http://bbs\.weiphone\.com/api/uc_api/api/uc\.php\?time=\d+&code=\S+)"')
tidRE     = re.compile('href="read-htm-tid-(\d+)\.html">(.+?)</a>')
titleRE   = re.compile('<title>(.+?) -')
verifyRE  = re.compile("verifyhash = '(\w{7,8})'")
wwsfyRE   = re.compile('value="(\w+)" name="wwsfy">')

usertidRE = re.compile('<a href="job\.php\?action=topost&tid=(\d+)&pid=(\d+)"')
usernameRE = re.compile('<strong class="f14 b">(.+?)</strong>')

def get_module_path():
        if hasattr(sys, "frozen"):
            module_path = os.path.dirname(sys.executable)
        else:
            module_path = os.path.dirname(os.path.abspath(__file__))
        return module_path
path=get_module_path()

confile    = "%s/content.txt"%path
configfile = "%s/config.ini"%path
userfile = "%s/user"%path


sysencode=sys.getfilesystemencoding()



def printf(str):

    Work.print_callback(str)

def load_config():
        global CONFIG
        CONFIG={"timeout":"40","fidlist":"240,272","looppage":"2","uselog":"0","usexpression":"1,-14"}
        if not os.path.exists(configfile):
            return
        config = open(configfile)
        text = config.read()
        if text.startswith("\xef\xbb\xbf"):
            text=text[3:]
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            key, value = line.split("#")[0].strip().split("=", 1)
            if value in ["True", "true", "yes"]:
                value = True
            if value in ["False", "false", "no"]:
                value = False
            try:
                CONFIG[key] = str(value)
            except:
                CONFIG[key] = value
        config.close()



class work:
    def __init__(self,print_callback=None):
        self.print_callback=print_callback
        printf ("取得验证或任何问题请联系\nkikyous@163.com\n".decode("u8"))
        self.cookiefile = "%s/cookie"%path

        self.count=1
        load_config()
        self.currentfidindex=0
        self.currentpage=1
        self.currenttopicindex=0
        self.fidlist=CONFIG["fidlist"].split(",")
        self.num=20
        self.addpoint="1"
        self.setoff=0
        self.parse_args()
      #  self.loadcookie()


        self.exprBlist=CONFIG["usexpression"].split(",")
        for i,item in enumerate(self.exprBlist):
            self.exprBlist[i]=abs(int(item))
        

        if CONFIG["uselog"]=="1":
            self.log=open("log.txt","a")
      #  printf CONFIG
    def parse_args(self):
        try:
            opts,args=getopt.getopt(sys.argv[1:], "c:f:t:u:n:p:h")
            for i in opts:
                if "-f" in i:
                    self.currentfidindex=int(i[1])
                elif "-t" in i:
                    self.currenttopicindex=int(i[1])
                    self.setoff=int(i[1])
                elif "-u" in i:
                    self.user=i[1]
                elif "-p" in i:
                    self.addpoint=i[1]

                elif "-n" in i:
                    self.num=int(i[1])
                elif "-c" in i:
                    self.cookiefile = "%s/%s"%(path,i[1])

                elif "-h" in i:
                    printf '''option usage:
-t num \t 帖子偏移num,即忽略前num个帖子(回帖和评分模式有效)
-f num \t 板块偏移num,即首次忽略板块列表中前num个板块(回帖模式有效)
-u userid  要评分的用户id(评分模式有效)
-n num \t 要进行评分的次数(评分模式有效)
-p num \t 每次评分的分数,负数就是扣分(评分模式有效)
-c file \t 指定使用的用户标识cookie文件
-h \t 显示帮助'''.decode("u8")

                    sys.exit()

                    
        except getopt.GetoptError:
            printf "option error !"

    def getContent(self):
        try:
            f=open(confile)
            list=f.readlines()
            f.close()
            if list[0].startswith("\xef\xbb\xbf"):
                list[0]=list[0][3:]

            return list
        except:
            printf "content.txt 文件异常,2s后退出!".decode("u8")
            time.sleep(2)
            sys.exit()

    def getReplycon(self):
        expr=""
        if self.exprBlist[0]:
            while 1:
                expr=random.randint(1,130)
                if not expr in self.exprBlist[1:]:
                    break
            expr="[s:%d]\n"%expr
        self.conIndex+=1
        if self.conIndex>=self.Clen:
            self.conIndex=0
        return self.conList[self.conIndex]+expr
                



   # @work.verifi_login
    def login(self,username,passwd):
     #   username=username.decode(sysencode).encode("u8")
     #   passwd=passwd.decode(sysencode).encode("u8")
        url="http://passport.weiphone.com/?r=user/loginProcess"
        data = {"Kaf_Model_Form_Login[login]":username, "Kaf_Model_Form_Login[password]":passwd, "yt0":"登  陆","Kaf_Model_Form_Login[rememberMe]":"1"}
        data = urllib.urlencode(data)
        cookieJar = cookielib.LWPCookieJar(self.cookiefile)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

       # req = urllib2.Request(url)
        request = urllib2.Request(url)
        request.add_header("Proxy-Connection","keep-alive")
        response = opener.open(request, data)
        response = response.read().decode("u8")
        url=loginRE.findall(response)[0]
    #    printf url
        cookieJar.save()

        cookieJar = cookielib.LWPCookieJar(self.cookiefile)
        cookieJar.load()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

        urllib2.install_opener(opener)

        cookieJar = cookielib.LWPCookieJar(self.cookiefile)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

        request = urllib2.Request(url)


        request.add_header("Host","bbs.weiphone.com")
        request.add_header("Referer","http://passport.weiphone.com/?r=user/login")
        request.add_header("User-Agent","Mozilla/5.0 (X11; Linux i686; rv:10.0a2) Gecko/20111126 Firefox/10.0a2")
        res=opener.open(request)
     #   printf res.headers
        cookieJar.save()
    def loadcookie(self,write=0):
        try:
            cookieJar = cookielib.LWPCookieJar(self.cookiefile)
            cookieJar.load()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

      #      printf "load cookiefile success! "
        except :
            printf "cookie file not fount,please login !"
            time.sleep(1)
            while 1:
                try:
                    username=raw_input("用户名:".decode("u8").encode(sysencode))
                    passwd=raw_input("密  码:".decode("u8").encode(sysencode))
                    username=username.decode(sysencode).encode("u8")
                    passwd=passwd.decode(sysencode).encode("u8")

                    printf "正在登录,请稍候...".decode("u8")
                    self.verifi_login(username,passwd)
            #        self.login(username,passwd)
                    printf "登录成功!".decode("u8")

                    self.loadcookie()
                    break
                except SystemExit:
                    sys.exit()

                except:
                    printf "登录失败,请重新登录!\n".decode("u8")

    def changepage(self):
        if self.currentpage>=int(CONFIG["looppage"]):
            self.currentpage=1
            self.currentfidindex+=1
            if self.currentfidindex>=len(self.fidlist):
                self.currentfidindex=0
            printf "+fid : ",self.fidlist[self.currentfidindex]," : page ",self.currentpage
        else:
            self.currentpage+=1
            printf "fid: ",self.fidlist[self.currentfidindex]," : +page ",self.currentpage
        printf 
        self.tidList=self.getTid(self.fidlist[self.currentfidindex],self.currentpage)
        self.Tlen=len(self.tidList)

    def getTid(self,fid,page=1):
        url="http://bbs.weiphone.com/thread-htm-fid-%s-page-%d.html"%(fid,page)
        request=urllib2.Request(url)
        request.add_header("Host","bbs.weiphone.com")
        request.add_header("User-Agent","Mozilla/5.0 (X11; Linux i686; rv:10.0a2) Gecko/20111126 Firefox/10.0a2")
        response = self.opener.open(request).read().decode("utf-8")
        self.fidTitle=titleRE.findall(response)[0]
        if page==1:
            if not "短消息".decode("u8") in response:
                printf "不能识别用户信息,请删除cookie文件并重新登录,2s 后退出".decode("u8")
                time.sleep(2)
                sys.exit()
            else:
                self.verify=verifyRE.findall(response)[0]
                self.wwsfy=wwsfyRE.findall(response)[0]
        #        printf self.verify
          #      printf self.wwsfy

            response=response.split(">普通主题<".decode("u8"))[1]

        return tidRE.findall(response)


    def getUserTid(self,user,page="1"):

        url="http://bbs.weiphone.com/apps.php?q=article&uid=%s&see=post&ptable=1&page=%s"%(user,page)

        request=urllib2.Request(url)
        request.add_header("Host","bbs.weiphone.com")
        request.add_header("User-Agent","Mozilla/5.0 (X11; Linux i686; rv:10.0a2) Gecko/20111126 Firefox/10.0a2")
        response = self.opener.open(request).read().decode("utf-8")
        self.verify=verifyRE.findall(response)[0]
        if not hasattr(self,"username"):
            try:
                self.username=usernameRE.findall(response)[0]
            except:
                self.username="Unknown"
        return usertidRE.findall(response)

    def run(self,fid,tid,con): 
        try:
            #  url="http://bbs.weiphone.com/post.php?fid=240"
            url="http://bbs.weiphone.com/post.php?nowtime=1322463075539&verify=%s"%self.verify

            data = {"action":"reply","atc_usesign":"1","atc_convert":"1","atc_autourl":"1","step":"2","type":"ajax_addfloor","fid":fid,"tid":tid,"atc_title":"","atc_content":con,"attachment_1":"","atc_desc1":"","ok":"1","cyid":"","replytouser":"","wwsfy":self.wwsfy,"stylepath":"weiphone","cyid":"","_hexie":"469c2cfb","iscontinue":"0"}
            data = urllib.urlencode(data)

            request = urllib2.Request(url)
            request.add_header("Host","bbs.weiphone.com")
            request.add_header("User-Agent","Mozilla/5.0 (X11; Linux i686; rv:10.0a2) Gecko/20111126 Firefox/10.0a2")


            response = self.opener.open(request,data).read()#.decode("utf-8")

            if "<title>提示信息" in response:
                if CONFIG["uselog"]=="1":
                    self.log.write(response)
                return "fail"
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            return "network"


    def points(self,tid,pid,con):
        try:
            url="http://bbs.weiphone.com/operate.php?action=showping&ajax=1&nowtime=1322633914831&verify=%s"%self.verify#59412924

            data={"addpoint[]":self.addpoint,"atc_content":con,"cid[]":"2","ifmsg":"1","ifpost":"1","selid[]":pid,"step":"1","tid":tid}

            data = urllib.urlencode(data)

            request = urllib2.Request(url)
            request.add_header("Host","bbs.weiphone.com")
            request.add_header("User-Agent","Mozilla/5.0 (X11; Linux i686; rv:10.0a2) Gecko/20111126 Firefox/10.0a2")

            response = self.opener.open(request,data).read()#.decode("utf-8")
            if not '"point":' in response:
                if CONFIG["uselog"]=="1":
                    self.log.write(response)
                return "fail"
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            return "network"




#    @classmethod    
    def verifi_login(self,username,passwd):
            n=libnets.nets(username.decode("utf8").encode("gbk"))
            printf ('正在验证...'.decode("u8"))
            self.check=n.verifi()
            if not self.check:
                printf ('验证失败, 2s 后退出! '.decode("u8"))
                time.sleep(2)
                sys.exit()
            printf( '验证成功 ! '.decode("u8"))

            self.login(username,passwd)
            f=open(self.cookiefile,"a")
            f.write("#%s\n#%s"%(username,passwd))
            f.close()






    def verifi(self,n=0):
        if not n:
            self.loadcookie()
            return 
        self.loadcookie(1)
        if not hasattr(self,"check"):
            f=open(self.cookiefile)
            list=f.readlines()[-2:]
            f.close()
            username=list[0][1:].strip()
            passwd=list[1][1:]

         #   printf username,passwd
            try:
                os.remove(self.cookiefile)
                self.verifi_login(username,passwd)
                self.loadcookie()
            except:
                printf ( '登录失败 , 2s 后退出! '.decode("u8") )
                time.sleep(2)
                sys.exit()




    def start(self):
        self.conList=self.getContent()

        self.Clen=len(self.conList)
        self.conIndex=random.randint(0,self.Clen)

        try:
            if hasattr(self,"user"):
                print

                startpage=1+ self.setoff / 20
                tidlist=self.getUserTid(self.user,str(startpage))[self.setoff % 20:]
                
                last=None
                while self.num>len(tidlist):
                    startpage+=1
                    tmp=self.getUserTid(self.user,str(startpage))
                    if tmp==last:
                        break
                    tidlist+=tmp
                    last=tmp
                    sorted(set(tidlist),key=tidlist.index)
                tidlist=tidlist[:self.num]

#                index=1
#                for i in tidlist:
#                    printf index,i
#                    index+=1
                if tidlist==[]:
                    printf (self.username,"没有帖子或您没有权限查看!".decode('u8') )

                self.currenttopicindex=0
                while 1:
                    printf ("+%d x %s"%(self.count,self.addpoint))
                    printf (self.username)
                    printf ("http://bbs.weiphone.com/job.php?action=topost&tid=%s&pid=%s"%(tidlist[self.currenttopicindex][0],tidlist[self.currenttopicindex][1]) )
                    replyCon=self.getReplycon()
                    point=self.points(tidlist[self.currenttopicindex][0],tidlist[self.currenttopicindex][1],con=replyCon)
                    if point=="fail":
                        printf ("XXX",replyCon.decode("utf-8"))
                    elif point=="network":
                        printf ("Network can not reach")
                    else:
                        printf ("↘ ".decode("u8"),replyCon.decode("utf-8"))
                        self.count+=1



                    self.currenttopicindex+=1
                    if self.currenttopicindex >= len(tidlist):
                        return 

                    time.sleep(int(CONFIG["timeout"]))

            else:
                print "fid is",
                tmp=self.fidlist[:]
                tmp[self.currentfidindex]="+%s"%tmp[self.currentfidindex]
                for i in tmp:
                    print i,

                print ("\n")


                self.tidList=self.getTid(self.fidlist[self.currentfidindex])
                self.Tlen=len(self.tidList)
                while 1:
                    if self.currenttopicindex>=self.Tlen:
                        self.changepage()
                        self.currenttopicindex=0
                    printf ("+%d"%self.count)
                    printf (self.fidTitle)
                 #   printf self.tidList[t][1]
                    printf ("http://bbs.weiphone.com/read-htm-tid-%s-page-99999.html"%self.tidList[self.currenttopicindex][0])
                    replyCon=self.getReplycon()

                    reply=self.run(fid=self.fidlist[self.currentfidindex],tid=self.tidList[self.currenttopicindex][0],con=replyCon)
                    if reply=="fail":
                        printf ("XXX",replyCon.decode("utf-8") )
                    elif reply=="network":
                        printf ("Network can not reach" )

                    else:
                        printf ( "↘ ".decode("u8"),replyCon.decode("utf-8"))
                        self.count+=1

                    self.currenttopicindex+=1

                    time.sleep(int(CONFIG["timeout"]))
        except KeyboardInterrupt:
            printf ' have published %d articles'%(self.count-1)
            printf '^C received, 5s 后退出! '.decode("u8")
            time.sleep(5)
            sys.exit()
        except:
            time.sleep(5)
            if hasattr(self,"log"):
                traceback.printf_exc(file=self.log)
            else:
                f=open("log.txt","a")
                traceback.printf_exc(f)
                f.close()



