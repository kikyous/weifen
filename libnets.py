#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import re,urllib2
class nets:
    def __init__(self,username):
        self.home="http://hi.baidu.com/valentine1992/blog/item/8043f48e6e0e508ef603a6eb.html"
        self.RE=re.compile("\[\[(\S+) (\d+)\]\]")
        self.meRE=re.compile("\{\{(\d+)\}\}")
        self.username=username
        self.forme=0

    def verifi(self):
        done=False
        res=urllib2.urlopen(self.home)
        if res.url!=self.home:
            return False
        res=res.read()
        self.me=self.meRE.findall(res)[0]
        result=self.RE.findall(res)
    #    print result
        for i,x in enumerate(result):
            if self.username in x:
                done=True
                break
        if done:
            self.forme=result[i][1]
            return True
        return False



