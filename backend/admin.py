from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.models import AbstractAdmin
from models.event import Event
from models.period import Period
from utils.database import db_manager
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class User(AbstractAdmin):
    """Admin user model for authentication and authorization"""
    pass

async def setup_admin():
    """Initialize and configure the admin interface"""
    try:
        # Load admin configuration from config.yaml
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f).get("admin", {})
        
        # Register model views
        admin_app.add_model_view(Event)
        admin_app.add_model_view(Period)
        
        # Configure admin interface
        await admin_app.configure(
            providers=[
                UsernamePasswordProvider(
                    login_logo_url=config.get("login_logo_url"),
                    admin_model=User
                )
            ],
            logo_url=config.get("logo_url"),
            template_folders=["templates"],
            favicon_url=config.get("favicon_url"),
            engine=db_manager.db
        )
        logger.info("Admin interface initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize admin interface", exc_info=True)
        raise
