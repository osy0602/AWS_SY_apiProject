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
from models import Jikgu
import uuid


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

# year | subject input 후 해당하는 data 가져오기
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

@app.get('/insertSQL')
async def insertSQL(year = null):
    data = await selectShop(year)
    data = data['result']
    result = session.query(Jikgu).filter(Jikgu.year == year).all()
    if (len(result) != 0):
        return {'resultcode' : 201 , "result":result}
    for i in range(1, len(data)):
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
    result = session.query(Jikgu).all()
    return result

    # print(data[0]['상품군별(1)'])