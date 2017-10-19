# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
import pymssql
import json
import urllib2
import uuid
import time,datetime
from decimal import *
import chardet
import sys
reload(sys)
sys.setdefaultencoding('utf8')
allData = []
BaseInfo = []

class Mssql:
    def __init__(self):
        self.host = '192.168.1.253:1433'
        self.user = 'bs-prt'
        self.pwd = '123123'
        self.db = 'Collectiondb'

    def __get_connect(self):
        if not self.db:
            raise (NameError, "do not have db information")
        self.conn = pymssql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            database=self.db,
            # charset="utf8"
            charset = "utf8"
        )
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "Have some Error")
        else:
            return cur

    def exec_query(self, sql):
        """
         the query will return the list, example;
                ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        """
        cur = self.__get_connect()
        cur.execute(sql)
        res_list = cur.fetchall()

        # the db object must be closed
        self.conn.close()
        return res_list

    def exec_non_query(self, sql):
        """
        execute the query without return list, example：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        cur = self.__get_connect()

        cur.execute(sql)

        self.conn.commit()
        self.conn.close()

    def exec_many_query(self, sql, param):
        """
        execute the query without return list, example：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        cur = self.__get_connect()
        try:
            cur.executemany(sql, param)

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()

        self.conn.close()

    # def exec_one_by_one_query(self, sql, param):
    #     """
    #     execute the query without return list, example：
    #         cur = self.__GetConnect()
    #         cur.execute(sql)
    #         self.conn.commit()
    #         self.conn.close()
    #     """
    #     cur = self.__get_connect()
    #     insert_date = dt.today().strftime('%Y-%m-%d %H:%M:%S')
    #
    #     for i in param:
    #         sql_text = "insert into T_Treasure_EvalCustomItem_Detail values ('%s','%s','%s','%s','%s','%d','%d','%d','%s','%s','%s','%s','%s','%d','%s','%s','%s','%d','%s','%s','%d','%s','%d','%s','%s','%s','%s','%s')" %\
    #                    (i[0],i[3],' ',' ',' ',1,1,1,' ',uuid.uuid1(),' ',' ',' ',1,' ',' ',' ',1.0,' ',' ',1.0,' ',1,i[1],insert_date,' ',' ',' ')
    #         try:
    #             cur.execute(sql_text)
    #             self.conn.commit()
    #         except Exception as e:
    #             print e
    #             self.conn.rollback()
    #
    #     self.conn.close()

#TODO:XDF 预售宝贝表
def InsertPreSaleNew(product):
    conn = Mssql()
    print product
    modifyTime = strToDateTime(product['modifyTime'], 'sixLineTypes')
    # TODO:XDF 这里要注意，不要把 , 号写成中文符号(这里坑了我好久)，否则会报错：‘pymssql.ProgrammingError: (102, "Incorrect syntax near '\xef\xbc\x8c'.DB-Lib error message 20018, severity 15:\nGeneral SQL Server error: Check messages from the SQL Server\n")’
    # sql_text = "insert into T_Treasures_PreSaleNew values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d','%d')" % \
    #                    (uuid.uuid1(), str(uuid.uuid1()), product['ID'], product['detailURL'], strToDateTime(product['StartTime'],'fiveColonTypes'), strToDateTime(product['EndTime'],'fiveColonTypes'),
    #                     strToDateTime(product['paymentBeginDate'], 'fiveColonTypes'),strToDateTime(product['paymentFinishDate'], 'fiveColonTypes'),product['title'],product['mainPic'],'0',product['shopName'],
    #                     product['categoryName'],product['style'],0,modifyTime,0,'0','0',0,'0.00','0.00','0','0',0,0,0)


    sql_text = "insert into T_Treasures_PreSale values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uuid.uuid1(),  product['TreasureID'], product['StartTime'], product['EndTime'],
                        strToDateTime(product['paymentBeginDate'], 'fiveColonTypes'),strToDateTime(product['paymentFinishDate'], 'fiveColonTypes'),'','','',product['URL_NO'],product['mainPic'],'0',modifyTime,0,0)

    conn.exec_non_query(sql_text)
    print '*******预售宝贝表插入成功********'

