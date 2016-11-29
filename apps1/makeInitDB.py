# -*- coding=utf-8 -*-
from django.shortcuts import render
from .models import Word, Checkdup, InitWord
from bs4 import BeautifulSoup
import urllib2
import urllib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from random import shuffle
import datetime
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from operator import eq

def makeInitDB():
    start_list = ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카',
         '타','파', '하']

    for sw in start_list:
        url="http://krdic.naver.com/search.nhn?query= %2A&kind=keyword&page=1"
        url = url[0:40] + urllib.quote(sw) + url[41:]
        soup = BeautifulSoup(urllib2.urlopen(url).read())

        whole_list = soup.findAll("ul", "lst3")

        word_list = whole_list[0].findAll("a", "fnt15")
        l = []
        for i in word_list:
            f = False
            for j in range(len(i.text)):
                if i.text[j] == '(':
                    data = i.text[0:j-1]
                    l.append(data)
                    f = True
                    break
                if i.text[j].isdigit() == True:
                    data = i.text[0:j]
                    l.append(data)
                    f = True
                    break
            if f == False:
                l.append(i.text[:])
        for i in l:
            n = InitWord(word=i)
            n.save()


makeInitDB()
