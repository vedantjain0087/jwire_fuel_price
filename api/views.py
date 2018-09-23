from django.shortcuts import render
from django.http import HttpResponse
import bs4 as bs
import urllib
import json
import requests
# Create your views here.
def index(request):
    url = 'http://www.emeapromotions.com/screensaver/includes/apac-fuel/jp/jp-tab1-surcharge.html'
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    page = requests.get(url, headers=agent)
    soup = bs.BeautifulSoup(page.content, 'lxml')
    trs = soup.find_all('tr')
    res = []
    j = 0
    t = {}
    a = []
    for tr in trs[1:len(trs)]:
        x = tr.find_all('td')
        for y in x:
            if x.index(y) == 0:
                key = y.strong.string
            else:
                a.append(y.strong.string)
        t[key] = a
        a = []
        if t not in res:
            res.insert(j,t)
        j+=1
    print(res)

    #END OF tab 1

    url = 'http://www.emeapromotions.com/screensaver/includes/apac-fuel/jp/jp-tab3-historical.html'
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    page = requests.get(url, headers=agent)
    soup = bs.BeautifulSoup(page.content, 'lxml')
    s_trs = soup.find_all('tr')

    res2 = []
    t2 = {}
    k=0
    temp2 = []
    for x in s_trs[1:len(s_trs)]:
        arr = x.find_all('td')
        for td in arr:
            if arr.index(td) == 0:
                key = td.string
            else:
                temp2.append(td.string)
        t2[key] = temp2
        if t2 not in res2:
            res2.insert(k,t2)
        temp2 = []
        k+=1
    print(res2)
    return HttpResponse(json.dumps({'tab1':res,'tab2':res2}), content_type='application/json')
