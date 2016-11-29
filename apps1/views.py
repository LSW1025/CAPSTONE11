# -*- coding=utf-8 -*-
from django.shortcuts import render
from .models import Word, Checkdup
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

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def firstWord(request):
    if request.method == 'GET':
        firstWord = u"사랑"
        now = datetime.datetime.now()
        n = Checkdup(time = now)
        n.save()
        p = Checkdup.objects.get(time=now)
        m = Word(word = firstWord, session_num=str(p.idx))
        m.save()


        url2 = 'http://krdic.naver.com/search.nhn?query= &kind=keyword'
        url2 =  url2[0:40] + urllib.quote(firstWord[0:len(firstWord)].encode('utf-8')) + url2[41:]

        soup2 = BeautifulSoup(urllib2.urlopen(url2).read())
        meaning = soup2.findAll("a", "fnt15")[0].find_all_next("p")
        if len(meaning[0].text) < 6:
            meaning = soup2.findAll("a", "fnt15")[0].find_all_next("span", "con")
        result = {'word':m.word, 'session':m.session_num,
                  'meaning':meaning[0].text}
        return JSONResponse(result)


def checkDuplication(word_, session):
    p = Word.objects.filter(word=word_)
    flag = False
    for i in p:
        if i.session_num == session:
            flag = True
    if flag == True: return True
    else: return False


def checkNorthKoreaLang(word, session):
        url = 'http://krdic.naver.com/search.nhn?query= &kind=all'
        url =  url[0:40] + urllib.quote(word[0:len(word)].encode('utf-8')) + url[41:]
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        strArray = soup.find("span","ex")
        if strArray == True:
            curWord = strArray.text[1:4].encode('utf-8')
            curWord2 = strArray.text[1:3].encode('utf-8')
            target = "북한어"
            target2 = "방언"
            if curWord == target or curWord2 == target2:
                return True # 북한어 또는 방언
            else:
                return False
        else:
            return False

def checkExistance(word, session): # 상대편이 말한 단어가 존재하지 않으면 
        url = 'http://krdic.naver.com/search.nhn?query= &kind=all'
        url =  url[0:40] + urllib.quote(word[0:len(word)].encode('utf-8')) + url[41:]
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        strArray = soup.findAll("h4")
        if len(strArray) < 1:
            return False
        strArray2 = str(strArray[0]).split()
        if len(strArray2) < 4:
            return False
        if len(strArray2[4].decode('utf-8')) >= 10:
            return True
        else:
            return False

# 단어를 10개 랜덤으로 중복안되게 뿌려줌. 일단 10개만
def nextWord(request):
    if request.method == 'GET':
        curWord = request.GET['word']
        session_num = request.GET['session']

        # 유저가 말한 단어가 중복이면
#        if checkDuplication(curWord, session_num) == True:
#            return JSONResponse({'word':"dup", 'session':session_num})
        # 유저가 말한 단어가 존재하지 않으면        
#        if checkExistance(curWord, session_num) == True:
#            return JSONResponse({'word':"non", 'session':session_num})


        # 웹페이지에서받은 단어 끝으로 시작하는 단어 10개를 가져옴
        url="http://krdic.naver.com/search.nhn?query= %2A&kind=keyword&page=1"
        url =  url[0:40] + urllib.quote(curWord[len(curWord)-2:len(curWord)-1].encode('utf-8')) + url[41:]
        soup = BeautifulSoup(urllib2.urlopen(url).read())

        whole_list = soup.findAll("ul", "lst3")
        # 다음 단어를 말할게 없으면
        if len(whole_list) == 0:
            return JSONResponse({'word':"end", 'session':session_num,
                                 'meaning':"end"})
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

        # 랜덤으로 섞은 뒤 중복되지 않은 단어를 리턴
        shuffle(l)
        next_word = ''
        flag = False
        for i in l:
            if checkNorthKoreaLang(i, session_num) == False: # 북한어아닐때
                if checkDuplication(i, session_num) == False: # 중복이 없으면
                    next_word = i
                    flag = True
                    break

        # 현재 뽑은 단어가 모두 중복이거나 모두 북한어 이면 종료
        if flag == False:
            return JSONResponse({'word':"end",
                                 'session':session_num,'meaning':"end"})

        url2 = 'http://krdic.naver.com/search.nhn?query= &kind=keyword'
        url2 =  url2[0:40] + urllib.quote(next_word[0:len(next_word)].encode('utf-8')) + url2[41:]
        soup2 = BeautifulSoup(urllib2.urlopen(url2).read())
        meaning = soup2.findAll("a", "fnt15")[0].find_all_next("p")
        if len(meaning[0].text) < 6:
            meaning = soup2.findAll("a", "fnt15")[0].find_all_next("span", "con")


        w = Word(word=next_word, session_num=session_num)
        w.save()
        result = {'word':next_word, 'session':session_num,
                  'meaning':meaning[0].text}
        return JSONResponse(result)

