# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import datetime
import requests
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from lxml import etree
import pandas as pd
import re



#和购旗舰店 田田家园家居旗舰店 ikazz旗舰店 卡依莱芙旗舰店 林氏木业旗舰店 林氏旗舰店
import sys
# import importlib
# importlib.reload(sys)
# sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf-8')

client = pymongo.MongoClient('localhost',27017)
db = client.TmallScrapy
table = db.TmallTB2
tableShop = db.TmallTB2

df = pd.read_excel('sell815.xlsx')
allCategory = pd.read_csv('taoBaoCategory.csv')
allShopName = pd.read_excel('allShopName.xlsx')

#TODO:EXP 从首页点击到第二页情况
def tmallDataSEL():
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
    # driver = webdriver.Chrome(chrome_options=options,
    #                           executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')
    # wait = WebDriverWait(driver, 200, 0.5)  # 表示给browser浏览器一个10秒的加载时间


    # TODO:XDF PhantomJS无头浏览器
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36")  # 设置user-agent请求头
    dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

    service_args = []
    service_args.append('--load-images=no')  ##关闭图片加载
    service_args.append('--disk-cache=yes')  ##开启缓存
    service_args.append('--ignore-ssl-errors=true')  ##忽略https错误

    driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs',service_args=service_args, desired_capabilities=dcap) #TODO:XDF 针对Linux

    # driver = webdriver.PhantomJS(executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/phantomjs', desired_capabilities=dcap) #TODO:XDF 针对本地调试
    wait = WebDriverWait(driver, 60, 0.5)  # 表示给browser浏览器一个10秒的加载时间
    #
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)

    try:
        driver.get("https://s.taobao.com/search")
    except:
        driver.save_screenshot('RecordProcess/quit.png')
        driver.quit()
        pass

    time.sleep(1)

    for i in range(0,len(allShopName)):
        print('进来了---%s' % i)
        driver.find_element_by_xpath('//*[@id="q"]').clear()
        time.sleep(2)
        driver.save_screenshot('RecordProcess/begin.png')
        driver.find_element_by_xpath('//*[@id="q"]').send_keys(allShopName['shopName'][i])
        print('地址********%s'%(allShopName['shopName'][i]))
        driver.find_element_by_xpath('//*[@id="J_SearchForm"]/button').click()
        driver.save_screenshot('RecordProcess/ceShiPic%s1.png' % i)
        while True:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'icon-btn-top')))

            time.sleep(5) #这里得让他睡眠一下，否则第二页开始会报错(加载数据)

            html =driver.page_source  #这是一面的页面内容

            doc = pq(html)

            list=doc('#mainsrp-itemlist .items').eq(0).children().items()
            driver.save_screenshot('RecordProcess/ceShiPic%s2.png'%i)
            for data in list:
                print('即将获取内容********')
                Id = str(pq(data.find('.row.row-2.title').html()).attr('data-nid'))

                sureURL = str(pq(data.find('.pic .pic-link.J_ClickStat.J_ItemPicA')).attr('data-href'))
                if 'tmall' in sureURL:
                    detailURL = 'https://detail.tmall.com/item.htm?id='+Id
                else:
                    detailURL = 'https://item.taobao.com/item.htm?id='+Id

                if 'taobao' in sureURL:
                    continue

                now_handle = driver.current_window_handle


                #获取所有窗口句柄

                xpathID = '//*[@id="J_Itemlist_PLink_'+Id+'"]'
                print(now_handle, detailURL,xpathID)
                time.sleep(3)
                # driver.find_element_by_xpath(xpathID).send_keys(Keys.RETURN)
                try:
                    driver.find_element_by_xpath(xpathID).click()
                except Exception as e:
                    print '超时...跳到下一个宝贝%s'%e
                    continue

                # print '测试一下下2'
                all_handle = driver.window_handles
                print ('测试一下下2')
                for handle in all_handle:
                    if handle != now_handle:
                        #输出待选择的窗口句柄
                        print ('***************%s'%handle)
                        driver.switch_to.window(handle)
                        # time.sleep(3)
                        if 'login.tmall' in str(driver.current_url):
                            print ('需要登录----')
                            # time.sleep(2)
                            # driver.implicitly_wait(10)
                            driver.save_screenshot('RecordProcess/loginPic1.png')
                            driver.switch_to.frame("J_loginIframe")
                            time.sleep(5)
                            driver.save_screenshot('RecordProcess/loginPic2.png')
                            loginBtn = driver.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
                            driver.save_screenshot('RecordProcess/loginPic3.png')
                            time.sleep(2)

                            driver.find_element_by_name("TPL_username").send_keys("13672456277")
                            driver.find_element_by_name("TPL_password").send_keys("248552ZZN")
                            driver.save_screenshot('RecordProcess/loginPic4.png')
                            #
                            loginBtn = driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]')
                            driver.save_screenshot('RecordProcess/loginPic5.png')
                            # loginBtn.send_keys(Keys.RETURN)
                            loginBtn.click()
                            print  ('login_success****')
                        try:
                            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-detail-hd')))  # 显性等待
                        except Exception as e:
                            print '显性未加载成功---%s'%e
                            driver.close()  # 关闭当前窗口
                            break

                        time.sleep(5)  # 这里得让他睡眠一下，否则第二页开始会报错(加载数据)
                        driver.implicitly_wait(30)  # 隐性等待30秒，如果30之内页面加载完毕，往下执行，否则超时会报错，需要处理
                        try:
                            detailDoc = pq(driver.page_source)
                            driver.save_screenshot('RecordProcess/secPage.png')
                            # TODO:XDF 这里需要注意一下，src图片链接可能不存在https，需要自己手动拼接
                            mainPics = detailDoc.find('#J_ImgBooth').attr('src')
                            if 'https:' in mainPics:
                                mainPic = mainPics
                            else:
                                mainPic = 'https:' + mainPics
                            # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）
                            if 'xmlns' in detailDoc.find('.tb-detail-hd').html():
                                print ('存在xmlns--%s' % detailDoc.find('.tb-detail-hd').html())
                                titles = detailDoc.find('.tb-detail-hd').html()
                                selector = etree.HTML(titles)
                                title = str(selector.xpath('//h1/text()')[0]).replace('\r\n', '').replace(' ','').replace('\n', '').replace('\t', '')
                                print (title)
                            else:
                                title = detailDoc.find('#detail .tb-detail-hd h1').text().replace('\r\n', '').replace(' ','').replace('\n', '').replace('\t', '')

                            presellPrice = detailDoc.find('#J_PromoBox').text().replace('\r\n', '').replace(' ', '').replace('\n', '').replace('¥', '')
                            address = detailDoc.find('#J_deliveryAdd').text()
                            # 收藏人数
                            popularity = detailDoc.find('#J_CollectCount').text().replace('（', '').replace('人气）', '')
                            shopName = str(allShopName['shopName'][i])
                            paymentDate = detailDoc.find('.J_step2Time').text().split('~')
                            try:
                                paymentBeginDate = paymentDate[0]
                                paymentFinishDate = paymentDate[1]
                            except Exception as e:
                                print ('error---%s' % e)

                            reserveCount = detailDoc.find('.tb-wrt-guc').text().replace('\r\n', '').replace(' ', '').replace('\n', '').replace('件', '')
                            detailPrice = detailDoc.find('#J_StrPriceModBox .tm-price').text().replace('\r\n', '').replace(' ', '').replace('\n', '')
                            categoryIdContent = str(detailDoc.find('#J_ZebraPriceDesc').attr('mdv-cfg')).replace(' ','').replace('{', '').replace('}', '')
                            categoryIds = '.*catId:([0-9]+)'
                            categoryId = re.compile(categoryIds).findall(categoryIdContent)[0]
                            for h in range(0, len(allCategory)):
                                if str(allCategory['CategoryId'][h]) == categoryId:
                                    categoryName = str(allCategory['CategoryName'][h])
                                    break
                                else:
                                    categoryName = '-'

                            styleData = detailDoc.find('#J_AttrUL').children().items()

                            for data in styleData:
                                if '风格: ' in data.text():
                                    style = data.text().split(': ')[1]
                                    print ('风格---------------%s---%s' %(style,categoryId))
                                    break
                                else:
                                    style = '-'
                            print shopName,categoryName,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),detailPrice,address,detailURL,title,mainPic,presellPrice,popularity #,paymentBeginDate,paymentFinishDate,reserveCount


                            if len(reserveCount)>0:
                                print ('----------进来了吗？')
                                product = {
                                    'title': title,
                                    'ID': Id,
                                    'addRess': address,
                                    'shopName': shopName,
                                    'mainPic': mainPic,
                                    'detailURL': detailURL,
                                    'detailPrice': detailPrice,
                                    'popularity': popularity,
                                    'reserveCount': reserveCount,
                                    'paymentBeginDate': paymentBeginDate,
                                    'paymentFinishDate': paymentFinishDate,
                                    'presellPrice': presellPrice,
                                    'style': style,
                                    'categoryId': categoryId,
                                    'categoryName': categoryName,
                                    'spiderTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                saveTmallTB(product)
                        except Exception as e:
                            print ('miss---%s'%e)
                        finally:
                            print ('*******即将退出*******')
                            time.sleep(3)
                            driver.close()  # 关闭当前窗口
                            print ('*******已关闭*******')

                #输出主窗口句柄
                print (now_handle)
                driver.switch_to.window(now_handle) #返回主窗口

            try:
                if driver.find_element_by_class_name('next-disabled'):
                    break
            except Exception as e:
                print ('miss----%s'%e)
                driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/ul/li[@class="item next"]/a').click() #send_keys(Keys.RETURN)
                print '即将到达下一页'
            finally:
                print ('退出吧')

        print ('---------------名字----1')

    time.sleep(5)
    driver.close()
    driver.quit()

def saveTmallTB(result):
    try:
        if table.insert(result):
            print ('saveSuccess')
    except Exception as e:
        print ('save_Error...')

#TODO:EXP 给定ID和店铺情况
def tmallGivenIDAndShopName():
    # TODO:XDF Chrome欲歌浏览器
    # options = webdriver.ChromeOptions()
    # # 设置中文
    # options.add_argument('lang=zh_CN.UTF-8')
    # # 更换头部
    # options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"')
    #
    #
    # driver = webdriver.Chrome(chrome_options=options,executable_path=r'/Users/zhuoqin/Desktop/Python/SeleniumDemo/chromedriver')


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

    driver = webdriver.PhantomJS(executable_path=r'/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)  # TODO:XDF 针对Linux
    # TODO:XDF 针对Linux服务器
    wait = WebDriverWait(driver, 60, 0.5)  # 表示给browser浏览器一个10秒的加载时间

    driver.implicitly_wait(20)
    driver.set_page_load_timeout(20)
    print ('等待中。。。')
    for k in range(0,len(df)):

        driver.get('https://detail.tmall.com/item.htm?id=%s' % str(df['ID'][k]))
        print ('https://detail.tmall.com/item.htm?id=%s' % str(df['ID'][k]))
        if 'login.tmall' in str(driver.current_url):
            print ('需要登录----')
            # # TODO:XDF: 这是设置窗口大小（仅仅针对phantomjs无头浏览器，其它会报错）
            # driver.set_window_size(1800, 1000)
            driver.switch_to.frame("J_loginIframe")
            time.sleep(5)
            # TODO:XDF:1 因为无头浏览器是无界面的，所以只能通过截图来查看过程，下面同理（仅仅针对phantomjs无头浏览器，其它会报错）
            driver.save_screenshot('RecordProcess/process1.png')

            driver.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()

            time.sleep(2)
            # TODO:XDF:2
            driver.save_screenshot('RecordProcess/process2.png')
            driver.find_element_by_name("TPL_username").send_keys("13672456277")
            driver.find_element_by_name("TPL_password").send_keys("248552ZZN")
            #
            # TODO:XDF:3
            driver.save_screenshot('RecordProcess/process3.png')
            loginBtn = driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]')
            # TODO:XDF:4
            driver.save_screenshot('RecordProcess/process4.png')
            # loginBtn.send_keys(Keys.RETURN)
            loginBtn.click()
            print ('login success')
            driver.save_screenshot('RecordProcess/process5.png')


        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tb-detail-hd'))) #显性等待

        time.sleep(5) #这里得让他睡眠一下，否则第二页开始会报错(加载数据)
        # driver.implicitly_wait(30) #隐性等待30秒，如果30之内页面加载完毕，往下执行，否则超时会报错，需要处理
        html =driver.page_source  #这是一面的页面内容
        # print '源码内容----%s'%html
        print ('等待中。。。%s'%k)
        if 'tmall' in driver.current_url:
            detailURL = 'https://detail.tmall.com/item.htm?id='+str(df['ID'][k])
        else:
            detailURL = 'https://item.taobao.com/item.htm?id='+str(df['ID'][k])
        try:
            doc = pq(html)

            # TODO:XDF 这里需要注意一下，src图片链接可以不丰在https，需要自己手动拼接
            mainPics = doc.find('#J_ImgBooth').attr('src')
            if 'https:' in mainPics:
                mainPic = mainPics
            else:
                mainPic = 'https:'+mainPics


            # TODO:XDF 这里要注意，源码中可能存在xmlns，用pq是爬取不到的，要用lxml的tree抓取（非常坑爹）
            if 'xmlns' in doc.find('.tb-detail-hd').html():
                print ('存在xmlns--%s'%doc.find('.tb-detail-hd').html())
                titles = doc.find('.tb-detail-hd').html()
                selector = etree.HTML(titles)
                title = str(selector.xpath('//h1/text()')[0]).replace('\r\n','').replace(' ','').replace('\n','').replace('\t','')
                print (title)
            else:
                title = doc.find('#detail .tb-detail-hd h1').text().replace('\r\n', '').replace(' ', '').replace('\n', '').replace('\t','')

            ID = str(df['ID'][k])
            presellPrice = doc.find('#J_PromoBox').text().replace('\r\n', '').replace(' ','').replace('\n', '').replace('¥', '')
            address = doc.find('#J_deliveryAdd').text()
            #收藏人数

            popularity = doc.find('#J_CollectCount').text().replace('（', '').replace('人气）','')
            shopName = str(df['shop'][k])
            paymentDate = doc.find('.J_step2Time').text().split('~')
            driver.save_screenshot('RecordProcess/ceShiprocess%s.png' % k)
            try:
                paymentBeginDate = paymentDate[0]
                paymentFinishDate = paymentDate[1]
            except Exception as e:
                print ('miss2---%s'%e)

            reserveCount = doc.find('.tb-wrt-guc').text().replace('\r\n', '').replace(' ', '').replace('\n','').replace('件','')
            detailPrice = doc.find('#J_StrPriceModBox .tm-price').text().replace('\r\n', '').replace(' ', '').replace('\n', '')
            categoryIdContent = str(doc.find('#J_ZebraPriceDesc').attr('mdv-cfg')).replace(' ', '').replace('{','').replace('}', '')
            print (categoryIdContent)
            categoryIds = '.*catId:([0-9]+)'
            categoryId = re.compile(categoryIds).findall(categoryIdContent)[0]

            for k in range(0, len(allCategory)):
                if str(allCategory['CategoryId'][k]) == categoryId:
                    categoryName = str(allCategory['CategoryName'][k])
                    break
                else:
                    categoryName = '-'

            # print '类型---%s'%categoryId
            styleData = doc.find('#J_AttrUL').children().items()


            for data in styleData:
                # print '数据-----%s'%data.text()
                if '风格: ' in data.text():
                    style = data.text().split(': ')[1]
                    print ('风格---------------%s' % style)
                    break
                else:
                    style = '-'
            print ID, shopName,categoryName, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), detailPrice, address, detailURL, title, mainPic, presellPrice, popularity #, paymentBeginDate, paymentFinishDate, reserveCount

            product = {
                'title': title,
                'ID': ID,
                'addRess': address,
                'shopName': shopName,
                'mainPic': mainPic,
                'detailURL': detailURL,
                'detailPrice': detailPrice,
                'popularity': popularity,
                'reserveCount': reserveCount,
                'paymentBeginDate': paymentBeginDate,
                'paymentFinishDate': paymentFinishDate,
                'presellPrice': presellPrice,
                'style': style,
                'categoryId': categoryId,
                'categoryName': categoryName,
                'spiderTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            if len(reserveCount) > 0:
                saveTmallTB3(product)
        except Exception as e:
            print ('error---%s'%e)

    print ('---------------名字----1')




    time.sleep(6)
    driver.close()
    driver.quit()

def saveTmallTB3(result):
    try:
        if tableShop.insert(result):
            print ('saveSuccess')
    except Exception as e:
        print ('save_Error...')

if __name__ == '__main__':
    tmallDataSEL()
    # tmallGivenIDAndShopName()
