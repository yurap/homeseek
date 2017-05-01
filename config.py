import os.path

class Config:
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB  = 'homeseek'
    BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_FOLDER = BASE_FOLDER + '/templates'
    STATIC_FOLDER    = BASE_FOLDER + '/static'
    DATA_FOLDER      = BASE_FOLDER + '/data'
    FB_TOKEN_FILE = DATA_FOLDER + '/fb_token'
