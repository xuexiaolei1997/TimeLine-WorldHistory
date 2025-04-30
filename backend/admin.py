from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from models import Event, Period
from database import engine
from fastapi_admin.models import AbstractAdmin

class User(AbstractAdmin):
    pass

async def setup_admin():
    admin_app.add_model_view(Event)
    admin_app.add_model_view(Period)
    
    await admin_app.configure(
        providers=[
            UsernamePasswordProvider(
                login_logo_url=None
            )
        ],
        logo_url=None,
        template_folders=["templates"],
        favicon_url=None,
        engine=engine
    )
