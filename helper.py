from dotenv import load_dotenv
import os

load_dotenv()

def getUsername():
    return os.getenv('USERNAME')

def getPassword():
    return os.getenv('PASSWORD')

def getDatabaseFileName():
    return os.getenv('DATABASE_FILE_NAME')

def getDatabaseFilePath():
    return 'data/' + os.getenv('DATABASE_FILE_NAME')