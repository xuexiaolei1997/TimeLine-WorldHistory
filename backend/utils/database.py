from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure
from contextlib import contextmanager
from typing import Generator
import yaml
import os
import logging
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        try:
            # Load database configuration
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                mongo_config = config.get("database", {}).get("mongodb", {})

            if not mongo_config:
                raise ValueError("MongoDB configuration not found in config.yaml")

            # Create MongoDB client with enhanced options
            self.client = MongoClient(
                host=mongo_config["host"],
                port=mongo_config["port"],
                username=os.getenv("MONGO_USERNAME") or mongo_config.get("username"),
                password=os.getenv("MONGO_PASSWORD") or mongo_config.get("password"),
                authSource=mongo_config.get("auth_source", "admin"),
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                maxPoolSize=50,
                retryWrites=True,
                retryReads=True,
                w="majority",  # Write concern for better consistency
                readPreference="primaryPreferred"  # Read preference for better availability
            )
            
            self.db = self.client[mongo_config["database"]]
            
            if not self.check_connection():
                raise ConnectionFailure("Failed to connect to MongoDB")
                
        except Exception as e:
            logger.error("Database initialization failed", exc_info=True)
            raise DatabaseError({
                "message": "Failed to initialize database connection",
                "details": {"error": str(e)}
            })

    @contextmanager
    def get_db(self) -> Generator[MongoClient, None, None]:
        try:
            if not self.check_connection():
                # Try to reconnect
                self.client.admin.command('ping')
            yield self.db
        except PyMongoError as e:
            logger.error("Database operation failed", exc_info=True)
            raise DatabaseError({
                "message": "Database operation failed",
                "details": {"error": str(e)}
            })

    def check_connection(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except PyMongoError as e:
            logger.warning("Database connection check failed", exc_info=True)
            return False
            
    def close(self):
        try:
            if self.client:
                self.client.close()
        except PyMongoError as e:
            logger.error("Error closing database connection", exc_info=True)
            raise DatabaseError({
                "message": "Failed to close database connection",
                "details": {"error": str(e)}
            })

# Create a global instance
db_manager = DatabaseManager()
