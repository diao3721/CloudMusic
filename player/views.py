from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
import logging
from .models import Playlist
# Create your views here.
logger = logging.getLogger('django')
class Requests(object):
    def __init__(self,url):
        self.session = requests.session()
        self.header = {}
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

    # 原始post使用保留
    # bodyData: request's data
    def post(self, bodyData):
        response = None
        self.errorMsg = ""

        try:
            response = self.session.post(self.URL, data=bodyData.encode('utf-8'), headers=self.header,
                                         timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            self.errorMsg = str(e)
            logger.error("HTTP请求异常，异常信息：%s" % self.errorMsg)
        return response

    # 复数请求并发处理，采用线程池的形式，用例数>线程池的容量：线程池的容量为并发数，否则，用例数为并发数
    # dicDatas: {用例编号：用例数据}
    def req_all(self, dicDatas, iThreadNum=5):

        if len(dict(dicDatas)) < 1:
            logger.error("没有测试对象，请确认后再尝试。。。")
            return self.responses.clear()

        # 请求用例集合转换（用例编号，用例数据）
        seed = [i for i in dicDatas.items()]
        self.responses.clear()

        # 线程池并发执行，iThreadNum为并发数
        with ThreadPoolExecutor(iThreadNum) as executor:
            executor.map(self.req_single, seed)

        # 返回所有请求的响应信息（{用例编号：响应数据})，http连接异常：对应None
        return self.responses

    # 用于单用例提交，http连接失败可以重新连接，最大重新连接数可以动态设定
    def req_single(self, listData, reqType="post", iLoop=1):
        response = None
        # 如果达到最大重连次数，连接后提交结束
        if iLoop == self.iRetryNum:
            if reqType == "post":
                try:
                    response = requests.post(self.URL, data=listData[1].encode('utf-8'), headers=self.header,
                                             timeout=self.timeout)
                    response.raise_for_status()
                except Exception as e:
                    # 异常信息保存只在最大连接次数时进行，未达到最大连接次数，异常信息为空
                    self.resErr[listData[0]] = str(e)
                    logger.error("HTTP请求异常，异常信息：%s【%d】" % (str(e), iLoop))

                self.responses[listData[0]] = response
            else:
                # for future： other request method expand
                pass
        # 未达到最大连接数，如果出现异常，则重新连接尝试
        else:
            if reqType == "post":
                try:
                    response = requests.post(self.URL, data=listData[1].encode('utf-8'), headers=self.header,
                                             timeout=self.timeout)
                    response.raise_for_status()
                except Exception as e:
                    logger.error("HTTP请求异常，异常信息：%s【%d】" % (str(e), iLoop))
                    # 重连次数递增
                    iLoop += 1
                    # 进行重新连接
                    self.req_single(listData, reqType, iLoop)
                    # 当前连接终止
                    return None
                self.responses[listData[0]] = response
            else:
                # for future： other request method expand
                pass

    # 设定SoapAction, 快捷完成webservice接口header设定
    def setSoapAction(self, soapAction):
        self.header["SOAPAction"] = soapAction
        self.header["Content-Type"] = "text/xml;charset=UTF-8"
        self.header["Connection"] = "Keep-Alive"
        self.header["User-Agent"] = "InterfaceAutoTest-run"


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


def musicSearch(request):
    __url = "https://api.bzqll.com/music/netease/search"
    __key = "579621905"
    failRes = {
        'code':9999,
        'msg':""
    }
    logging.info("开始")
    logger.info("接收到request请求")
    # logging.info(request.POST)
    logger.info(request.body)
    logger.info(request.POST)
    if(request.method != 'POST'):
        failRes['msg'] = "请使用POST方法"
        return JsonResponse(failRes,safe=False)
    else:
        song = request.POST.get('song','')
        if not song.strip():
            failRes['msg'] = "emptyPost"
            return JsonResponse(failRes,safe=False)
        logger.info(song)
        payload = {
            'key' : __key,
            'limit' : 50,
            'offset' : 0,
            's':song
        }
        s = requests.get(__url,params=payload)
        res = s.json()
        # r = Requests(__url)
        # res = r.post(urllib.parse.urlencode(payload))
        return JsonResponse(res)