#TODO:XDF 宝贝基本信息表
def InsertOrUpdateBaseInfo(product,states):
    conn = Mssql()

    print '进入更新或者插入---%s'
    rateData = getCommentBestNewTime(product)
    if rateData:
        # commentNewTime = getCommentBestNewTime(product)
        EvaluationNewTime = strToDateTime(str(rateData), 'sixLineTypes')
    else:
        EvaluationNewTime = ''
    currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    modifyTime = strToDateTime(currentTime,'sixLineTypes')

    print '------------进入更新或者插入---------------'
    print type(product['title']),type(product['detailURL']),type(product['ShopID']),type(product['shopName']),type(product['JHSmodifyTime']),type(product['categoryName']),type(product['spuId']),type(product['EvaluationScores']),\
            type(product['brandId']),type(product['brand']),type(EvaluationNewTime),type(product['TreasureID']),type(product['StyleName']),type(product['ShopURL']),type(product['ItemName']),type(product['NCategory_Name']),\
            type(product['NStyleName']),type(product['NewstPrice']),type(product['mainPic']),type(product['URL_NO']),type(product['categoryId']),type(product['ItemName'])

    TreasureID = product['TreasureID']
    ShopID = str(product['ShopID'])
    TreasureName = str(product['title'])
    ShopName = str(product['shopName'])
    spuId = str(product['spuId'])
    brandId = str(product['brandId'])
    brand = str(product['brand'])
    StyleName = str(product['StyleName'])


    if states == 'Insert':
        print '即将开始------插入'
        sql_text = "insert into T_Treasures_BaseInfo (BatchNo,TreasureID,TreasureName,TreasureLink,ShopID,ShopName,Shop_Platform,Treasure_Status,Monthly_Volume,Is_Search,InsertDate,ModifyDate,IsMerge," \
                   "Category_Name,IsDel,GrpName,spuId,EvaluationScores,Successful_Trading,ShopURL,TreasureHref,TreasureFileURL,IsAuto,Url_No,CategoryId,brandId,brand,rootCatId,StyleName,EffectiveTime," \
                   "ReservationStatus,ReNewPreSaleTime,JHSReNewTime,CollectionNum,JHSModifyTime,ItemName,EvaluationTime,SkuModifyDate,TempleteTime,NCategory_Name,NStyleName,NewestPrice)" \
                   " values ('%s', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s'," \
                   "'%s','%s','%s','%d', '%s', '%s', '%s', '%s','%s','%s','%s','%s')"%(' ',TreasureID,TreasureName,str(product['detailURL']),ShopID,ShopName,
                    1,1,0,'1',modifyTime,modifyTime,'0',product['categoryName'],'0',' ',spuId,product['EvaluationScores'],0,product['ShopURL'],product['mainPic'],product['mainPic'],'1',product['URL_NO'],
                    product['categoryId'],product['brandId'],product['brand'],product['rootCatId'],StyleName,modifyTime,product['ReservationStatus'],modifyTime,
                    modifyTime,product['CollectionNum'],modifyTime,product['ItemName'],EvaluationNewTime,modifyTime,modifyTime,product['NCategory_Name'],product['NStyleName'],product['presellPrice']
                    )

    else:
        print '即将开始-------更新'
        sql_text = "UPDATE T_Treasures_BaseInfo SET TreasureName='%s',TreasureLink='%s',ShopID='%s',ShopName='%s',ModifyDate='%s',Category_Name='%s',spuId='%s',EvaluationScores='%f',brandId='%s',brand='%s'," \
                   "EvaluationTime='%s' NewsPrice='%s' WHERE TreasureID='%s'"%(
                                                    TreasureName,str(product['detailURL']),ShopID,ShopName,modifyTime,product['categoryName'],spuId,product['EvaluationScores'],brandId,brand,
                                                    EvaluationNewTime,product['presellPrice'],TreasureID
                                       )
    print 'sql---%s'%sql_text
    conn.exec_non_query(sql_text)

