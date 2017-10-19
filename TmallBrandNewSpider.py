# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
import time
import datetime
import requests
import chardet
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from pyquery import PyQuery as pq
import pymongo
from lxml import etree
import pandas as pd
import re
import urllib,urllib2
import base64
import json
from multiprocessing import Pool
from multiprocessing.dummy import Pool as TheaderPool
import random
from connectModel import Mssql,InsertPreSaleNew,InsertOrUpdateBaseInfo,judgeHaveTreasureID,InsertShopTempletes,ExistenceShopName,SelectShopTempletes,now
from  common import styleNames,categoryNamesQly,brandName,evaluationScoreURL,clearToReplaceData,tmallYuShouTable,tmallCode,JudgeLoginSuccess,tmallLogin,WhetherYuShou,saveTmallYuShouToMongodb,\
getProductData,saveYuShouOrRemove,judgeProduct,dbChoice,allShopName
import os

#亚蔑蝶

#和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


allShopTreasureID = []

#TODO:EXP 全新天猫预售  首页点击到第二页情况
def tmallBrandNews():

    # TODO:XDF Chrome欲歌浏览器
    # options = webdriver.ChromeOptions()
    # # options.add_extension('AdBlock_v3.15.0.crx') # TODO:XDF Chrome欲歌广告过滤插件
    # # 设置中文
    # options.add_argument('lang=zh_CN.UTF-8')
    # # prefs = {"profile.managed_default_content_settings.images": 2}
    # # options.add_experimental_option("prefs", prefs)  # TODO:XDF 禁止加载图片
    # # 更换头部
    # options.add_argument(
    #     'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"')
    # # driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')#chrome_options=options,
    # driver = webdriver.Chrome(
    #     executable_path=r'/Users/zhuoqin/Downloads/123456/chromedriver')  # chrome_options=options,
    # wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间
    # print '窗口最大化----1'
    # tmallLogin(driver, UnexpectedAlertPresentException, ActionChains)
    # print '窗口最大化----2'

    # TODO:XDF PhantomJS无头浏览器
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36")  # 设置user-agent请求头
    dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

    print ('即将开始。。。')
    service_args = []
    service_args.append('--load-images=no')  ##关闭图片加载
    service_args.append('--disk-cache=yes')  ##开启缓存
    service_args.append('--ignore-ssl-errors=true')  ##忽略https错误
    # #TODO:XDF 针对本地调试
    # driver = webdriver.PhantomJS(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/phantomjs',service_args=service_args,desired_capabilities=dcap)

    driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)  # TODO:XDF 针对Linux
    # # TODO:XDF 针对Linux服务器
    # wait = WebDriverWait(driver, 60, 0.5)  # 表示给browser浏览器一个10秒的加载时间
    #
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)
    wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间

    try:
        print '进来窗口了'
        # driver.maximize_window()
        driver.get("https://list.tmall.com/search_product.htm?q=123&type=p")

        print '窗口最大化----'
    except Exception as e:
        print '即将出错啦----%s'%e
        driver.quit()
        driver.close()
        return

    time.sleep(2)
    if 'login.tmall' in str(driver.current_url):
        print '即将登录'
        tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
    SelectShopTempletes()
    for i in range(0,len(allShopName)):

        print('进来了---%s' % i)
        driver.find_element_by_xpath('//*[@id="mq"]').clear()
        time.sleep(random.uniform(2,4))
        driver.find_element_by_xpath('//*[@id="mq"]').send_keys(allShopName['shopName'][i])
        print('地址********%s'%(allShopName['shopName'][i]))
        time.sleep(random.uniform(3,5))

        if 'login.tmall' in str(driver.current_url):
            print '当前为登录页面'
            tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)

        driver.find_element_by_xpath('//*[@id="mallSearch"]/form/fieldset/div/button').click()
        tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
        wait.until(EC.presence_of_element_located((By.ID, 'J_ItemList')))
        time.sleep(random.uniform(2, 4))
        print '赶紧睡吧'
        JudgeLoginSuccess(driver,UnexpectedAlertPresentException,ActionChains)

        time.sleep(random.randint(1, 3))

        key = allShopName['shopName'][i]
        html = driver.page_source
        docs = pq(html)

        for j in range(0,getProjectPage(docs)):
            time.sleep(random.randint(4, 8))
            urls = 'https://list.tmall.com/search_shopitem.htm?s=' + str(j*60) + '&oq=' + str(key) + '&style=sg&sort=s&user_id='+str(allShopName['user_id'][i])+'&stype=search'
            driver.get(urls)
            time.sleep(random.randint(1,3))
            if tmallCode(driver, wait,EC) == '访问过快':
                continue
            tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
            wait.until(EC.presence_of_element_located((By.ID, 'J_ItemList')))
            time.sleep(random.uniform(3,5))
            html = driver.page_source

            doc = pq(html)
            list = doc('#J_ItemList .product   .product-iWrap').items()

            resultData = search(list, urls)
            time.sleep(random.uniform(3, 5))

            print '所有店铺ID----%s-----%s'%(len(resultData),resultData)
            getDetailFilterData(driver,wait,resultData,allShopName['shopName'][i])


    # tmallYuShouTable.close()  # 这里需要手动关闭游标

