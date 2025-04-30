# Backend Documentation

## Overview
The backend is built with Python using FastAPI framework. It provides RESTful APIs for managing historical events and periods.

## Directory Structure
```
backend/
├── api/           - API routers
├── core/          - Core utilities and base classes
├── endpoints/     - API endpoint definitions
├── models/        - Database models
├── schemas/       - Pydantic schemas
├── services/      - Business logic
└── utils/         - Utility functions
```

## Key Components

### Models
- `event.py`: Historical event model
- `period.py`: Historical period model

### Services
- `event_service.py`: CRUD operations for events
- `period_service.py`: CRUD operations for periods

### Schemas
- `event_schemas.py`: Pydantic schemas for event validation
- `period_schemas.py`: Pydantic schemas for period validation

### Endpoints
- `events.py`: Event-related API endpoints
- `periods.py`: Period-related API endpoints

## Main Files
- `main.py`: FastAPI application entry point
- `database.py`: Database connection and setup
- `requirements.txt`: Python dependencies

## API Documentation
The backend provides RESTful endpoints for:
- Creating/reading/updating/deleting historical events
- Creating/reading/updating/deleting historical periods
- Searching and filtering historical data

All endpoints follow standard HTTP methods and return JSON responses.
