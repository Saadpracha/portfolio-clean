from pymongo import MongoClient
from django.conf import settings
import logging
import urllib.parse
import certifi

logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """
    Connect to MongoDB using settings from Django settings
    """
    try:
        # Get MongoDB settings
        mongodb_settings = settings.MONGODB_DATABASES['default']
        
        # Construct connection string if MONGODB_URI is not available
        if not hasattr(settings, 'MONGODB_URI'):
            username = urllib.parse.quote_plus(mongodb_settings['username'])
            password = urllib.parse.quote_plus(mongodb_settings['password'])
            host = mongodb_settings['host']
            port = mongodb_settings['port']
            db_name = mongodb_settings['name']
            
            connection_string = f"mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority"
        else:
            connection_string = settings.MONGODB_URI

        # Create MongoDB client with optimized settings
        client = MongoClient(
            connection_string,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10,
            retryWrites=True,
            retryReads=True
        )
        
        # Test the connection and get database
        db = client[mongodb_settings['name']]
        db.command('ping')
        logger.info("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        raise

def disconnect_from_mongodb(client=None):
    """
    Disconnect from MongoDB
    """
    try:
        if client:
            client.close()
        logger.info("Successfully disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {str(e)}")
        raise 