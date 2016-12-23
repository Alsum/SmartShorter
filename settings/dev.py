# settings/prod.py

class Config:

    # Database
    MONGO_URI = 'mongodb://localhost:27017/mydb'

    # Debugging
    DEBUG = True

    # Networking
    PORT = 5000
