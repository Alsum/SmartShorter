# settings/prod.py

class Config:

    # Database
    MONGO_URI = 'mongodb://localhost:27017/mydb'
    # MONGO_USERNAME = 'mydb'
    # MONGO_PASSWORD = 'password'

    # Debugging
    DEBUG = False

    # Networking
    PORT = 5000
    # PREFERRED_URL_SCHEME = 'https'
    # SERVER_NAME = 'mywebsite.com'