# Photo Library (backend)

Photo hosting service with image classification and searching

This code implements the API endpoints that tag, store, and serve photos.

## Installation

### Set up virtual environment
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

### Install dependencies
```bash
$ pip3 install -r requirements.txt
$ python3 -m pip install tensorflow
```

### Train and save the image classification model
```bash
$ python3 ML.py
```

### Start the app
```bash
$ python3 main.py
```

### Default host
http://localhost:8000/

### Automatically generated documentation
http://localhost:8000/docs/