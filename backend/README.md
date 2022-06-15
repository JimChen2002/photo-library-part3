# Photo Library (backend)

Photo hosting service with image classification and searching

Part I: Upload Photos

This code implement an API endpoint that takes a photo in form data as input, store the photo bytes in a document of MongoDB, and store the document's object ID in TigerGraph. You can test it on the documentation page.
![doc](https://github.com/JimChen2002/photo-library-part1/blob/master/demo_images/backend-doc.png)

## Install the dependencies
```bash
pip3 install -r requirements.txt
```

### Start the app
```bash
python3 main.py
```

### Default host
http://localhost:8000/

### Automatically generated documentation
http://localhost:8000/docs/