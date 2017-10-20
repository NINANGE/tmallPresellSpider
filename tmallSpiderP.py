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
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from lxml import etree
import pandas as pd
import re
import urllib,urllib2
import base64
import json
import random
from connectModel import Mssql,InsertPreSaleNew,InsertOrUpdateBaseInfo,judgeHaveTreasureID,strToDateTime
from common import tmallLogin,tmallCode,categoryNamesQly,styleNames,brandName,evaluationScoreURL,saveTmallGivenIDTB,ownShopID,allShopName,save_img,clearToReplaceData,df,\
    saveTmallGivenIDToYuShouTB,WhetherYuShou,judgeProduct,JudgeLoginSuccess,dbChoice,TmallYuShouBaseInfoData,UpdateTmallBaseInfoTB,saveTmallBaseInfoTBToMongodb,UpdateTmallYuShouTB
import os


#验证接口
url = 'https://v2-api.jsdama.com/upload'

#和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


#TODO:EXP 给定ID和店铺情况
def tmallGivenIDAndShopName():
    # TODO:XDF Chrome欲歌浏览器
    # options = webdriver.ChromeOptions()
    # # options.add_extension('AdBlock_v3.15.0.crx') # TODO:XDF Chrome欲歌广告过滤插件
    # # 设置中文
    # options.add_argument('lang=zh_CN.UTF-8')
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)  # TODO:XDF 禁止加载图片
    # # 更换头部
    # options.add_argument(
    #     'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"')
    # # driver = webdriver.Chrome(chrome_options=options,
    # #                           executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')
    # driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Downloads/123456/chromedriver')  # chrome_options=options,
    # wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间

    # TODO:XDF PhantomJS无头浏览器
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36")  # 设置user-agent请求头
    dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

    print ('即将开始。。。')
    service_args = []
    service_args.append('--load-images=no')  ##关闭图片加载
    service_args.append('--disk-cache=yes')  ##开启缓存
    service_args.append('--ignore-ssl-errors=true')  ##忽略https错误
    #TODO:XDF 针对本地调试
    # driver = webdriver.PhantomJS(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/phantomjs',service_args=service_args,desired_capabilities=dcap)
    #
    driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)  # TODO:XDF 针对Linux
    # # TODO:XDF 针对Linux服务器
    wait = WebDriverWait(driver, 60, 0.5)  # 表示给browser浏览器一个10秒的加载时间
    #
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)
    print ('等待中。。。')

    while True:
        BaseInfo = TmallYuShouBaseInfoData()
        for k in range(0,len(ownShopID)):
            time.sleep(random.uniform(6, 10))
            TreasureID = str(ownShopID['shopID'][k]).replace(' ','')
            driver.get('https://detail.tmall.com/item.htm?id=%s' % TreasureID)
            print ('https://detail.tmall.com/item.htm?id=%s' % TreasureID)
            # ID = str(ownShopID['shopID'][k])
            # JudgeLoginSuccess(driver,UnexpectedAlertPresentException,ActionChains)

            tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)

            time.sleep(random.uniform(3, 5))
            if judgeProduct(driver) == True:
                print '商品不存在'
                continue
            tmallCode(driver, wait,EC)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-detail-hd')))  # 显性等待
            except Exception as e:
                print '显性未加载成功---%s' % e

            time.sleep(random.randint(4,5)) #这里得让他睡眠一下，否则第二页开始会报错(加载数据)

            # driver.implicitly_wait(30) #隐性等待30秒，如果30之内页面加载完毕，往下执行，否则超时会报错，需要处理
            html =driver.page_source  #这是一面的页面内容
            # print '源码内容----%s'%html
            print ('等待中。。。%s'%k)
            if 'tmall' in driver.current_url:
                detailURL = 'https://detail.tmall.com/item.htm?id='+str(ownShopID['shopID'][k])
            else:
                detailURL = 'https://item.taobao.com/item.htm?id='+str(ownShopID['shopID'][k])
            try:
                doc = pq(html)

                if WhetherYuShou(doc) == False:
                    print '-----不是预售-----跳过'
                    continue

                # TODO:XDF 这里需要注意一下，src图片链接可以不丰在https，需要自己手动拼接
                mainPics = doc.find('#J_ImgBooth').attr('src')
                if 'https:' in mainPics:
                    mainPic = mainPics
                else:
                    mainPic = 'https:'+mainPics

                # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）
                # if 'xmlns' in doc.find('.tb-detail-hd').html():
                #     print ('存在xmlns--%s'%doc.find('.tb-detail-hd').html())
                #     titles = doc.find('.tb-detail-hd').html()
                #     selector = etree.HTML(titles)
                #     title = str(selector.xpath('//h1/text()')[0]).replace('\r\n','').replace(' ','').replace('\n','').replace('\t','')
                #     print (title)
                # else:
                #     title = doc.find('#detail .tb-detail-hd h1').text().replace('\r\n', '').replace(' ', '').replace('\n', '').replace('\t','')

                presellPrice = clearToReplaceData(doc.find('#J_PromoBox').text(),1)
                address = doc.find('#J_deliveryAdd').text()
                #收藏人数

                popularity = clearToReplaceData(doc.find('#J_CollectCount').text(),0)

                reserveCount = clearToReplaceData(doc.find('.tb-wrt-guc').text(),3)

                paymentDate = doc.find('.J_step2Time').text().split('~')
                # driver.save_screenshot('RecordProcess/ceShiprocess%s.png' % k)
                try:
                    paymentBeginDate = paymentDate[0]
                    paymentFinishDate = paymentDate[1]
                except Exception as e:
                    print ('miss2---%s'%e)

                detailPrice = clearToReplaceData(doc.find('#J_StrPriceModBox .tm-price').text(),5)
                categoryIdContent = clearToReplaceData(str(doc.find('#J_ZebraPriceDesc').attr('mdv-cfg')),2)
                print (categoryIdContent)

                spuIds = 'TShop.Setup\((.*?)\);'
                apiData = re.findall(spuIds, html, re.S)[0]
                datas = json.loads(apiData)
                brandId = datas['itemDO']['brandId']
                categoryId = datas['itemDO']['categoryId']
                rootCatId = datas['itemDO']['rootCatId']
                spuId = datas['itemDO']['spuId']
                title = datas['itemDO']['title']
                sellerId = datas['rateConfig']['sellerId']
                shopID = sellerId
                shopName = doc.find('.slogo-shopname').text()
                categoryName = categoryNamesQly(TreasureID)

                # print '类型---%s'%categoryId
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

                try:
                    ShopURL = str(doc.find('.shopLink').attr('href'))
                    if len(ShopURL):
                        ShopURL = clearToReplaceData(ShopURL,4)
                    else:
                        ShopURL = '-'
                except Exception as e:
                    print e

                print TreasureID, shopName,categoryName, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), detailPrice, address, detailURL, title, mainPic, presellPrice, popularity #, paymentBeginDate, paymentFinishDate, reserveCount

                # product = {
                #     'title': title,
                #     'ID': ID,
                #     'addRess': address,
                #     'shopName': shopName,
                #     'mainPic': mainPic,
                #     'detailURL': detailURL,
                #     'detailPrice': detailPrice,
                #     'popularity': popularity,
                #     'reserveCount': reserveCount,
                #     'paymentBeginDate': paymentBeginDate,
                #     'paymentFinishDate': paymentFinishDate,
                #     'presellPrice': presellPrice,
                #     'categoryId': int(categoryId),
                #     'categoryName': categoryName,
                #     'spiderTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'ShopID':shopID,
                #     'brandId':brandId,
                #     'brand':brand,
                #     'spuId':spuId,
                #     'rootCatId':int(rootCatId),
                #     'StyleName':StyleName,
                #     'EffectiveTime':'',
                #     'ReservationStatus':0,
                #     'ReNewPreSaleTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'JHSReNewTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'CollectionNum':0,
                #     'JHSmodifyTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'ItemName':'',
                #     'EvaluationTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'NCategory_Name':'',
                #     'Is_Search':1,
                #     'NStyleName':'',
                #     'NewstPrice':0,
                #     'SkuModifyDate':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'TempleteTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     'EvaluationScores':float(EvaluationScores),
                #     'URL_NO':URL_NO,
                #     'ShopURL':ShopURL,
                #     'sellerId':sellerId
                # }
                StartTime = datetime.datetime.strptime(str(allShopName['YuShouStartTime'][0]), '%Y-%m-%d %H:%M:%S')

                EndTime = datetime.datetime.strptime(str(allShopName['YuShouEndTime'][0]), '%Y-%m-%d %H:%M:%S')
                product = {
                    'title': title,
                    'TreasureID': TreasureID,
                    'addRess': address,
                    'shopName': shopName,
                    'mainPic': mainPic,
                    'detailPrice': detailPrice,
                    'popularity': popularity,
                    'reserveCount': int(reserveCount),
                    'paymentBeginDate': strToDateTime(str(paymentBeginDate), 'fiveColonTypes'),
                    'paymentFinishDate': strToDateTime(str(paymentFinishDate), 'fiveColonTypes'),
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
                    'CollectionNum': int(popularity),
                    'ItemName': '',
                    'NCategory_Name': '',
                    'Is_Search': 1,
                    'NStyleName': ' ',
                    'NewstPrice': 0,
                    'EvaluationScores': float(EvaluationScores),
                    'URL_NO': URL_NO,
                    'ShopURL': ShopURL,
                    'sellerId': sellerId,
                    'productState': '1',
                    'JHSmodifyTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'modifyTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'StartTime': StartTime,
                    'EndTime': EndTime,
                    'detailURL': detailURL
                }

                if str(dbChoice['tmallYuShouSql'][0]) == 'Mongodb':

                    if TreasureID in BaseInfo:
                        UpdateTmallBaseInfoTB(product)
                        UpdateTmallYuShouTB(product)

                    else:
                        saveTmallGivenIDToYuShouTB(product)
                        saveTmallBaseInfoTBToMongodb(product)
                else:
                    if judgeHaveTreasureID(product) == True:
                        print '存在------'
                        InsertOrUpdateBaseInfo(product,'Update')
                        print '更新成功------'
                    else:
                        print '不存在吧------'
                        InsertOrUpdateBaseInfo(product, 'Insert')
                        print '存入成功------'
                    # InsertPreSaleNew(product)

            except Exception as e:
                print ('error---%s'%e)

        break

    print ('---------------名字----1')

    time.sleep(random.randint(4,7))
    driver.close()
    driver.quit()




def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

if __name__ == '__main__':
    # tmallDataSEL()
    tmallGivenIDAndShopName()


































