# main.py
# modules for MongoDB
import motor.motor_asyncio
# modules for TigerGraph
import pyTigerGraph as tg
# modules for FastAPI
import uvicorn
from fastapi import FastAPI, UploadFile

####################
# Connection to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
database = client.photo_library
photo_collection = database.get_collection("photos")

# Add a new photo to MongoDB
async def add_photo_to_MongoDB(photo_data:dict):
    try:
        entry = await photo_collection.insert_one(photo_data)
        return str(entry.inserted_id) 
    except:
        return False

####################
# Connection to TigerGraph
conn = tg.TigerGraphConnection(
    host="https://photo-library.i.tgcloud.io",
    graphname="photos",
    username="tigergraph",
    password="tigergraph", )
conn.apiToken = conn.getToken(conn.createSecret())
#conn.apiToken = ('...', ..., '...')
async def add_photo_id_to_TigerGraph(id: str):
    try:
        conn.upsertVertex("Photo", id, {})
        return True
    except:
        return False

####################
# API endpoints
app = FastAPI()

@app.post("/uploadPhoto/")
async def upload_photo(file: UploadFile):
    contents = await file.read()
    # add to MongoDB
    data = { "photo": contents }
    photoID = await add_photo_to_MongoDB(data)
    success = await add_photo_id_to_TigerGraph(photoID)
    if success:
        return { "code": 200, "message": "Photo uploaded"}
    else:
        return { "code": 401, "message": "Failed to add photo"}

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)