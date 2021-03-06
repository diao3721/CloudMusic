from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import mplayer
import json
from .models import Playlist
import asyncio
import redis
# Create your views here.
global_list = []
logger = logging.getLogger('django')
def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton
@Singleton
class mControll(mplayer.Player):
    def __init__(self):
        # super(mplayer.Player,self).__init__()
        mplayer.Player.__init__(self)
        logger.info("234")
        logger.info(id(self))
    def check(self):
        if self.is_alive():
            self.quit()
            logger.info("已经退出")
            return True
        else:
            return False
    def startplay(self,url):
        try:
            logger.info("准备播放"+url)
            # self.check()
            if self.is_alive():
                logger.info("存在")
            else:
                logger.info("不存在")
            self.loadfile(url)
            return True
        except Exception as e:
            logger.info(e)
            return False
    def pause(self):
        logger.info("暂停播放")
        self.stop()
        return True
    def __del__(self):
        if self.is_alive():
            self.quit()
        class_name = self.__class__.__name__
        logger.info(class_name, '销毁')
p = mControll()
# re = redis.Redis(host='192.168.13.199',port=32770)
# re.set('p',p)
global_list.append(p)
# if callable(p):
#     logger.info("已存在，销毁")
#     p.pause()
#     p = mControll()

logger.info(json.dumps({'控制器id':id(p)},ensure_ascii=False))
class netGet(object):
    def __init__(self,url):
        # self.session = requests.session()
        self.header = {
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        }
        # URL默认来源于配置文件，方便不同测试环境的切换，也可以动态设定
        self.URL = url
        # 默认60s，可以动态设定
        self.timeout = 60
        # http连接异常的场合，重新连接的次数，默认为3，可以动态设定
        self.iRetryNum = 3

        self.errorMsg = ""
        # 内容 = {用例编号：响应数据}
        self.responses = {}
        # 内容 = {用例编号：异常信息}
        self.resErr = {}

    def get(self, bodyData):
        response = None
        self.errorMsg = ""

        try:
            response = requests.get(self.URL, params=bodyData, headers=self.header,
                                         timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            self.errorMsg = str(e)
            logger.error("HTTP请求异常，异常信息：%s" % self.errorMsg)
        return response.json()


def index(request):
    logger.info("接收到request请求")
    return render(request, 'index.html')

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def playMusic(request):
    failRes = {
        'code': 9999,
        'errRes': ""
    }
    logging.info("开始")
    logger.info("接收到request请求")
    logger.info(request.GET)
    if (request.method != 'GET'):
        failRes['errRes'] = "请使用GET方法"
        return JsonResponse(failRes)
    else:
        song = request.GET.get('song', '')
        return HttpResponse(song)

def musicSearch(request):
    failRes = {
        'code':9999,
        'errRes':""
    }
    logging.info("开始")
    logger.info("接收到request请求")
    # logging.info(request.POST)
    logger.info(request.GET)
    if(request.method != 'GET'):
        failRes['errRes'] = "请使用GET方法"
        return JsonResponse(failRes)
    else:
        song = request.GET.get('song','')
        limit = request.GET.get('limit','10')
        offset = request.GET.get('page','0')
        if not song.strip():
            failRes['errRes'] = "emptyPost"
            return JsonResponse(failRes)
        logger.info(song)
        payload = {
            'limit' : limit,
            'offset' : offset,
            'keywords':song
        }
        logger.info("开始请求")
        r = requests.get(settings.SEARCH_URL,params=payload)
        if r.status_code != 200:
            failRes['errRes'] = "网络异常"
            return JsonResponse(failRes)
        else:
            # logger.info(r.text)
            srch = r.json()
            if srch['code'] ==200:
                logger.info("请求成功")
                sucRes = {
                    'code': 0,
                    'msg': "SUCCESS",
                    'count':srch['result']['songCount'],
                    'data': srch['result']['songs']
                }
                # logger.info(sucRes)
                return JsonResponse(sucRes)
                # return render(request,'detail.html',sucRes)
            else:
                failRes['errRes'] = srch['result']
                return JsonResponse(failRes)
        # r = Requests(__url)
        # res = r.post(urllib.parse.urlencode(payload))
def musicCheck(request):
    failRes = {
        'code': 9999,
        'errRes': ""
    }
    try:

        logging.info("开始")
        logger.info("接收到check请求")
        # logging.info(request.POST)
        logger.info(request.GET)
        if (request.method != 'GET'):
            failRes['msg'] = "请使用GET方法"
            return JsonResponse(failRes)
        else:
            id = request.GET.get('id', '')
            if not id.strip():
                failRes['msg'] = "emptyPost"
                return JsonResponse(failRes)
            logger.info(id)
            payload = {
                'id': id
            }
            logger.info("开始请求")
            r = requests.get(settings.CHECK_URL, params=payload)
            srch = r.json()
            if r.status_code != 200:
                failRes['msg'] = srch['message']
                return JsonResponse(failRes,status=404)
            else:
                logger.info(r.text)
                if srch['success'] == True:
                    sucRes = {
                        'code': 200,
                        'msg': srch['message'],
                    }
                    logger.info(sucRes)
                    logger.info(global_list)
                    res = musicPlay(id)
                    if res:
                        logger.info("播放")
                        return JsonResponse(sucRes)
                    else:
                        failRes['msg'] = res['errRes']
                        return JsonResponse(failRes)

                    # return render(request,'detail.html',sucRes)
                else:
                    failRes['msg'] = srch['message']
                    return JsonResponse(failRes)
    except Exception as e:
        print(e)
        failRes['msg'] = '系统异常'
        return JsonResponse(failRes)
        # r = Requests(__url)


def musicPlay(id):
    try:
        failRes = {
            'code': 9999,
            'errRes': ""
        }
        # logging.info(request.POST)
        if not id.strip():
            failRes['errRes'] = "emptyPost"
            return failRes
        logger.info(json.dumps({'歌曲ID':id},ensure_ascii=False))
        payload = {
            'id': id
        }
        logger.info("开始请求播放地址")
        r = requests.get(settings.MUSIC_URL, params=payload)
        srch = r.json()
        if r.status_code != 200:
            failRes['msg'] = srch['message']
            return JsonResponse(failRes)
        else:
            # logger.info(r.text)
            
            if srch['code'] == 200:
                url = srch['data'][0]['url']
                logger.info(json.dumps({'播放地址':url},ensure_ascii=False))
                # return render(request,'detail.html',sucRes)
                # p = mplayer.Player()
                # if p.is_alive():
                #     logger.info("alive")
                #     logger.info(id(p))
                # p.loadfile(url)
                # res = True
                logger.info("启用")
                # global re
                # p = re.get('p')
                p = global_list[0]
                if p.is_alive():
                    logger.info("alive")
                else:
                    logger.info("err")
                res = p.startplay(url)
                if res:
                    return True
                else:
                    failRes['msg'] = '失败'
                    return JsonResponse(failRes)
            else:
                failRes['msg'] = srch['message']
                return JsonResponse(failRes)
    except Exception as e:
        logger.error(e)
        failRes['msg'] = '系统异常'
        return JsonResponse(failRes)
def musicStop(object):
    failRes = {
        'code': 9999,
        'errRes': ""
    }
    try:
        # global re
        # p = re.get('p')
        p = global_list[0]
        logger.info("stop的id"+str(id(p)))
        p.stop()
        return JsonResponse({'code':200,'msg':'停止了'})
    except Exception as e:
        logger.error(e)
        failRes['msg'] = e
        return JsonResponse(failRes)