#获取最新评论时间
def getCommentBestNewTime(product):
    commentURL = 'https://rate.tmall.com/list_detail_rate.htm?itemId='+str(product['TreasureID'])+'&spuId='+str(product['spuId'])+'&sellerId='+str(product['sellerId'])+'&order=1&currentPage=1&append=0&content=1&posi=&picture=&needFold=0'
    # commentURL = 'https://rate.tmall.com/list_detail_rate.htm?itemId=17731025119&spuId=216642496&sellerId=911093189&order=1&currentPage=1&append=0&content=1&posi=&picture=&needFold=0'
    commentResult = getCommentResults(commentURL)
    # print commentResult
    CommentData = commentResult["rateDetail"]["rateList"]

    if CommentData:
        rateData = CommentData[0]['rateDate']
        print '数据源是----------%s' % CommentData
    else:
        rateData = ''

    print '数据源是1----------%s' % CommentData
    return rateData

#TODO:XDF 数据源抽取
def getCommentResults(commentURL):
    i = 0
    while True:
        req = urllib2.Request(commentURL)  # req表示向服务器发送请求#
        response = urllib2.urlopen(req)  # response表示通过调用urlopen并传入req返回响应 response#
        result = response.read()  # 用read解析获得的HTML文件#

        """
            这里要特别注意了，如果单纯用try内这种解码方式可能会报错：UnicodeDecodeError: 'gbk' codec can't decode bytes in position 6681-6682: illegal multibyte sequence ，很明显是编码问题
            在 commentData = '{' + result + '}'.decode(encoding='utf-8') 如果将.decode(encoding='utf-8') 删除，也可以显示数据，但是数据源中会出现乱码
            经过本人不断尝试，用except中的编码方式（其实只用except中的方法就可以了，但担心后面会出现问题，所以先保留）就可以解决编码问题了
            如果想看实际效果，可以请求以下URL获取数据源
            https://rate.tmall.com/list_detail_rate.htm?itemId=527123591448&spuId=509103357&sellerId=143584903&order=1&currentPage=37&append=0&content=1&tagId=&posi=&picture=&needFold=0
        """
        commentData = '{' + result + '}'
        commentData = settingNameCode(commentData)

        if 'https://sec.taobao.com/' in commentData:
            print 'enter----login'
            time.sleep(3)
            if i == 20:
                commentResult = {}
                break
            i += 1
        else:
            commentResult = json.loads(commentData)
            break
    return commentResult


"""
    在爬虫中，也许会出现多种编码格式，就像KOI8-R（这也是我第一次见），如果不设置一下，会报如下错误
    编码格式---{'confidence': 0.7313997367253507, 'language': 'Russian', 'encoding': 'KOI8-R'}
                {'confidence': 0.25598990785387277, 'language': 'Russian', 'encoding': 'IBM855'}
                {'confidence': 0.73, 'language': '', 'encoding': 'ISO-8859-1'}
                {'confidence': 0.3391494065054961, 'language': 'Greek', 'encoding': 'ISO-8859-7'}
            save_Error...strings in documents must be valid UTF-8: '\xcc\xa9\xc9\xbd\xcf\xb5\xc1\xd0'
            {'confidence': 0.0, 'language': None, 'encoding': None}
            {'confidence': 0.73, 'language': '', 'encoding': 'Windows-1252'}
            {'confidence': 0.4626272726179244, 'language': 'Thai', 'encoding': 'TIS-620'}
            save_Error...strings in documents must be valid UTF-8: 'CQ\xca\xe9\xd7\xc0'

"""
def settingNameCode(itemName):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    mychar = chardet.detect(itemName)
    nameCode = mychar['encoding']
    nameLanguage = mychar['language']
    if nameCode == 'KOI8-R' or nameLanguage == 'Russian' or nameCode == 'ISO-8859-1' or nameCode == 'ISO-8859-7' or nameLanguage == 'Thai' or nameCode == None:
        Name = itemName.decode('gb18030').encode('utf-8')
    elif nameCode == 'utf-8' or nameCode == 'UTF-8':
        Name = itemName.decode('utf-8', 'ignore').encode('utf-8')
    elif nameCode == 'GB2312' or nameCode == 'gb2312':
        Name = itemName.decode('gb2312', 'ignore').encode('utf-8')
    elif nameCode == 'Windows-1252':
        Name = itemName.decode('Windows-1252').encode('utf-8')
    else:
        Name = itemName
    return Name


