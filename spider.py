#-*- codeing = utf-8 -*-
#@Time: 2020/10/15 23:41
#@Auther: Jack hou
#@File: spider.py
#@Software: PyCharm

from bs4 import BeautifulSoup           #网页解析,获取数据,分解网页的结构，并对其中的内容进行提取。
import re            #正则表达式,进行文字匹配
import urllib.request,urllib.error      #制定URL,获取网页数据
import xlwt          #进行Excel操作
import _sqlite3     #进行sqlite数据库操作
import mysql.connector



def main():
    baseurl="https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist=getData(baseurl)
    #savepath="豆瓣电影Top250.xls"
    dbpath="movie.db"
    #3.保存数据
    #saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)

    #askURL("https://movie.douban.com/top250?start=")

    # 影片详情
findLink = re.compile(r'<a href="(.*?)">')  # 创建正则表达式对象,表示规则(字符串模式)\
    # 影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S让换行符包含在字符中
    # 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
    # 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
    # 找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
    # 找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
    # 找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)

#爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):    #调用获取页面信息的函数*10
        url=baseurl+str(i*25)
        html=askURL(url)      #保存获取的网页源码


        #2.逐一解析数据
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"): #找到class_="item"的div  #查找符合要求的字符串,形成列表

            #print(item)    #测试:查看电影item所有信息                                 #class要加下划线是类别否则报错
            data = []
            item =str(item)
            # print(item)
            # break
            #影片详情的链接
            link=re.findall(findLink,item)[0]           #re库用来通过正则表达式查找指定字符串
            data.append(link)

            imgSrc=re.findall(findImgSrc,item)[0]       #添加图片
            data.append(imgSrc)

            titles= re.findall(findTitle, item)      #片名可能只有一个中文名,没有外国名
            if(len(titles)==2):
                chinesetitle=titles[0]                  #添加中文名
                data.append(chinesetitle)
                foreigntitle=titles[1].replace("/","")  #去掉无关的符好,用replace将"/"换成""空的
                foreigntitle = re.sub('\xa0',"",foreigntitle)
                data.append(foreigntitle)               #添加外国名
            else:
                data.append(titles[0])
                data.append(' ')         #留空

            rating=re.findall(findRating,item)[0]        #添加评分
            data.append(rating)

            judgeNumbes = re.findall(findJudge, item)[0]  #添加评价人数
            data.append(judgeNumbes)

            inq=re.findall(findInq,item)              #添加概述
            if len(inq) != 0:
                inq=inq[0].replace("。","")           #去掉句号
                data.append(inq)
            else:
                data.append(" ")                     #留空

            bd=re.findall(findBd,item)[0]
            bd=re.sub('<br(s\+)?/>(\s+)?'," ",bd)    #去掉<br/>
            bd=re.sub('/'," ",bd)                  #替换/
            bd=re.sub('\xa0',"",bd)                 #替换\xa0
            data.append(bd.strip())                #去掉前后空格

            datalist.append(data)              #把处理好的一部电影信息放入datalist

            # print(link)
    #print(datalist)
    return datalist

#到到指定一个URL的网页内容
def askURL(url):

    head={            #模拟浏览器头部信息,向豆瓣服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 86.0.4240.75Safari / 537.36"
    }                 #用户代理表示告诉豆瓣服务器,我们是什么类型的机器*浏览器(本质上是告诉浏览器,我们可以接受什么水平的文件
    request =urllib.request.Request(url,headers=head)
    html=""
    try:
        request=urllib.request.urlopen(request)
        html=request.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)

    return html



#保存数据
def saveData(datalist,savepath):

    book=xlwt.Workbook(encoding="utf-8",style_compression=0)    #style_compression=0 样式压缩样式
    sheet=book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)   #cell_overwrite_ok是否覆盖原内容
    col=("电影详情链接","图片链接","影片中文名","影片外国名","评分","评分人数","概况","相关信息")
    for i in range(0,8):
        sheet.write(0,i,col[i])   #列名
    for i in range(0,250):
        print("第%d条" %(i+1))
        data=datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])     #数据

    book.save(savepath)    #保存

def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = mysql.connector.connect(
        # host="127.0.0.1", # 数据库主机地址 localhost报错
        host="localhost",  # 数据库主机地址
        user="root",  # 数据库用户名
        passwd="7758521", # 数据库密码y
        database="movie"
    )
    cur=conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            data[index]='"'+data[index]+'"'
        sql='''
            insert into movie250 (
            info_link,pic_link,cname,ename,score,rated,introduction,info)
            values(%s)'''%",".join(data)
        #print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):
    conn = mysql.connector.connect(
        # host="127.0.0.1", # 数据库主机地址 localhost报错
        host="localhost",  # 数据库主机地址
        user="root",  # 数据库用户名
        passwd="7758521", # 数据库密码
        database="movie"
    )
    mycursor = conn.cursor(dbpath)

    # 创建数据库#create database movie

    sql='''
        create table movie250
        (
        id integer primary key auto_increment,
        info_link text,
        pic_link text,
        cname varchar(30),
        `ename` varchar(100),            #在MySQL中，为了区分MySQL的关键字与普通字符，MySQL引入了一个反引号,列名称使用的是单引号而不是反引号，所以会就报了这个错误出来
        `score` numeric(30,1),
        `rated` numeric(30),
        introduction text,
        info text
        )
    '''
    mycursor.execute(sql)  # 创建名为test的数据库
    conn.commit()  # 提交数据库操作
    conn.close()  # 关闭数据库连接

    print("成功创建数据库movie!")




if __name__=="__main__":
    print("爬取开始!!!")
    main()
    init_db("movietest.db")
    print("爬取完成!!!")