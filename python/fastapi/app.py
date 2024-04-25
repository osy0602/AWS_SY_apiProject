import requests
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import dotenv_values
config = dotenv_values("../../.env")

app = FastAPI()

url = 'http://0.0.0.0:5000/cross_border'  # 5000번 포트에서 가져올게요
response = requests.get(url)
json_data = response.json()
client = MongoClient(host=config["host"], port=27017)

db = client['api_pj']
col = db['cross_border']

@app.get(path='/')
async def connectionCheck():
    return "connected"

#json mongo에 저장
@app.get(path='/dataset')
async def getData():
    col.insert_many(json_data)
    return "dataset saved"

#mongo data delete
@app.get(path='/datasetDelete')
async def deleteData():
    col.delete_many({})
    return "deleted"

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