#这是获取产品
def getDetailFilterData(driver,wait,resultData,ShopName):
    for TreasureID in resultData:
        print '------你大爷------'
        time.sleep(random.uniform(4, 7))
        try:
            driver.get('https://detail.tmall.com/item.htm?id='+str(TreasureID))
            time.sleep(random.randint(1, 3))
            print '地址----%s' % str(TreasureID)
        except Exception as e:
            print e
            continue

        if judgeProduct(driver) == True:
            print '商品不存在'
            continue

        if tmallCode(driver, wait, EC) == '访问过快':
            continue
        tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-detail-hd')))  # 显性等待
        except Exception as e:
            print '显性未加载成功---%s' % e
            continue
        time.sleep(random.randint(2, 5))  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)
        htmlDetail = driver.page_source  # 这是一面的页面内容
        try:
            doc = pq(htmlDetail)

            if WhetherYuShou(doc) == False:
                print '-------不是预售，不需要保存--------'
                time.sleep(random.uniform(2,4))
                continue

            # TODO:XDF 这里需要注意一下，src图片链接可以不丰在https，需要自己手动拼接
            mainPics = doc.find('#J_ImgBooth').attr('src')
            if 'https:' in mainPics:
                mainPic = mainPics
            else:
                mainPic = 'https:' + mainPics
            # 收藏人数
            popularity = clearToReplaceData(doc.find('#J_CollectCount').text(),0)

            # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）
            presellPrice = clearToReplaceData(doc.find('#J_PromoBox').text(), 1)
            address = doc.find('#J_deliveryAdd').text()
            paymentDate = doc.find('.J_step2Time').text().split('~')
            paymentBeginDate = paymentDate[0]
            paymentFinishDate = paymentDate[1]
            reserveCount = clearToReplaceData(doc.find('.tb-wrt-guc').text(),3)
            detailPrice = clearToReplaceData(doc.find('#J_StrPriceModBox .tm-price').text(), 5)
            categoryIdContent = clearToReplaceData(str(doc.find('#J_ZebraPriceDesc').attr('mdv-cfg')), 2)
            print (categoryIdContent)

            spuIds = 'TShop.Setup\((.*?)\);'
            apiData = re.findall(spuIds, htmlDetail, re.S)[0]
            datas = json.loads(apiData)
            brandId = datas['itemDO']['brandId']
            categoryId = datas['itemDO']['categoryId']
            rootCatId = datas['itemDO']['rootCatId']
            spuId = datas['itemDO']['spuId']
            title = datas['itemDO']['title']
            sellerId = datas['rateConfig']['sellerId']
            # URL_NO = datas['rstShopId']
            shopID = sellerId

            shopName = doc.find('.slogo-shopname').text()
            categoryName = categoryNamesQly(str(TreasureID))
            styleData = doc.find('#J_AttrUL').children().items()
            # 风格
            StyleName = styleNames(styleData)
            # 因为styleData是一个迭代器，被循环完的就会被释放掉（品牌有可能在查找风格的时候循环过去了，已经被释放掉了），所以这里得重新赋值数据源
            brandData = doc.find('#J_AttrUL').children().items()
            # 品牌
            brand = brandName(brandData)
            # 评价描述评分
            EvaluationScores = evaluationScoreURL(str(TreasureID), str(spuId), str(sellerId))
            URL_NO = doc.find('#LineZing').attr('shopid')

            if ExistenceShopName(ShopName) == False: #这里证明这家店铺是没有被爬过的
                InsertShopTempletes(ShopName,URL_NO)

            try:
                ShopURL = str(doc.find('.shopLink').attr('href'))
                if len(ShopURL):
                    ShopURL = clearToReplaceData(ShopURL, 4)
                else:
                    ShopURL = '-'
            except Exception as e:
                print e

            print str(TreasureID),shopName, categoryName, datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'), detailPrice, address, title, mainPic, presellPrice, popularity  # , paymentBeginDate, paymentFinishDate, reserveCount

            StartTime = datetime.datetime.strptime(str(allShopName['YuShouStartTime'][0]), '%Y-%m-%d %H:%M:%S')

            EndTime = datetime.datetime.strptime(str(allShopName['YuShouEndTime'][0]), '%Y-%m-%d %H:%M:%S')

            # print nowTime, type(nowTime), type(endTime), now(), endTime

            # if now() > str(allShopName['YuShouEndTime'][0]):
            #     print '过期'
            # else:
            #     print '没过期'

            product = {
                'title': title,
                'TreasureID': str(TreasureID),
                'addRess': address,
                'shopName': shopName,
                'mainPic': mainPic,
                'detailPrice': detailPrice,
                'popularity': popularity,
                'reserveCount': reserveCount,
                'paymentBeginDate': paymentBeginDate,
                'paymentFinishDate': paymentFinishDate,
                'presellPrice': presellPrice,
                'categoryId': int(categoryId),
                'categoryName': categoryName,
                'spiderTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ShopID': shopID,
                'brandId': brandId,
                'brand': brand,
                'spuId': spuId,
                'rootCatId': int(rootCatId),
                'StyleName': StyleName,
                'EffectiveTime': '',
                'ReservationStatus': 0,
                'CollectionNum': 0,
                'ItemName': '',
                'NCategory_Name': '',
                'Is_Search': 1,
                'NStyleName': '',
                'NewstPrice': 0,
                'EvaluationScores': float(EvaluationScores),
                'URL_NO': URL_NO,
                'ShopURL': ShopURL,
                'sellerId': sellerId,
                'productState': '1',
                'StartTime':StartTime,
                'EndTime':EndTime
            }

            if str(dbChoice['TmallYuShouEnemyShopSql'][0]) == 'Mongodb': #保存到mongodb
                saveYuShouOrRemove(product, str(TreasureID))
            else:
                print '保存到sqlserver数据库...'

                if judgeHaveTreasureID(product) == True:
                    InsertOrUpdateBaseInfo(product, 'Update')
                else:
                    InsertOrUpdateBaseInfo(product, 'Insert')
                InsertPreSaleNew(product)

        except Exception as e:
            print ('error---%s' % e)





