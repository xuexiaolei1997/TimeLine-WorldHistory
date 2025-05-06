from database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_mongo():
    try:
        # Check connection
        if not db_manager.check_connection():
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Get database
        db = db_manager.db
        logger.info(f"Connected to MongoDB database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        logger.info(f"Collections: {collections}")
        
        # Check if events collection exists
        if "events" not in collections:
            logger.warning("'events' collection does not exist")
            return False
            
        return True
        
    except Exception as e:
        logger.error("MongoDB check failed", exc_info=True)
        return False

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))
    check_mongo()
