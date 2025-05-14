from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import yaml
import os
import logging
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

def check_mongo_connection():
    """
    检查MongoDB连接是否可用
    Returns:
        bool: 连接是否成功
    """
    try:
        # Load database configuration
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            mongo_config = config.get("database", {}).get("mongodb", {})

        if not mongo_config:
            raise DatabaseError({
                "message": "MongoDB configuration not found",
                "details": {"config_file": "config.yaml"}
            })

        # Create test client
        client = MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
            username=os.getenv("MONGO_USERNAME") or mongo_config.get("username"),
            password=os.getenv("MONGO_PASSWORD") or mongo_config.get("password"),
            authSource=mongo_config.get("auth_source", "admin"),
            serverSelectionTimeoutMS=5000
        )

        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        logger.info("MongoDB connection check successful")
        return True

    except ConnectionFailure as e:
        logger.error("MongoDB connection check failed", exc_info=True)
        raise DatabaseError({
            "message": "Failed to connect to MongoDB",
            "details": {
                "error": str(e),
                "host": mongo_config.get("host"),
                "port": mongo_config.get("port")
            }
        })
    except ServerSelectionTimeoutError as e:
        logger.error("MongoDB server selection timeout", exc_info=True)
        raise DatabaseError({
            "message": "MongoDB server selection timeout",
            "details": {
                "error": str(e),
                "host": mongo_config.get("host"),
                "port": mongo_config.get("port"),
                "timeout": "5000ms"
            }
        })
    except Exception as e:
        logger.error("Unexpected error during MongoDB connection check", exc_info=True)
        raise DatabaseError({
            "message": "Unexpected error during MongoDB connection check",
            "details": {"error": str(e)}
        })

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    try:
        check_mongo_connection()
    except DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