#获取每种产品的总页数
def getProjectPage(doc):
    pageNumber = doc.find('.ui-page-s-len').text()

    print '总页数-------%s'%pageNumber
    if '/' in pageNumber:
        page = int(pageNumber.split('/')[1])
    else:
        page = int(pageNumber)
    return page


def search(list, url):
    print '***789*********%s' % url
    allShopTreasureID = []
    for item in list:

        TreasureID = item.find('.productStatus').eq(0).children().eq(-1).attr('data-item')

        allShopTreasureID.append(TreasureID)
    return allShopTreasureID



if __name__ == '__main__':

    # if str(dbChoice['TmallYuShouEnemyShopSql'][0]) == 'Mongodb':
    #     print '相等'
    #
    tmallBrandNews()

    # nowTime = datetime.datetime.strptime(str(allShopName['YuShouStartTime'][0]), '%Y-%m-%d %H:%M:%S')
    #
    # endTime = datetime.datetime.strptime(str(allShopName['YuShouEndTime'][0]), '%Y-%m-%d %H:%M:%S')
    #
    # print nowTime,type(nowTime),type(endTime),now(),endTime
    #
    # if now() > str(allShopName['YuShouEndTime'][0]):
    #     print '过期'
    # else:
    #     print '没过期'


    # SelectShopTempletes()
    # for i in range(0, len(allShopName)):
    #     if ExistenceShopName(allShopName['shopName'][i]) == True:  # 这里证明这家店铺是没有被爬过的
    #         # InsertShopTempletes(allShopName['shopName'][i], URL_NO)
    #         print '存在'
    #         break

    # ceShiProduct()
    # pool = TheaderPool(processes=4)
    # pool.map_async(tmallBrandNews(),range())

    # headers = {
    #     'UserAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    #     'Host':'www1.rmfysszc.gov.cn'
    # }
    # #
    # url = 'http://www1.rmfysszc.gov.cn/ProjectHandle.shtml'
    # # 发送一个http请求
    # request = urllib2.Request(url=url, headers=headers)
    # # 获得回送的数据
    # response = urllib2.urlopen(request)
    #
    # datas = response.read()
    # print  datas

    # url = 'http://httpbin.org/post'
    # s = json.dumps({})
    # r = requests.post(url, data=s,headers=headers)
    # print r.text









