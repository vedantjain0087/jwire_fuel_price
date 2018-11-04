from django.shortcuts import render
from django.http import HttpResponse
import bs4 as bs
import urllib
import json
import requests
import datetime
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

def attach_day(dt):
    # dt format 7/24/2017
    month, day, year = (int(x) for x in dt.split('/'))
    date = datetime.date(year, month, day)
    mdy = dt.split('/')
    # format Mon 24/7/2017
    return date.strftime('%A')[:3] + ' ' + '/'.join([mdy[1], mdy[0], mdy[2]])


def get_standard_time(tm):
    # tm format 4:21 pm
    tm = tm.strip()
    if tm[5:] == 'am':
        return tm
    hour = int(tm.split(':')[0])
    if hour != 12:
        hour = hour + 12
    time = str(hour) + ':' + tm.split(':')[1].split(' ')[0]
    # format time 16:21
    return time


def get_package_details(request):
    track_no = request.POST.get("track_no")
    try:
        header = {
            'Origin': 'https://www.fedex.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.fedex.com/apps/fedextrack/?tracknumbers=%s&locale=en_CA&cntry_code=ca_english' % (
                str(track_no)),
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8,fr;q=0.6,ta;q=0.4,bn;q=0.2'
        }

        data = {
            'action': 'trackpackages',
            'data': '{"TrackPackagesRequest":{"appType":"WTRK","appDeviceType":"DESKTOP","uniqueKey":"",'
                    '"processingParameters":{},"trackingInfoList":[{"trackNumberInfo":{"trackingNumber":"%s",'
                    '"trackingQualifier":"","trackingCarrier":""}}]}}' % (
                        str(track_no)),
            'format': 'json',
            'locale': 'en_CA',
            'version': '1'
        }

        url = "https://www.fedex.com/trackingCal/track"
        
        print "Sending request ..."

        response = requests.post(url, data=data, headers=header)

        if response.status_code == 200:
            print "response received successfully\n"
        else:
            print "request failed, error code : ",response.status_code
            return

        res_json = response.json()

        if res_json['TrackPackagesResponse']['packageList'][0]['errorList'][0]['message'] != "":
            print res_json['TrackPackagesResponse']['packageList'][0]['errorList'][0]['message']
            # exists the function if package id is wrong
            return

        key_status = res_json['TrackPackagesResponse']['packageList'][0]['keyStatus']

        # changes the scheduled delivery date and time w.r.t status
        if key_status == "In transit":
            schld_deli = attach_day(res_json['TrackPackagesResponse']['packageList'][0][
                                        'displayEstDeliveryDt']) + " by " + get_standard_time(
                res_json['TrackPackagesResponse']['packageList'][0]['displayEstDeliveryTm'])
        else:
            schld_deli = attach_day(
                res_json['TrackPackagesResponse']['packageList'][0]['displayActDeliveryDt']) + " " + get_standard_time(
                res_json['TrackPackagesResponse']['packageList'][0]['displayActDeliveryTm'])
 

        result = {
            'tracking_no': int(track_no),
            'ship date': attach_day(res_json['TrackPackagesResponse']['packageList'][0]['displayShipDt']),
            'status': res_json['TrackPackagesResponse']['packageList'][0]['keyStatus'],
            'scheduled delivery': schld_deli
        }
        return HttpResponse(json.dumps({'result':result}), content_type='application/json')

    except Exception as e:
        print 'Error occurred : \n Error Message: ' + str(e)