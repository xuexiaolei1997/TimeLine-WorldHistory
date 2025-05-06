from pymongo import MongoClient
from contextlib import contextmanager
from typing import Generator
import yaml
import os
from pathlib import Path
import logging
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            config_path = Path(__file__).parent.parent / "config.yaml"
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found at {config_path}")
            
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            if not config.get("database", {}).get("mongodb"):
                raise ValueError("Missing MongoDB configuration in config.yaml")
            
            # Process environment variable placeholders
            mongo_config = {}
            for key, value in config["database"]["mongodb"].items():
                if isinstance(value, str) and value.startswith('${') and '}' in value:
                    var_part = value[2:-1].split(':')
                    env_var = var_part[0]
                    default = var_part[1] if len(var_part) > 1 else ''
                    mongo_config[key] = os.getenv(env_var, default)
                else:
                    mongo_config[key] = value
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
                retryReads=True
            )
            self.db = self.client[mongo_config["database"]]
            
            if not self.check_connection():
                raise ConnectionError("Failed to connect to MongoDB")
                
        except Exception as e:
            logger.error("Database initialization failed", exc_info=True)
            raise

    @contextmanager
    def get_db(self) -> Generator[MongoClient, None, None]:
        try:
            yield self.db
        except PyMongoError as e:
            logger.error("Database operation failed", exc_info=True)
            raise

    def check_connection(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except PyMongoError as e:
            logger.warning("Database connection check failed", exc_info=True)
            return False

db_manager = DatabaseManager()

def get_db():
    return db_manager.get_db()
