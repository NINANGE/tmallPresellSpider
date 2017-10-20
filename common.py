# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
import time
import datetime
import requests
from pyquery import PyQuery as pq
import pymongo
from lxml import etree
import pandas as pd
import re
import urllib,urllib2
import base64
import json
import random

#验证接口
url = 'https://v2-api.jsdama.com/upload'

ownShopID = pd.read_csv('allShopID.csv')

allShopName = pd.read_excel('allShopName.xlsx')

df = pd.read_excel('sell815.xlsx')

dbChoice = pd.read_csv('dbChoiceType.csv')

#和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# client = pymongo.MongoClient('localhost',27017)

client = pymongo.MongoClient('192.168.3.172',27017)

db = client.TmallYuShouDB
givenIDTable = db.TmallGivenIDTB

givenIDToTmallYuShouTable = db.TmallYuShouTB

TmallYuShouBaseInfoTable = db.TmallYuShouBaseInfoTB

tmallYuShouTable = db.TmallYSDetailTB

#下载图片
def save_img(imgURL,filename):
    # 下载图片，并保存到文件夹中
    try:
        urllib.urlretrieve(imgURL, filename=filename)

    except IOError as e:
        print '文件操作失败', e
    except Exception as e:
        print 'download fail*****%s'%e


#通过请求获取类目
def categoryNamesQly(TreasureID):
    url = 'http://plugin.qly360.com/productDetailList.do?spid='+TreasureID

    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()

    babyCategoryInfo = json.loads(res)
    print babyCategoryInfo
    for data in babyCategoryInfo:
        if '-' in data['category']:
            # 类目
            category = data['category'].encode("utf-8")
            categoryName = category.split('-')[-1]

        else:
            categoryName = '-'

        # time_local = data['delist'] / 1000
        # time_local = time.localtime(time_local)
        # offTime = time.strftime("%Y-%m-%d %H:%M:%S", time_local) #这是产品下架时间，暂且忽略
    return categoryName

