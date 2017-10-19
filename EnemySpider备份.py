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
import random
from connectModel import Mssql, InsertPreSaleNew, InsertShopTemplete, InsertOrUpdateBaseInfo, judgeHaveTreasureID,selectAllProductID
from common import tmallCode, categoryNamesQly, styleNames, brandName, evaluationScoreURL, \
    saveTmallGivenIDTB, ownShopID, allShopName, save_img, clearToReplaceData,productNumberTimes,judgeProduct
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
    driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')

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
    # #TODO:XDF 针对本地调试
    # driver = webdriver.PhantomJS(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/phantomjs',service_args=service_args,desired_capabilities=dcap)
    # #
    # # # driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)  # TODO:XDF 针对Linux
    # # # TODO:XDF 针对Linux服务器
    # wait = WebDriverWait(driver, 60, 0.5)  # 表示给browser浏览器一个10秒的加载时间
    # #
    # driver.implicitly_wait(30)
    # driver.set_page_load_timeout(30)
    print ('等待中。。。')

    while True:

        # for k in range(0, len(ownShopID)):
        for datas in selectAllProductID():

            driver.get('https://detail.tmall.com/item.htm?id=%s'%str(datas[0]))
            print ('https://detail.tmall.com/item.htm?id=%s'%str(datas[0]))
            TreasureID = str(datas[0])
            JudgeLoginSuccess(driver)

            tmallLogin(driver)

            time.sleep(random.uniform(3, 5))
            if judgeProduct(driver) == True:
                print '商品不存在'
                continue
            tmallCode(driver, wait)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-detail-hd')))  # 显性等待
            except Exception as e:
                print '显性未加载成功---%s' % e

            time.sleep(random.randint(4, 5))  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)

            # driver.implicitly_wait(30) #隐性等待30秒，如果30之内页面加载完毕，往下执行，否则超时会报错，需要处理
            html = driver.page_source  # 这是一面的页面内容
            # print '源码内容----%s'%html
            # print ('等待中。。。%s' % k)
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
                print '你大爷的------000'
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
                print '你大爷的------456'
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
                    'NumTimes':'第'+str(productNumberTimes(TreasureID)+1)+'次爬取'
                }

                saveTmallGivenIDTB(product)

                # if judgeHaveTreasureID(product) == True:
                #     print '存在------'
                #     InsertOrUpdateBaseInfo(product,'Update')
                #     print '更新成功------'
                # else:
                #     print '不存在吧------'
                #     InsertOrUpdateBaseInfo(product, 'Insert')
                #     print '存入成功------'
                # # InsertPreSaleNew(product)

            except Exception as e:
                print ('error---%s' % e)

        break

    print ('---------------名字----1')

    time.sleep(random.randint(4, 7))
    driver.close()
    driver.quit()

def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

"""
    判断是否已登录，未登录则先登录（这也是为了预防后面出现滑动验证），请知悉，反之，直接略过
"""
def JudgeLoginSuccess(driver):
    while True:
        time.sleep(2)
        if loginBtnExistence(driver) == True:
            print '还未登录'
            driver.find_element_by_xpath('//*[@id="login-info"]/a[1]').click()
            time.sleep(2)
            tmallLogin(driver)
        else:
            print '已登录'
            break

        """
            判断是否存在‘请登录’，存在就点击登录，反之，略过
        """

def loginBtnExistence(driver):
    try:
        if driver.find_element_by_xpath('//*[@id="login-info"]/a[1]').text == '请登录':
            loginBtn = True
        else:
            loginBtn = False
    except Exception as e:
        print 'loginMessage----%s' % e
        loginBtn = False
    return loginBtn

#中途可能需要登录
def tmallLogin(driver):
    if 'login.tmall' in str(driver.current_url):
        print ('需要登录----')
        # # TODO:XDF: 这是设置窗口大小（仅仅针对phantomjs无头浏览器，其它会报错）

        # driver.delete_all_cookies()
        driver.switch_to.frame("J_loginIframe")
        while True:
            time.sleep(random.randint(5,7))
            # TODO:XDF:1 因为无头浏览器是无界面的，所以只能通过截图来查看过程，下面同理（仅仅针对phantomjs无头浏览器，其它会报错）
            # driver.save_screenshot('RecordProcess/process1.png')

            if judgeHaveLogin(driver) == True:
                print '点击登录啦'
                driver.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
                print '------点击登录--------'
            else:
                print '----NO_Click----'

            time.sleep(2)
            # TODO:XDF:2
            driver.find_element_by_name("TPL_username").clear()
            driver.find_element_by_name("TPL_username").send_keys("13672456277")
            time.sleep(random.uniform(3, 6))
            driver.find_element_by_name("TPL_password").clear()
            driver.find_element_by_name("TPL_password").send_keys("248552ZZN")
            time.sleep(random.uniform(3, 5))

            if codeSEL(driver) == True:
                dragger = driver.find_element_by_class_name("nc_bg")

                action = ActionChains(driver)
                # action.click_and_hold(dragger).perform()  # 鼠标左键按下不放
                action.click_and_hold(on_element=dragger).perform()
                print '456'
                for index in range(299):
                    try:
                        action.move_by_offset(random.uniform(5,15), random.uniform(1,4)).perform()  # 平行移动鼠标
                    except UnexpectedAlertPresentException:
                        print '滑动出错'
                        break
                    action.reset_actions()
                    # time.sleep(random.uniform(0.01,0.05))  # 等待停顿时间
                    time.sleep(random.randint(20, 70) / 100)


                # action.move_by_offset(258,0)
                action.release().perform()


            time.sleep(1.5)
            # driver.save_screenshot('RecordProcess/codeLogin1.png')
            # TODO:XDF:3
            driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()
            # TODO:XDF:4
            print ('login success')
            time.sleep(2)
            if sliderCode(driver) == False:
                break

# def codeSEL(driver):
#     try:
#         driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')
#         codeTrue = True
#     except Exception as e:
#         print 'error--%s' % e
#         codeTrue = False
#     return codeTrue

def codeSEL(driver):
    try:
        if driver.find_element_by_xpath('//*[@id="nc_1__scale_text"]/span').text:
            codeTrue = True
            print '有滑块，需要验证-----'
        else:
            codeTrue = False

    except Exception as e:
        print 'error--%s' % e
        codeTrue = False
    return codeTrue

#判断是否包含‘密码登录’字样，如果有需要执行点击，反之不需要
def judgeHaveLogin(driver):
    try:
        if driver.find_element_by_xpath('//*[@id="J_QRCodeLogin"]/div[@class="login-links"]/a[@class="forget-pwd J_Quick2Static"]').text:
            a = True
            print '内容---%s' % driver.find_element_by_xpath('//*[@id="J_QRCodeLogin"]/div[@class="login-links"]/a[@class="forget-pwd J_Quick2Static"]').text
        else:
            print '内容2---%s' % driver.find_element_by_xpath('//*[@id="J_QRCodeLogin"]/div[@class="login-links"]/a[@class="forget-pwd J_Quick2Static"]').text
            a = False
    except Exception as e:
        print 'loginError ---%s'%e
        a = False
    return a


#判断是否滑动验证失败
def sliderCode(driver):
    try:
        if driver.find_element_by_class_name("error"):
            a = True
        else:
            a = False
    except Exception as e:
        print '滑块验证失败---%s'%e
        a = False
    return a


if __name__ == '__main__':
    tmallGivenIDAndShopName()



































