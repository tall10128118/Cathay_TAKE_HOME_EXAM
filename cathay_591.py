from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv
import requests
import pandas as pd 
from pymongo import MongoClient

#---------------------------------------------------------------------------
def data_to_dataframe():  
    
    select_df = pd.read_csv(output_file_name)
    dataframe_to_mongo(select_df)

def dataframe_to_mongo(select_df):

    client = MongoClient()
    database = client["db_591_rent"] 
    collection = database["collection"]   

    records = select_df.to_dict('records') 
    collection.insert_many(records)

#---------------------------------------------------------------------------

def getData(url):
    
    request_url='https:'+str(url).strip()
    res=requests.get(request_url)
    print(request_url)

    # 若伺服器傳回狀態碼為 200 代表 ok
    if res.status_code == 200:
        bs=BeautifulSoup(res.text,'html.parser')
        # initialization 若沒有取得資料則以NULL顯示
        addr='NULL' # 地址
        renter = 'NULL' # 房東/房仲/代理人
        renter_id = 'NULL' # 房東身分 目前爬取不到
        phone = 'NULL' # 電話
        price='NULL' # 價格
        size='NULL' # 坪數
        floor='NULL' # 樓層
        room_type='NULL' # 型態
        condition = 'NULL'# 現況
        form='NULL' # 格局
        car='NULL' # 車位
        gender='NULL' # 性別入住    
        
        soup = BeautifulSoup(res.text,'lxml')
        # 取得 房東、電話資訊
        # 因為和 CLASS 包在一起，先將整段擷取下來
        phone_results = soup.find_all("span", class_="dialPhoneNum")
        renter_results = soup.find_all("span", class_="kfCallName")
        # 再將 CLASS讀出來的 BS4 RESULTS_SET 讀取 所要的資訊
        phone =  phone_results[0]['data-value']
        renter = renter_results[0]['data-name']
        # 利用 BeautifulSoup 的 find 搭配 css selector 並取得指定資料
        addr=bs.find('span',{'class':'addr'}).text        
        price=bs.find('div',{'class':'price'}).text.strip().split(' ')[0]   

        # 在原始碼一開頭以 ul 包著，先將 ul 中 CLASS : attr 的 li 先用find 定位
        # 再以 split 分開，並藉由我們要的資料去取得data

        room_attrs=bs.find('ul',{'class':'attr'}).findAll('li')
        for attr in room_attrs:
            if attr.text.split('\xa0:\xa0\xa0')[0]=='坪數':
                size=attr.text.split('\xa0:\xa0\xa0')[1]
            elif attr.text.split('\xa0:\xa0\xa0')[0]=='樓層':
                floor=attr.text.split('\xa0:\xa0\xa0')[1]
            elif attr.text.split('\xa0:\xa0\xa0')[0]=='型態':
                room_type=attr.text.split('\xa0:\xa0\xa0')[1]
            elif attr.text.split('\xa0:\xa0\xa0')[0]=='現況':
                condition=attr.text.split('\xa0:\xa0\xa0')[1]   

        # 在原始碼一開頭以 ul 包著，先將 ul 中 CLASS : labelList-1 的 li 先用find 定位
        # 再以 split 分開，並藉由我們要的資料去取得data         
        room_descriptions=bs.find('ul',{'class':'labelList-1'}).findAll('li')
        for description in room_descriptions:
            
            if description.text.split('：')[0]=='格局':
                form=description.text.split('：')[1]
            if description.text.split('：')[0]=='車 位':
                car=description.text.split('：')[1]
            if description.text.split('：')[0]=='性別要求':
                gender=description.text.split('：')[1] # 因為爬蟲時會爬到下一欄，問題尚未解決，用字串比較處理。
             
        # 將取得資訊回傳              
        return addr,renter,phone,price,size,floor,room_type,condition,form,gender,car,request_url
    
    # 若伺服器傳回狀態碼非 200 ，皆顯示
    else:
        print('The link you broswered is expired:', url)
        return 404, 404, 404, 404, 404, 404, 404
    
def main(outputfile):
    #開啟chrome
    browser = webdriver.Chrome()
    browser.get("https://rent.591.com.tw/?kind=0&region=1")
    # 關閉選擇區域按鈕
    browser.find_element_by_id('area-box-close').click()
    time.sleep(3)
    # ESC 關閉google 提示       
    browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE) #ECS鍵
    time.sleep(3)    

    with open(outputfile, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 寫出標題
        writer.writerow(['地址', '出租者', '電話', '租金', '坪數', '樓層', '型態', '現況', '格局', '性別要求', '車位','網址'])
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        # 一個頁面 30筆 ，依據搜尋結果的總數 除30 得到總共要翻幾頁
        totalpages = int(bs.find('span', {'class':'TotalRecord'}).text.split(' ')[-2])/30 + 1
        # 顯示總頁數
        print('Total pages: ', int(totalpages))

        for i in range(int(totalpages)):
            room_url_list=[] #存放網址list
            bs = BeautifulSoup(browser.page_source, 'html.parser')
            titles=bs.findAll('h3') # h3 放置物件的區塊
            for title in titles:
                room_url=title.find('a').get('href') # 每個物件的 url
                room_url_list.append(room_url)
            time.sleep(3)

            # 將 getData 的回傳值寫入 csv檔中
            for url in room_url_list:
                # getData 回傳值
                addr,renter,phone,price,size,floor,room_type,condition,form,gender,car,request_url = getData(url)
                
            #--------------------------------------------
            # gender 過濾多餘資料    
                gender_list='男女生皆可'
                gender_result = ''
                counter = 0
                for i in gender:
                    for j in gender_list:
                        if i == j:
                            counter = counter + 1   
                if counter < 5 & counter > 0:
                   gender_result =  gender[:2]    
                else:
                   gender_result =  gender[:5]
            #--------------------------------------------
            # car 過濾多餘資料  
                car_list = '無平面式機械式停車位'
                car_result = ''
                counter = 0
                for i in car:
                    for j in car_list:
                        if i == j:
                            counter = counter + 1                                   
                if counter == 1:
                    car_result =  car[0]    
                else:
                    car_result =  car[:6] 
                if condition == '車位':
                    car_result = '停車位'
            #--------------------------------------------
            # form 過濾多餘資料  
                form_list = '5房4房3房2房1房幾廳幾衛有陽臺'
                form_result = ''
                counter = 0
                for i in form:
                    for j in form_list:
                        if i == j:
                           counter = counter + 1                                   
                if counter == 1:
                    form_result =  form[0]    
                elif counter == 3:
                    form_result =  form[:3] 
                else:
                    form_result = form[:9]
                  
            #--------------------------------------------
            # 寫入 csv        
                writer.writerow([addr,renter,phone,price,size,floor,room_type,condition,form_result,gender_result,car_result,request_url])    
            #--------------------------------------------
            # 偵測是否當前頁面為最後一頁 (利用 find 找 class:'last')
            # 若是最後一頁，跳出 for
            if bs.find('a',{'class':'last'}):
                pass
            else:
                # 若當前頁面不是最後一頁，點選下一頁
                # click下一頁之後，time.sleep(3)些微暫停
                browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)
                browser.find_element_by_class_name('pageNext').click()
                time.sleep(3)

    # 將 rent_591_output.csv 放置 MongoDB
    data_to_dataframe()            
                
if __name__ == '__main__':    
    output_file_name = 'D:/Cathay_bank_HW/rent_591_output.csv'    
    main(output_file_name)
    print('591出租網資料csv輸出完成')

    