#TODO:XDF 验证码验证（通过打码平台）
def tmallCode(driver,wait,EC):
    if 'sec.taobao.com' in driver.current_url:
        while True:
            time.sleep(random.uniform(2,4))
            print '需要验证码'
            # wait.until(EC.presence_of_element_located((By.ID, 'checkcodeImg')))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'main')))
            print '----查找图片----'
            time.sleep(random.uniform(2, 4))
            detailCode = pq(driver.page_source)

            if fangWenGuoKuai(detailCode) == True:
                content = '访问过快'
                break

            picURL = detailCode.find('#checkcodeImg').attr('src')

            if 'https:' in picURL:
                imageURL = picURL
            else:
                imageURL = 'https:' + picURL
            print '图片地址---%s' % imageURL
            save_img(imageURL, 'picDic/picDic.png')

            driver.find_element_by_xpath('//*[@id="checkcodeInput"]').clear()

            # 设置要请求的头，让服务器不会以为你是机器人
            headers = {'UserAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
            f = open('picDic/picDic.png', 'rb')  # 二进制打开图文件 CrawlResult/1111.png
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
            print 'data---%s---%s--%s--%s' % (datas['code'], datas['message'], datas['data']['recognition'], datas['data']['captchaId'])
            code = str(datas['data']['recognition']).replace('\r\n', '').replace(' ', '').replace('\n', '').replace('\t','')
            driver.find_element_by_xpath('//*[@id="checkcodeInput"]').send_keys(code)

            driver.find_element_by_xpath('//*[@id="query"]/div[@class="submit"]/input').click()
            time.sleep(2)
            print '测试结束************'
            # continue
            detailCode = pq(driver.page_source)
            if judgeProdctCode(detailCode) == True:
                print '验证码错误，继续下载识别'
            elif judgeProdctCode(detailCode) == 'codeMiss':
                print '验证码正确-----'
                content = '验证码正确'
                break

            else:
                print '验证成功，跳出。。。'
                content = '验证码正确'
                break
        return content

#有可能访问过快，验证码无法显示出来
def fangWenGuoKuai(detailCode):
    try:
        if '访问太快了,请休息一下吧' in detailCode.find('.main').text():
            code = True
            print '访问过快'
        else:
            code = False

    except Exception as e:
        print 'codeMiss---%s' % e
        time.sleep(3)
        code = False
    return code

#判断验证错是否验证错误
def judgeProdctCode(detailCode):
    try:
        if detailCode.find('#tip .error').text():
            code = True
            print '验证码错误,不能跳出--------%s'%detailCode.find('#tip .error').text()
        else:
            code = 'codeMiss'

    except Exception as e:
        print 'codeMiss---%s' % e
        time.sleep(3)
        code = False
    return code

#风格
def styleNames(styleData):
    for data in styleData:
        # print '数据-----%s'%data.text()
        if '风格: ' in data.text():
            StyleName = data.text().split(': ')[1]
            print ('风格---------------%s' % StyleName)
            break
        else:
            StyleName = '-'
    return StyleName

#评价描述评分
def evaluationScoreURL(itemId,spuId,sellerId):

    evaluationScoresURL = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId='+str(itemId)+'&spuId='+str(spuId)+'&sellerId='+str(sellerId)
    headers = {
        'UserAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
    request = urllib2.Request(url=evaluationScoresURL.replace(' ', ''),headers=headers) #这里地址可能存在空格  会报错：HTTP Error 505: HTTP Version Not Supported
    # 获得回送的数据
    response = urllib2.urlopen(request)
    result = response.read()
    comments = '.*\((.*?)\)'

    apiData = re.findall(comments, result, re.S)[0]

    datas = json.loads(apiData)
    return datas['dsr']['gradeAvg']

#品牌
def brandName(brandData):
    for data in brandData:
        if '品牌: ' in data.text():
            brand = data.text().split(': ')[1]
            print ('品牌---------------%s' % brand)
            break
        else:
            brand = '-'
    return brand

"""
    判断是否已登录，未登录则先登录（这也是为了预防后面出现滑动验证），请知悉，反之，直接略过
"""
def JudgeLoginSuccess(driver,UnexpectedAlertPresentException,ActionChains):
    while True:
        time.sleep(1)
        if loginBtnExistence(driver) == True:
            print '还未登录'
            driver.find_element_by_xpath('//*[@id="login-info"]/a[1]').click()
            time.sleep(1)
            tmallLogin(driver,UnexpectedAlertPresentException,ActionChains)
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
        print 'loginMessage----%s'%e
        loginBtn = False
    return loginBtn

#中途可能需要登录
def tmallLogin(driver,UnexpectedAlertPresentException,ActionChains):
    if 'login.tmall' in str(driver.current_url):
        print ('需要登录----')
        # # TODO:XDF: 这是设置窗口大小（仅仅针对phantomjs无头浏览器，其它会报错）
        # driver.set_window_size(1800, 1000)
        driver.delete_all_cookies()
        driver.switch_to.frame("J_loginIframe")
        while True:
            time.sleep(random.randint(4,6))
            # TODO:XDF:1 因为无头浏览器是无界面的，所以只能通过截图来查看过程，下面同理（仅仅针对phantomjs无头浏览器，其它会报错）
            # driver.save_screenshot('RecordProcess/process1.png')

            if judgeHaveLogin(driver) == True:
                print '点击登录'
                driver.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
            else:
                print '----NO_Click----'

            time.sleep(2)
            # TODO:XDF:2
            driver.find_element_by_name("TPL_username").clear()
            driver.find_element_by_name("TPL_username").send_keys("13672456277")
            time.sleep(random.uniform(4, 6))
            driver.find_element_by_name("TPL_password").clear()
            driver.find_element_by_name("TPL_password").send_keys("248552ZZN")
            time.sleep(random.uniform(4, 5))

            if codeSEL(driver) == True:
                dragger = driver.find_element_by_class_name("nc_bg")

                action = ActionChains(driver)
                # action.click_and_hold(dragger).perform()  # 鼠标左键按下不放
                action.click_and_hold(on_element=dragger).perform()
                print '456'
                # driver.save_screenshot('RecordProcess/codeProcess1.png')
                for index in range(257):
                    try:
                        action.move_by_offset(random.uniform(5,20), random.uniform(2,8)).perform()  # 平行移动鼠标
                    except UnexpectedAlertPresentException:
                        print '滑动出错'
                        break
                    action.reset_actions()
                    # time.sleep(random.uniform(0.01,0.05))  # 等待停顿时间
                    time.sleep(random.randint(15, 70) / 100)


                # action.move_by_offset(258,0)
                action.release().perform()


            time.sleep(2)
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

#判断这个产品是否已下架
def judgeProductOff(driver):
    try:
        driver.find_element_by_class_name('sold-out-tit')
        a = True
    except Exception as e:
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

#保存到mongodb
def saveTmallGivenIDTB(result):
    try:
        if givenIDTable.insert(result):
            print 'saveTmallGivenTB_Success'
    except Exception as e:
        print 'saveTmallGivenTB_Error...'

def saveTmallGivenIDToYuShouTB(productData):
    try:
        if givenIDToTmallYuShouTable.insert(productData):
            print 'saveTmallYuShouTable_Success'
    except Exception as e:
        print 'saveTmallYuShouTable_Error...'

# 保存天猫数据到mongodb中
def saveTmallBaseInfoTBToMongodb(tmallYuShouProduct):
    try:
        if TmallYuShouBaseInfoTable.insert(tmallYuShouProduct):
            print ('tmallYuShouProduct saveSuccess')
    except Exception as e:
        print ('save_Error...%s' % e)

#预售宝贝详情BaseInfo，如果TreasureID存在，则更新
def UpdateTmallBaseInfoTB(ProductData):
    try:
        if TmallYuShouBaseInfoTable.update({'TreasureID':ProductData['TreasureID']},{'$set':{'presellPrice':ProductData['presellPrice'],'modifyTime':ProductData['modifyTime'],
                                                                                             'spiderTime':ProductData['spiderTime'],'CollectionNum':ProductData['CollectionNum'],
                                                                                             'reserveCount':ProductData['reserveCount']}}):
            print 'update successful*****'
    except Exception as e:
        print 'update error******%s'%e




# 保存天猫数据到mongodb中
def saveTmallYuShouToMongodb(tmallYuShouProduct):
    try:
        if tmallYuShouTable.insert(tmallYuShouProduct):
            print ('tmallYuShouProduct saveSuccess')
    except Exception as e:
        print ('save_Error...%s' % e)

# 更新预售宝贝表  保存天猫数据到mongodb中
def UpdateTmallYuShouTB(tmallYuShouProduct):
    try:
        if tmallYuShouTable.update({'TreasureID':tmallYuShouProduct['TreasureID']},{'$set':{'reserveCount':tmallYuShouProduct['reserveCount'],'presellPrice':tmallYuShouProduct['presellPrice'],
                                                                                             'modifyTime':tmallYuShouProduct['modifyTime'],'CollectionNum':tmallYuShouProduct['CollectionNum'],
                                                                                            'spiderTime': tmallYuShouProduct['spiderTime'],'JHSmodifyTime':tmallYuShouProduct['JHSmodifyTime']}}):
            print 'update successful*****'
    except Exception as e:
        print 'update error******%s'%e



def getProductData():
    try:
        result = tmallYuShouTable.find({},no_cursor_timeout=True)  # 设置no_cursor_timeout = True，永不超时，游标连接不会主动关闭，需要手动关闭
    except Exception as e:
        print 'e-----%s' % e
    return result

#数据清洗之替换
def clearToReplaceData(clearData,state):

    if state == 0:
        clearData = clearData.replace('（', '').replace('人气）', '')
    elif state == 1:
        clearData = clearData.replace('\r\n', '').replace(' ', '').replace('\n', '').replace('¥', '')
    elif state == 2:
        clearData = clearData.replace(' ', '').replace('{','').replace('}', '')
    elif state == 3:
        clearData = clearData.replace('\r\n', '').replace(' ', '').replace('\n','').replace('件','')
    elif state == 4:
        clearData = clearData.replace('//', '')
    elif state == 5:
        clearData = clearData.replace('\r\n', '').replace(' ', '').replace('\n', '')
    return clearData

#产品第几次爬取
def productNumberTimes(TreasureID):
    return givenIDTable.find({'TreasureID':TreasureID}).count()

#如果是预售就更新数据库，如果不是，直接删除
def saveYuShouOrRemove(product,TreasureID):
    try:
        if tmallYuShouTable.insert(product):
            print '是预售，保存成功----%s'%TreasureID
    except Exception as e:
        print '删除或保存出错啦----%s'%TreasureID

# 判断这个产品是否已经不存在了
def judgeProduct(driver):
    try:
        driver.find_element_by_class_name('errorDetail')

        a = True

    except Exception as e:
        # print '产品不存在-----%s' % e
        a = False
    return a

#判断是不是预售
def WhetherYuShou(doc):
    try:
        if '件' in doc.find('.tb-wrt-guc').text():
            a = True
        else:
            a = False

    except Exception as e:
        print '不是预售--出错啦---%s'%e
        a = False
    return a

def ceShiHTML():

    htmlfile = open('ceshiTmallYuShou.html', 'r')  # 以只读的方式打开本地html文件
    htmlpage = htmlfile.read()
    # print type(htmlpage),htmlpage
    doc = pq(htmlpage)
    list = doc('#J_ItemList .product').items()

    # doc = pq(htmlpage)
    spuIds = 'TShop.Setup\((.*?)\);'

    brand = doc.find('.J_EbrandLogo').text()

    styleData = doc.find('#J_AttrUL').children().items()
    shopName = doc.find('.slogo-shopname').text()

    for item in list:
        print '产品数据源----%s'%item
        if str(pq(pq(item.find('.productImg-wrap .productImg')).html()).attr('data-ks-lazyload')) == 'None':
            print '没有------src'
            mainPic = str(pq(pq(item.find('.productImg-wrap .productImg')).html()).attr('src'))
        else:
            print '--------------src'
            mainPic = str(pq(pq(item.find('.productImg-wrap .productImg')).html()).attr('data-ks-lazyload'))
        tmallYuShouProduct = {
            'itemID': "5971b84c1d41c84558080db4",
            'price': item.find('.productPrice').text(),
            'name': item.find('.productTitle').text(),
            'detailURL': 'https:' + str(item.find('.productImg-wrap .productImg').attr('href')),
            'mainPic': 'https:' + mainPic,
            'shopName': item.find('.productShop').text(),
            'payPerson': item.find('.productStatus')('span').html(),
            'TreasureID':item.find('.productStatus').eq(0).children().eq(-1).attr('data-item')

        }
        d = pq(item.find('.productStatus').eq(0)('span'))

        # detailDoc.find('.tb-detail-hd').html()

        print '数据----%s'%item.find('.productStatus').eq(0).children().eq(-1).attr('data-item')
        TreasureID = item.find('.productStatus').eq(0).children().eq(-1).attr('data-item')
        print '编码格式---%s', item.find('.productPrice').text(), item.find('.productTitle').text(), item.find('.productShop').text(),TreasureID

def DBTypechoice():
    if str(dbChoice['tmallYuShouSql'][0]) == 'Mongodb':
        print '相等'
    else:
        print '不相等'


"""
    这里得先进行一下数据迁移
"""
def TmallYuShouMoveData():
    givenIDToTmallYuShouTable.find({})


def TmallYuShouBaseInfoData():
    result = TmallYuShouBaseInfoTable.find({})
    BaseInfoList = []
    for data in result:
        BaseInfoList.append(data['TreasureID'])
    return BaseInfoList


if __name__ == '__main__':

    TmallYuShouBaseInfoData()

    # for i in dbChoice:
    #     print dbChoice[i]['tmallYuShouSql']
    print str(dbChoice['EnemySpiderSql'][0])
    if str(dbChoice['EnemySpiderSql'][0]) == 'Mongodb':
        print '相等'
    else:
        print '不相等'


















