import requests
from fastapi import FastAPI
from pymongo import MongoClient
# from dotenv import dotenv_values
import pandas as pd
# config = dotenv_values("../../.env")
import os.path
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from models import Jikgu,JPData,JPDictData
import uuid
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dtaidistance import dtw
from flask import Flask, render_template
from wordcloud import WordCloud


BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, '../../secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg

HOSTNAME = get_secret("Local_Mongo_Hostname")
USERNAME = get_secret("Local_Mongo_Username")
PASSWORD = get_secret("Local_Mongo_Password")
APIKEY = get_secret("data_apiKey")
PORT = get_secret("Mysql_Port")
SQLUSERNAME = get_secret("Mysql_Username")
SQLPASSWORD = get_secret("Mysql_Password")
SQLDBNAME = get_secret("Mysql_DBname")
TEAMHOSTNAME = get_secret("My_Team_Hostname")

DB_URL = f'mysql+pymysql://{SQLUSERNAME}:{SQLPASSWORD}@{HOSTNAME}:{PORT}/{SQLDBNAME}'

class db_conn:
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle=500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
    
    def connection(self):
        conn = self.engine.connection()
        return conn
    
app = FastAPI()

url = 'http://0.0.0.0:5000/cross_border'  # 5000번 포트에서 가져올게요
client = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}')

db = client['api_pj']
col = db['cross_border']

sqldb = db_conn()
session = sqldb.sessionmaker()


#json server에 있는 data 받아오기
@app.get(path='/getDataJSON')
async def getDataJSON():
    response = requests.get(url)
    json_data = response.json()
    response_code = response.status_code

    return {"result_code" : response_code, "result": json_data}

#json data mongo insert
@app.get(path='/dataInsert')
async def insertData():
    response = await getDataJSON()
    response_data = response.get("result", [])
    response_code = response.get("result_code",)
    col.insert_many(response_data)
    return {"result_code" : response_code, "result": col.find_one({},{"_id":0})}

#mongo data get
@app.get(path='/get')
async def get():
    data = list(col.find({},{"_id":0}))
    if len(data) == 0:
        data = await insertData()
    result = list(col.find({},{"_id":0}))
    return result

#mongo data delete
@app.get(path='/datasetDelete')
async def deleteData():
    col.delete_many({})
    return "deleted"

# year | subject input 후 해당하는 data mongo에서 가져오기
@app.get(path='/shop')
async def selectShop(year=None, subject=None):
    # result= {"resultcode": response_code}
    if year is None and subject is None:
        listtmp = list(col.find({}, { "_id":0}))
    elif subject is None:
        listtmp = list(col.find({}, {"상품군별(1)":1, str(year):1, str(year)+"1":1, str(year)+"2":1,"_id":0}))
    elif year is None:
        listtmp = col.find_one({"상품군별(1)":subject},{'_id':0})
    # result= {"resultcode": response_code}
    # result['result'] = listtmp
    
    return {"response_code":200, "result":listtmp}

@app.get('/getJikguAll')
async def getAll():
    result = session.query(Jikgu)
    return result.all()

# sql에 상품군별 insert하기
@app.get('/insertSQL')
async def insertSQL(year = null):
    data = await selectShop(year)
    data = data['result']
    result = session.query(Jikgu).filter(Jikgu.year == year).all()
    column_list_sample = ['사무·문구','가전·전자·통신기기','컴퓨터 및 주변기기','음·식료품','의류 및 패션 관련 상품','생활·자동차용품','스포츠·레저용품','기 타']
    #print(result)
    if (len(result) != 0):
        return {'resultcode' : 201 , "result":result}
    for i in range(1, len(data)):
        if(data[i]['상품군별(1)'] not in column_list_sample):
            continue
        id = str(uuid.uuid4())
        subject = data[i]['상품군별(1)']
        purchase = data[i][str(year)]
        percentage = data[i][str(year)+'2']
        new_jikgu = Jikgu(id = id,year = year,subject=subject, purchase=purchase, percentage=percentage)
        session.add(new_jikgu)
        session.commit()
        session.refresh(new_jikgu)
    result = session.query(Jikgu).filter(Jikgu.year == year).all()
    return {"resultcode": 200, "result" : result}

@app.get('/getSQL')
async def selectGet(year=null):
    result = session.query(Jikgu)
    return result.all()

    # print(data[0]['상품군별(1)'])

# 현주 api 접근해서 내 몽고디비에 전처리 해서 저장
@app.get('/getMallData')
async def failedMall():
    # 현주 api 접근
    response = requests.get('http://'+TEAMHOSTNAME+":3500/insertSQL")
    response = response.json()
    response = response['result']
    df_failedMall = pd.DataFrame(response)
    
    #column 맞추는 작업 위해 정제
    column_dict = {'교육/도서/완구/오락':'사무·문구','가전':'가전', '컴퓨터/사무용품':'컴퓨터', '가구/수납용품':0, '건강/식품':'음·식료품', '의류/패션/잡화/뷰티':'의류 및 패션 관련 상품 + 화장품', '자동차/자동차용품':'생활·자동차용품', '레져/여행/공연':'스포츠·레저용품', '기타':'기 타'}
    df_failedMall['subject'] = df_failedMall['subject'].map(column_dict)
    df_filtered = df_failedMall[df_failedMall['subject'] != 0]
    # df_filtered = df_filtered.set_index('subject')
    print(df_filtered)
    
    #내 mongodb 접근해서 데이터 가져옴
    col = db['cross_border']
    column_list = ['사무·문구','가전','컴퓨터','음·식료품','의류 및 패션 관련 상품 + 화장품','생활·자동차용품','스포츠·레저용품','기 타']
    
    #증감량만 가져오기
    tmp_list = list(col.find({}, {"상품군별(1)":1, "20192":1,"20202":1,"20212":1,"20222":1,"20232":1,"_id":0}))
    df_mall = pd.DataFrame(tmp_list)
    column_list_sample = ['사무·문구','가전·전자·통신기기','컴퓨터 및 주변기기','음·식료품','의류 및 패션 관련 상품','생활·자동차용품','스포츠·레저용품','기 타']

    my_mall_dict = []
    for i in column_list_sample:
        tmp_list = df_mall[df_mall['상품군별(1)'] == i]
        tmp_dict = {i:list(tmp_list.iloc[:,0:5].values[0])}
        my_mall_dict.append(tmp_dict)
    

    temp = []
    tmp_list = []
    closed_mall_dict = []
    for i in column_list:
        for j in range(2019, 2024):
            tmp_list = df_filtered[(df_filtered['subject'] == i) & (df_filtered['year'] == j)]
            temp.append(tmp_list.iloc[:,3:4].values[0][0])
        closed_mall_dict.append({i : temp})
        temp = []
    print(my_mall_dict)
    print(closed_mall_dict)
    
    col = db['data_calc']
    col.insert_one({'shopping':my_mall_dict})
    col.insert_one({'mall': closed_mall_dict})
        
    return {"result code":200, "result":my_mall_dict}


