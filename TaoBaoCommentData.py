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
from connectModel import Mssql,InsertPreSaleNew,InsertShopTemplete,InsertOrUpdateBaseInfo,judgeHaveTreasureID
from common import tmallLogin,tmallCode,categoryNamesQly,styleNames,brandName,evaluationScoreURL,saveTmallGivenIDTB,ownShopID,allShopName,save_img,clearToReplaceData,df,\
    saveTmallGivenIDToYuShouTB,WhetherYuShou,judgeProduct,JudgeLoginSuccess,dbChoice
import os


#验证接口
url = 'https://v2-api.jsdama.com/upload'

#和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#TODO:EXP 给定ID和店铺情况
def getTaoBaoCommentData():
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

    driver = webdriver.Chrome(executable_path=r'/Users/zhuoqin/Downloads/123456/chromedriver')  # chrome_options=options,
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
    driver.maximize_window()
    driver.get('https://item.taobao.com/item.htm?id=541901945837')
    BounceCommentLogin(driver)
    tmallLogin(driver, UnexpectedAlertPresentException, ActionChains)

    time.sleep(random.uniform(3, 5))

    tmallCode(driver, wait, EC)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'attributes-list')))  # 显性等待
    except Exception as e:
        print '显性未加载成功---%s' % e



    time.sleep(random.randint(5, 6))  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)
    doc = pq(driver.page_source)
    shopName = doc.find('.shop-name-link').text()
    Title = doc.find('#J_Title .tb-main-title').attr('data-title')

    # print '类型---%s'%categoryId
    styleData = doc.find('.attributes-list').children().items()
    # 风格
    StyleName = styleNames(styleData)
    # 因为styleData是一个迭代器，被循环完的就会被释放掉（品牌有可能在查找风格的时候循环过去了，已经被释放掉了），所以这里得重新赋值数据源
    brandData = doc.find('.attributes-list').children().items()
    # 品牌
    brand = brandName(brandData)

    categoryName = categoryNamesQly('541901945837')

    spuIds = "shopId           : '(.*?)',"
    shopId = re.findall(spuIds, driver.page_source, re.S)[0]

    sellerIds = "sellerId         : '(.*?)',"
    sellerId = re.findall(sellerIds, driver.page_source, re.S)[0]
    categoryIds = " cid           : '(.*?)',"
    categoryId = re.findall(categoryIds, driver.page_source, re.S)[0]
    print '店铺名-----%s'%shopName,Title,StyleName,brand,categoryName,shopId,sellerId,categoryId




    time.sleep(random.randint(15, 20))  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)

    time.sleep(random.randint(4, 5))  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)

    js ="var q = document.documentElement.scrollTop = 1000"
    driver.execute_script(js)

    time.sleep(random.uniform(3, 5))

    driver.find_element_by_xpath('//*[@id="J_TabBar"]/li[2]/a').click()
    time.sleep(random.uniform(3, 5))

    BounceCommentLogin(driver)

    dragger = driver.find_element_by_class_name("sorting")
    action = ActionChains(driver)
    action.move_to_element(dragger)

    time.sleep(random.uniform(3, 5))

    action.click_and_hold(on_element=dragger).perform()

    driver.find_element_by_xpath('//*[@id="reviews"]/div/div/div/div/div/div[1]/div[2]/div/ul/li[2]').click()

    # print '源码-----%s'%driver.page_source

    action.release()
    time.sleep(random.uniform(5, 8))

    driver.delete_all_cookies()

    print '测试一下吧-------1'
    time.sleep(random.uniform(5, 8))

    while True:
        BounceCommentLogin(driver)
        LoginCodeVerificatin(driver)
        time.sleep(random.uniform(5, 8))
        doc = pq(driver.page_source)

        print '源码吧----%s'%doc.find('.J_KgRate_ReviewItem.kg-rate-ct-review-item').text()

        for data in doc.find('.J_KgRate_ReviewItem.kg-rate-ct-review-item').items():

            RateDate = strToDateTime(str(data.find('.tb-r-act-bar .tb-r-info .tb-r-date').text()), 'fiveAllWordTypes')
            TaoBaoComment = data.find('.tb-rev-item .J_KgRate_ReviewContent.tb-tbcr-content ').text()
            PhotoItems = data.find('.tb-rev-item-media .kg-photo-viewer-thumb-bar.tb-tbcr-mt .photo-item').items()
            auctionSku = data.find('.tb-r-act-bar .tb-r-info').text()

            #追加内容
            appendContent = data.find('.tb-rev-item tb-rev-item-append .tb-rev-item.tb-rev-item-append .J_KgRate_ReviewContent.tb-tbcr-content ').text()
            if '颜色分类：' in auctionSku:
                auctionSku = '颜色分类：'+auctionSku.split('颜色分类：')[-1]
            else:
                auctionSku = '-'

            Phostos = []
            for photo in PhotoItems:
                # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）
                if 'xmlns' in photo.html():
                    selector = etree.HTML(photo.html())
                    Img = str(selector.xpath('//img/@src')[0])
                    if 'https:' not in Img:
                        Image = 'https:' + Img.replace('40x40', '400x400')
                    else:
                        Image = Img
                    Phostos.append(Image)

                else:
                    print '**************不存在xmlns啦*****************'

                # print '相片----%s'%Image#photo.html()
            print '测试一下吧------', data.find('.from-whom').text(), RateDate,TaoBaoComment,Phostos,auctionSku,appendContent
        # print '源码-----%s' %doc.find('.tb-revbd').text()
        time.sleep(random.uniform(5,8))
        driver.find_element_by_xpath('//*[@class="pg-next"]').click()
        time.sleep(random.uniform(5, 8))


