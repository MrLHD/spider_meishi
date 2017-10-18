import re
from config import *
import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

client = pymongo.MongoClient(MONGO_URL,MONGO_Port)
db = client[MONGO_DB]

# browser = webdriver.Chrome()
#用Phantom让它在后台运行
browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser, 10)
#设置窗口大小
browser.set_window_size(1400,900)

def search():
    """
    打开浏览器输入关键字，然后执行查找操作。
    :return:
    """
    print('正在搜索')
    try:
        browser.get("https://www.taobao.com")
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button")))
        input.send_keys(KEYWORD)
        submit.click()
        #查找一共需要爬去多少页
        total = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        #注意返回的是一个对象，但是对象是包含子列表里面的所以需要简单处理一下
        return  total[0].text
    except TimeoutException:
        return search()

def next_page(page_number):
    """
    1、翻页（找到输入页码的输入框输入页码，然后执行确认操作。）
    :param page_number:
    :return:
    """
    print('正在翻页')
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        #输入前清理输入框
        input.clear()
        input.send_keys(page_number)
        submit.click()
        #等待当前页加载出来操作
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
        #执行爬操作
        get_products()
    except TimeoutException:
        next_page(page_number)

def get_products():
    """
    爬去加载出来的页面信息
    :return:
    """
    #等待详细信息加载完
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    #拿到selenium拿到的html页面
    html = browser.page_source
    #使用pyquery分析html信息
    doc = pq(html)
    #抓取每个商品详细信息
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        #商品详细页链接，价格，已付款人数，商品标题，店名，
        product = {
            # 'image':item.find('.pic .img').attr('src'),
            'link': item.find('.pic .pic-link').attr('href'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('储存到MONGODB成功',result)
    except Exception:
        print("储存到MONGODB失败",result)



def main():
    try:
        #拿到总共需要爬去多少页
        total = search()
        #拿到的标签里还有汉字，用re筛选出数字并转换成int类型
        total = int(re.compile('(\d+)').search(total).group(1))
        #打开就是第一页，所以从第二页开始，总共需要爬去100页，range如果输入到100，只爬到99页所以要加1.
        for i in range(2,total + 1):
            next_page(i)
        #爬完成后关闭浏览器
    except Exception:
        print('出错了！！！！！！！')
    finally:
        browser.close()


if __name__ == '__main__':
    main()
