# main.py
# modules for MongoDB
import motor.motor_asyncio

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

####################
# API endpoints
app = FastAPI()

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

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)