#把字符串转成时间
def strToDateTime(strs,types):
    if types == 'threLineTypes':
        return datetime.datetime.strptime(strs,'%Y-%m-%d')
    elif types == 'threcolonTypes':
        return datetime.datetime.strptime(strs, '%Y:%m:%d')
    elif types == 'threWordTypes':
        return datetime.datetime.strptime(strs, '%Y年%m月%d日')
    elif types == 'fiveLineTypes':
        return datetime.datetime.strptime(strs, '%Y-%m-%d %H:%M')
    elif types == 'fiveColonTypes':
        return datetime.datetime.strptime(strs, '%Y.%m.%d %H:%M')
    elif types == 'fiveWordTypes':
        return datetime.datetime.strptime(strs, '%Y年%m月%d日 %H时%M分')
    elif types == 'fiveAllWordTypes':
        return datetime.datetime.strptime(strs, '%Y年%m月%d日 %H:%M')
    elif types == 'sixLineTypes':
        return datetime.datetime.strptime(strs, '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(strs, '%Y年%m月%d日 %H时%M分%S秒')

#是否弹出登录框
def BounceCommentLogin(driver):
    if CommentLogin(driver) == True:

        time.sleep(2)
        # TODO:XDF:2
        print '进来了*******2'
        driver.find_element_by_name("TPL_username").clear()
        driver.find_element_by_name("TPL_username").send_keys("13672456277")
        time.sleep(random.uniform(3, 6))
        driver.find_element_by_name("TPL_password").clear()
        driver.find_element_by_name("TPL_password").send_keys("248552ZZN")

        time.sleep(random.uniform(3, 5))
        driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()
        time.sleep(random.uniform(8, 12))
        driver.switch_to.default_content()

#判断是下是否需要登录
def CommentLogin(driver):
    print '弹出了窗口'
    try:
        print '弹出了窗口********'
        driver.switch_to.frame("sufei-dialog-content")
        print '弹出了登录窗口----%s'%driver.find_element_by_xpath('//*[@id="page2"]').text

        if '登录名' in driver.find_element_by_xpath('//*[@id="page2"]').text:
            code = True
        else:
            code = False
    except Exception as e:
        code = False
        print '弹出了窗口********你大爷的---%s'%e
        driver.switch_to.default_content()
    return code

def CodeVerification(driver):
    try:
        print '这里需要验证码验证*************1'
        driver.switch_to.frame('sufei-dialog-content')
        print '这里需要验证码验证*************2'
        print '验证登录----%s' % driver.find_element_by_xpath('//*[@class="wrap"]').text
        if '系统发现您的网络环境有异常，为保证正常使用，请完成验证。' in driver.find_element_by_xpath('//*[@class="wrap"]').text:
            code = True
        else:
            code = False
    except Exception as e:
        print '验证码错误-----%s'%e
        code = False
        driver.switch_to.default_content()
    return code

def LoginCodeVerificatin(driver):
    try:
        detailCode = pq(driver.page_source)
        imageURL = detailCode.find('#J_CheckCodeImg1').attr('src')

        save_img(imageURL, 'picDic/TaoBaoPicDic.png')
        driver.find_element_by_xpath('//*[@id="J_CodeInput"]').clear()

        # 设置要请求的头，让服务器不会以为你是机器人
        headers = {
            'UserAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        f = open('picDic/TaoBaoPicDic.png', 'rb')  # 二进制打开图文件 CrawlResult/1111.png
        ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        f.close()
        values = {"softwareId": 7616, "softwareSecret": "p2AXUYMaTDcV72UoULYQQt7ubVPwTUXXlXIw7A3S",
                  "username": "ZZN_1993", "password": "@ZHOUZEnan1993", "captchaData": ls_f,
                  "captchaType": 1017,
                  "captchaMinLength": 4, "captchaMaxLength": 8}  # @ZHOUZEnan1993
        data = json.dumps(values)
        # 发送一个http请求
        request = urllib2.Request(url=url, headers=headers, data=data)
        # 获得回送的数据
        response = urllib2.urlopen(request)

        datas = eval(response.read())
        print 'data---%s---%s--%s--%s' % (
        datas['code'], datas['message'], datas['data']['recognition'], datas['data']['captchaId'])
        code = str(datas['data']['recognition']).replace('\r\n', '').replace(' ', '').replace('\n', '').replace('\t',
                                                                                                                '')
        driver.find_element_by_xpath('//*[@id="J_CodeInput"]').send_keys(code)
        time.sleep(random.uniform(5, 8))
        driver.find_element_by_xpath('//*[@id="J_submit"]').click()
        time.sleep(random.uniform(5,8))
        print '测试结束************'
        driver.switch_to.default_content()

    except Exception as e:
        print '验证码登录错了子卡-------%s'%e


if __name__ == '__main__':
    getTaoBaoCommentData()
































