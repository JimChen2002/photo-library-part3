# main.py
# modules for MongoDB
import motor.motor_asyncio
from bson.objectid import ObjectId

# modules for TigerGraph
import pyTigerGraph as tg

# modules for ML model
import os
import tensorflow as tf
import numpy as np
import uuid
from PIL import Image
import matplotlib.pyplot as plt

# modules for FastAPI
import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
import base64
from fastapi.middleware.cors import CORSMiddleware
from typing import Union

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

# Get a specific photo from MongoDB by ID
async def retrieve_photo_from_MongoDB(id:str):
    try:
        entry = await photo_collection.find_one({"_id": ObjectId(id)})
        if entry:
            return entry
        else:
            return False
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
async def add_photo_id_with_predictions_into_TigerGraph(id: str, predictions: list):
    try:
        class_names = ['T-shirt', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle-boot']
        conn.upsertVertex("Photo", id, {})
        # only need to insert type vertexes once
        for name in class_names:
            conn.upsertVertex("Type", name, {})
        threshold = 0.01
        for idx, probability in enumerate(predictions):
            if probability >= threshold:
                conn.upsertEdge("Photo", id, "PHOTO_HAS_TYPE", "Type", class_names[idx], {"probability": probability})
        return True
    except:
        return False

async def retrieve_all_photo_info_from_TigerGraph(text: str):
    try:
        threshold = 0.5
        results = conn.runInstalledQuery("FetchAllPhotos", params={
            "text": text, 
            "threshold": threshold
        })
        ret = []
        for photo_info in results[0]["result"]:
            ret.append(photo_info["attributes"]["id"])
        return ret
    except:
        return False

####################
# API endpoints
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model('my_model')
probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

@app.post("/uploadPhoto/")
async def upload_photo(file: UploadFile):
    contents = await file.read()
    data = { "photo": contents }
    photoID = await add_photo_to_MongoDB(data)
    unique_file_path = str(uuid.uuid4()) + file.filename
    with open(unique_file_path, 'wb') as f:
      f.write(contents)
    img=Image.open(unique_file_path)
    os.remove(unique_file_path)
    small_img=img.resize((28,28),Image.Resampling.BILINEAR)
    BW_small_img=small_img.convert("L")
    pix = np.array(BW_small_img)
    img = np.expand_dims(pix,0) / 255.0
    predictions = probability_model.predict(img)
    success = await add_photo_id_with_predictions_into_TigerGraph(photoID, predictions[0].tolist())
    if success:
        return { "code": 200, "message": "Photo uploaded"}
    else:
        return { "code": 401, "message": "Failed to add photo"}

@app.put("/retrievePhoto/{id}")
async def retrieve_photo(id: str):
    data = await retrieve_photo_from_MongoDB(id)
    if not data:
        return { "code": 401, "message": "Failed to get photo."}
    contents = data["photo"]
    contents=base64.b64encode(contents)
    return Response(content=contents, media_type="image/png")

@app.put("/retrieveAllPhotoInfo")
async def retrieve_all_photo_info(text: Union[str, None] = None):
    if text is None:
        data = await retrieve_all_photo_info_from_TigerGraph("")
    else:
        data = await retrieve_all_photo_info_from_TigerGraph(text)
    if not data:
        return { "code": 401, "message": "Failed to retrieve photo"}
    else:
        return { "code": 200, "data": data, "message": "Photo fetched" }

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)