def judgeHaveTreasureID(product):
    try:
        for data in BaseInfo:
            if product['TreasureID'] == str(data):
                print 'TreasureID 存在---%s---%s'%(product['TreasureID'],str(data[3]))
                return True
        return False

    except Exception as e:
        print 'error----%s' % e


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
    elif types == 'sixLineTypes':
        return datetime.datetime.strptime(strs, '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(strs, '%Y年%m月%d日 %H时%M分%S秒')


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class BsproductcenterMssql:
    def __init__(self):
        self.host = '192.168.1.253:1433'
        self.user = 'bs-prt'
        self.pwd = '123123'
        self.db = 'BSPRODUCTCENTER'

    def __get_connect(self):
        if not self.db:
            raise (NameError, "do not have db information")
        self.conn = pymssql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            database=self.db,
            # charset="utf8"
            charset = "utf8"
        )
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "Have some Error")
        else:
            return cur

    def exec_query(self, sql):
        """
         the query will return the list, example;
                ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        """
        cur = self.__get_connect()
        cur.execute(sql)
        res_list = cur.fetchall()

        # the db object must be closed
        self.conn.close()
        return res_list

    def exec_non_query(self, sql):
        """
        execute the query without return list, example：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        cur = self.__get_connect()

        cur.execute(sql)

        self.conn.commit()
        self.conn.close()

    def exec_many_query(self, sql, param):
        """
        execute the query without return list, example：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        cur = self.__get_connect()
        try:
            cur.executemany(sql, param)

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()

        self.conn.close()

def selectAllProductID():
    conn = BsproductcenterMssql()
    sql_text = 'select distinct TreasureID from T_PRT_TreasureSetView where LastUpdateTime is null'
    return conn.exec_query(sql_text)


#插入ShopTemplete表，【店铺表】
def SelectShopTempletes():
    conn = Mssql()
    sql_text = 'SELECT * FROM ShopTemplete'
    results = conn.exec_query(sql_text)

    for data in results:
        allData.append(list(data)[0])
    return allData

#判断店铺是否被爬取过
def ExistenceShopName(shopName):
    for data in allData:
        if data == shopName:
            print '存在'
            return True
    return False

def SelectT_Treasures_BaseInfo():
    conn = Mssql()
    sql_text = 'SELECT * FROM T_Treasures_BaseInfo'
    results = conn.exec_query(sql_text)

    for data in results:
        BaseInfo.append(list(data)[3])
    return BaseInfo



#插入ShopTemplete表，【店铺表】
def InsertShopTempletes(shopName,URL_NO):
    conn = Mssql()
    shopName_InsertText = "insert into ShopTemplete values ('%s','%s','%d','%d','%s','%d')" % (shopName, URL_NO, 0, 0, ' ', 0)
    conn.exec_non_query(shopName_InsertText)
    print '插入成功'


if __name__ == '__main__':
    # tims = time.localtime()

    # print selectAllProductID()
    # result = selectAllProductID()
    # for data in result:
    #     print data[0]

    # print selectShopTemplete()

    # shopList = selectShopTemplete()
    # shopList.append(selectShopTemplete())
    # shopList = []
    # for data in selectShopTemplete():
    #     shopList.append(data[0])
    #     if '林氏木业家具' in data[0]:
    #         print '存在里面'
    #         break
    # print shopList

    # InsertShopTempletes()
    # shopName = '林氏木业家具旗舰店'
    # if ExistenceShopName(shopName)==True:
    #     print shopName+'********存在****'

    # shopList = InsertShopTempletes()
    # print '店铺名列表---%s'%shopList

    # print type(strToDateTime('2050-08-08', 'threLineTypes'))
    #
    # # print strToDateTime(time.localtime().strftime('%Y-%m-%d %H:%M:%S'),'sixLineTypes')
    # print strToDateTime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'sixLineTypes')
    #
    #
    # print unicode('\xef\xbc\x8c', "utf8")
    #
    # # ceShiDemo()
    #
    strs = '2017.09.09 01:00'
    print datetime.datetime.strptime(strs, '%Y.%m.%d %H:%M')
    s = '2017--26 00:00:00'
    if now() > s:
        print '过期'
    else:
        print '没过期'










