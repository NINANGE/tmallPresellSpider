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
import urllib, urllib2
import base64
import json
import traceback
import random
from connectModel import Mssql, InsertPreSaleNew, InsertShopTemplete, InsertOrUpdateBaseInfo, judgeHaveTreasureID,selectAllProductID
from common import tmallCode, categoryNamesQly, styleNames, brandName, evaluationScoreURL,saveTmallGivenIDTB, ownShopID, allShopName, save_img,\
    clearToReplaceData,productNumberTimes,judgeProduct,tmallLogin,JudgeLoginSuccess,judgeProductOff,dbChoice
import os

# 验证接口
url = 'https://v2-api.jsdama.com/upload'

# 和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# TODO:EXP 给定ID和店铺情况
def tmallGivenIDAndShopName():
    # TODO:XDF Chrome欲歌浏览器
    options = webdriver.ChromeOptions()
    # options.add_extension('AdBlock_v3.15.0.crx') # TODO:XDF Chrome欲歌广告过滤插件
    # 设置中文
    options.add_argument('lang=zh_CN.UTF-8')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)  # TODO:XDF 禁止加载图片
    # 更换头部
    options.add_argument(
        'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"')
    # driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')
    driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Downloads/123456/chromedriver')
    wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间

    # TODO:XDF PhantomJS无头浏览器
    # dcap = dict(DesiredCapabilities.PHANTOMJS)
    # dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36")  # 设置user-agent请求头
    # dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
    #
    # print ('即将开始。。。')
    # service_args = []
    # service_args.append('--load-images=no')  ##关闭图片加载
    # service_args.append('--disk-cache=yes')  ##开启缓存
    # service_args.append('--ignore-ssl-errors=true')  ##忽略https错误
    # # #TODO:XDF 针对本地调试
    # driver = webdriver.PhantomJS(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/phantomjs',service_args=service_args,desired_capabilities=dcap)
    # #
    # # # driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)  # TODO:XDF 针对Linux
    # # # TODO:XDF 针对Linux服务器
    # #
    # # driver.implicitly_wait(30)
    # # driver.set_page_load_timeout(30)
    # wait = WebDriverWait(driver, 100, 0.5)  # 表示给browser浏览器一个10秒的加载时间

    #TODO:XDF 火狐浏览器
    # driver = webdriver.Firefox(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/geckodriver')
    # # driver.set_page_load_timeout(30)
    # # driver.implicitly_wait(30)
    # wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间


    print ('等待中。。。')

    while True:

        # for k in range(0, len(ownShopID)):
        for datas in selectAllProductID():
            time.sleep(random.uniform(3, 5))
            driver.get('https://detail.tmall.com/item.htm?id=%s'%str(datas[0]))
            print ('https://detail.tmall.com/item.htm?id=%s'%str(datas[0]))
            TreasureID = str(datas[0])
            time.sleep(random.uniform(1, 2))
            try:
                tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
                time.sleep(random.uniform(3, 5))
                tmallCode(driver, wait,EC)
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print 'driver get error---%s' % e
                continue

            if (judgeProduct(driver) == True) or (judgeProductOff(driver) == True):# or ('item.taobao.com' in driver.current_url):
                print '商品不存在'
                continue
            print '---商品存在---%s'%driver.current_url
            # tmallCode(driver, wait,EC)
            if 'item.taobao.com' in driver.current_url:
                print '-----当前为淘宝产品页面-----'
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'attributes-list')))  # 显性等待
                    time.sleep(random.randint(1, 3))
                except Exception as e:
                    print '显性未加载成功---%s' % e
                    continue
                # 判断是否已登录
                JudgeLoginSuccess(driver, UnexpectedAlertPresentException, ActionChains)
                time.sleep(random.uniform(1, 2))
                html = driver.page_source
                if 'tmall' in driver.current_url:
                    detailURL = 'https://detail.tmall.com/item.htm?id='+str(datas[0])
                else:
                    detailURL = 'https://item.taobao.com/item.htm?id='+str(datas[0])
                try:
                    doc = pq(html)
                    # TODO:XDF 这里需要注意一下，src图片链接可以不丰在https，需要自己手动拼接
                    mainPics = doc.find('#J_ImgBooth').attr('src')
                    if 'https:' in mainPics:
                        mainPic = mainPics
                    else:
                        mainPic = 'https:' + mainPics

                    if 'xmlns' in doc.find('.tb-main-title').html():
                        print ('存在xmlns--%s' % doc.find('.tb-main-title').html())
                        titles = doc.find('.tb-detail-hd').html()
                        selector = etree.HTML(titles)
                        title = str(selector.xpath('text()')[0]).replace('\r\n', '').replace(' ', '').replace('\n','').replace('\t', '')
                        print (title)
                    else:
                        title = str(doc.find('.tb-main-title').attr('data-title')).replace('\r\n', '').replace(' ','').replace('\n', '').replace('\t', '')
                    popularity = clearToReplaceData(doc.find('.J_FavCount').text(), 0)#
                    categoryId = doc.find('#J_Pine').attr('data-catid')
                    rootCatId = doc.find('#J_Pine').attr('data-rootid')
                    sellerId = doc.find('#J_Pine').attr('data-sellerid')
                    shopID = doc.find('#J_Pine').attr('data-shopid')
                    shopName = doc.find('.shop-name-title').text()
                    categoryName = categoryNamesQly(TreasureID)

                    styleData = doc.find('.attributes-list').children().items()
                    # 风格
                    StyleName = styleNames(styleData)

                    brandData = doc.find('.attributes-list').children().items()
                    # 品牌
                    brand = brandName(brandData)
                    address = doc.find('#J-From').text()

                    try:
                        ShopURL = doc.find('.slogo-shopname').attr('href')
                        if len(ShopURL):
                            ShopURL = clearToReplaceData(ShopURL, 4)
                        else:
                            ShopURL = '-'
                    except Exception as e:
                        print e
                    platform = '淘宝'
                    brandId = ''
                    spuId = ''
                    EvaluationScores = 0
                    URL_NO = ''
                    product = {
                        'title': title,
                        'TreasureID': TreasureID,
                        'addRess': address,
                        'shopName': shopName,
                        'mainPic': mainPic,
                        'detailURL': detailURL,
                        'detailPrice': '',#detailPrice,
                        'popularity': popularity,
                        'reserveCount': '',#reserveCount,
                        'presellPrice': '',#presellPrice,
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
                        'ReNewPreSaleTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'JHSReNewTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'CollectionNum': 0,
                        'JHSmodifyTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'ItemName': '',
                        'EvaluationTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'NCategory_Name': '',
                        'Is_Search': 1,
                        'NStyleName': '',
                        'NewstPrice': 0,
                        'SkuModifyDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'TempleteTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'EvaluationScores': float(EvaluationScores),
                        'URL_NO': URL_NO,
                        'ShopURL': ShopURL,
                        'sellerId': sellerId,
                        'NumTimes': '第' + str(productNumberTimes(TreasureID) + 1) + '次爬取',
                        'platform':platform
                    }

                    saveTmallGivenIDTB(product)

                except Exception as e:
                    print '淘宝数据加载出错啦。。直接略过。%s'%e

            else:

                try:
                    wait.until(EC.presence_of_element_located((By.ID, 'J_AttrUL')))  # 显性等待
                    time.sleep(random.randint(1, 3))
                except Exception as e:
                    print '显性未加载成功---%s' % e
                    continue

                # 判断是否已登录
                JudgeLoginSuccess(driver,UnexpectedAlertPresentException,ActionChains)
                time.sleep(random.uniform(1, 2))

                # driver.implicitly_wait(30) #隐性等待30秒，如果30之内页面加载完毕，往下执行，否则超时会报错，需要处理
                html = driver.page_source  # 这是一面的页面内容

                # print '源码内容----%s'%html
                if 'tmall' in driver.current_url:
                    detailURL = 'https://detail.tmall.com/item.htm?id='+str(datas[0])
                else:
                    detailURL = 'https://item.taobao.com/item.htm?id='+str(datas[0])
                try:
                    doc = pq(html)

                    # TODO:XDF 这里需要注意一下，src图片链接可以不丰在https，需要自己手动拼接
                    mainPics = doc.find('#J_ImgBooth').attr('src')
                    if 'https:' in mainPics:
                        mainPic = mainPics
                    else:
                        mainPic = 'https:' + mainPics

                    # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）

                    presellPrice = clearToReplaceData(doc.find('#J_PromoBox').text(), 1)
                    address = doc.find('#J_deliveryAdd').text()
                    # 收藏人数
                    popularity = clearToReplaceData(doc.find('#J_CollectCount').text(), 0)

                    reserveCount = clearToReplaceData(doc.find('.tb-wrt-guc').text(), 3)
                    detailPrice = clearToReplaceData(doc.find('#J_StrPriceModBox .tm-price').text(), 5)
                    categoryIdContent = clearToReplaceData(str(doc.find('#J_ZebraPriceDesc').attr('mdv-cfg')), 2)
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
                    print '类目名称------%s'%categoryName

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
                            ShopURL = clearToReplaceData(ShopURL, 4)
                        else:
                            ShopURL = '-'
                    except Exception as e:
                        print e
                    print '你大爷的------123'
                    print TreasureID, shopName, categoryName, address, detailURL, title, mainPic, presellPrice, popularity  # , paymentBeginDate, paymentFinishDate, reserveCount
                    platform = '天猫'
                    product = {
                        'title': title,
                        'TreasureID': TreasureID,
                        'addRess': address,
                        'shopName': shopName,
                        'mainPic': mainPic,
                        'detailURL': detailURL,
                        'detailPrice': detailPrice,
                        'popularity': popularity,
                        'reserveCount': reserveCount,
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
                        'ReNewPreSaleTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'JHSReNewTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'CollectionNum': 0,
                        'JHSmodifyTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'ItemName': '',
                        'EvaluationTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'NCategory_Name': '',
                        'Is_Search': 1,
                        'NStyleName': '',
                        'NewstPrice': 0,
                        'SkuModifyDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'TempleteTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'EvaluationScores': float(EvaluationScores),
                        'URL_NO': URL_NO,
                        'ShopURL': ShopURL,
                        'sellerId': sellerId,
                        'NumTimes':'第'+str(productNumberTimes(TreasureID)+1)+'次爬取',
                        'platform': platform
                    }
                    if str(dbChoice['EnemySpiderSql'][0]) == 'Mongodb':
                        saveTmallGivenIDTB(product)
                    else:
                        print '这是保存到sql server'

                except Exception as e:
                    print ('error-直接略过--%s' % e)
                    continue

        break

    print ('---------------名字----1')

    time.sleep(random.randint(4, 7))
    driver.close()
    driver.quit()

def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))




if __name__ == '__main__':
    tmallGivenIDAndShopName()



