@app.get('/getCalcData')
async def calcData():
    col = db['data_calc']
    shopping = (list(col.find({}, {"shopping":1, '_id':0})))[0]['shopping']
    # print(shopping)
    closed = (list(col.find({}, {"mall":1, '_id':0})))[1]['mall']
    # print(shopping[0]['shopping'][0]['컴퓨터 및 주변기기'][0])
    # print(closed[0]['사무·문구'])
    column_list = ['사무·문구','가전','컴퓨터','음·식료품','의류 및 패션 관련 상품 + 화장품','생활·자동차용품','스포츠·레저용품','기 타']
    column_list_sample = ['사무·문구','가전·전자·통신기기','컴퓨터 및 주변기기','음·식료품','의류 및 패션 관련 상품','생활·자동차용품','스포츠·레저용품','기 타']
    sync_list = []
    year_list = [2019,2020,2021,2022,2023]
    for i in range(len(column_list)):
        closed_data = list(map(float, closed[i][column_list[i]]))
        shopping_data = shopping[i][column_list_sample[i]]
        distance = dtw.distance(closed_data, shopping_data)
        sync_list.append(distance)
        plt.rcParams['font.family'] = 'NanumBarunGothic'
        plt.figure()
        plt.plot(year_list, shopping_data, label = '직구')
        plt.plot(year_list, closed_data, label = '폐업')
        plt.title(column_list_sample[i] + '연도별 증감율 비교')
        plt.legend()
        plt.savefig('../../front/public/'+column_list_sample[i] +'.png')

    
    sync_dict = dict(zip(column_list_sample, sync_list))
    return {"result code" : 200, "result" :sync_dict}

# graph data sql로 insert하기
@app.get('/insertImage')
async def insertImage():
    for filename in os.listdir('./'):
        if filename.endswith(".png"):
            file_path = os.path.join('./', filename)
            with open(file_path, 'rb') as f:
                image_data = f.read()
            jpdata = JPData(subject = filename, image = image_data)
            session.add(jpdata)
            session.commit()
            print("image inserted")
            session.close()
    


@app.get('/insertDtwData')
async def insertDtw():
    dict = await calcData()
    if len(session.query(JPDictData).all()) != 0:
        return dict
    for k, v in dict.items():
        data = JPDictData(subject = k, data = v)
        session.add(data)
        session.commit()
        print("insert completed")
        session.close()
    return dict

# 현주한테 줘야하는 api 연도별 subject별 구매율 뽑아야함 
@app.get('/usingData')
async def usingData():
    col = db['cross_border']
    tmp_list = list(col.find({}, {"상품군별(1)":1, "2019":1,"2020":1,"2021":1,"2022":1,"2023":1,"_id":0}))
    #column_list_sample = ['사무·문구','가전·전자·통신기기','컴퓨터 및 주변기기','음·식료품','의류 및 패션 관련 상품','생활·자동차용품','스포츠·레저용품','기 타']
    # select_list =[]
    # for item in tmp_list:
    #     if item['상품군별(1)'] in column_list_sample:
    #         select_list.append(item)
    filtered_data = [item for item in tmp_list if item["상품군별(1)"] == "합계"]

    return {"result code" :200, "result" :filtered_data}

@app.get('/piechart')
async def piechart():
    col = db['cross_border']
    tmp_list = list(col.find({}, {"상품군별(1)":1, "2019":1,"2020":1,"2021":1,"2022":1,"2023":1,"_id":0}))

    result = [(data['2023'], data['상품군별(1)']) for data in tmp_list if '2023' in data]
    result.pop(0)
    print(result)
    categories = [data[1] for data in result]  # 카테고리
    sales = [data[0] for data in result] 
    # 판매량 기준으로 정렬 (내림차순)
    sorted_idx = np.argsort(sales)  # 인덱스 추출
    top10_idx = sorted_idx[-8:]  # 상위 10개 인덱스

    # 상위 10개 카테고리와 판매량 추출
    top10_categories = [categories[i] for i in top10_idx]
    top10_sales = [sales[i] for i in top10_idx]
    plt.rcParams['font.family'] = 'NanumBarunGothic'
    colors = ['#34617c', '#56829c', '#86a8bd', '#b1d5d6', '#9fc8c9']
    plt.pie(top10_sales, labels=top10_categories,colors = colors, autopct="%1.1f%%") 
    plt.savefig('../../front/public/pichart.png')



