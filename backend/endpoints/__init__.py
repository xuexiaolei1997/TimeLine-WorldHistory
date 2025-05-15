from fastapi import APIRouter

# Initialize the main router with proper OpenAPI tags
router = APIRouter(
    tags=["default"],
    responses={404: {"description": "Not found"}},
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name
)
