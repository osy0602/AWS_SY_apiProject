import requests
from fastapi import FastAPI
from pymongo import MongoClient
# from dotenv import dotenv_values
import pandas as pd
# config = dotenv_values("../../.env")
import os.path
import json


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

app = FastAPI()

url = 'http://0.0.0.0:5000/cross_border'  # 5000번 포트에서 가져올게요
client = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}')

db = client['api_pj']
col = db['cross_border']



#json server에 있는 data 받아오기
@app.get(path='/getDataJSON')
async def getDataJSON():
    response = requests.get(url)
    json_data = response.json()
    return json_data

#json data mongo insert
@app.get(path='/datainsert')
async def insertData():
    response = await getDataJSON()
    col.insert_many(response)
    return col.find_one({},{"_id":0})

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
    result= {"resultcode": response.status_code}
    if year is None and subject is None:
        listtmp = list(col.find({}, { "_id":0}))
    elif subject is None:
        listtmp = list(col.find({}, {"상품군별(1)":1, str(year):1, str(year)+"1":1, str(year)+"2":1, "_id":0}))
    elif year is None:
        listtmp = col.find_one({"상품군별(1)":subject},{'_id':0})
    result['result'] = listtmp
    
    return result

