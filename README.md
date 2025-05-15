# Timeline World History

A interactive web application for visualizing and exploring world history events on a 3D globe with timeline controls.

## Features

- 3D Earth visualization with historical events
- Timeline-based navigation
- Multi-language support (English/Chinese)
- Event management with categories and importance levels
- Media attachments support (images, videos, audios)
- Advanced filtering and search capabilities
- Region-based event grouping
- Administrative interface for content management

## Technology Stack

- Frontend:
  - React.js
  - Material-UI
  - Three.js for 3D visualization
  - i18next for internationalization
  
- Backend:
  - Python FastAPI
  - MongoDB
  - Redis for caching (optional)

## Prerequisites

- Node.js >= 16.x
- Python >= 3.10
- MongoDB >= 6.0
- Docker (optional)

## Development Setup

### Local Development

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd TimeLine-WorldHistory
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Start MongoDB:
   Make sure MongoDB is running on localhost:27017

5. Start the development servers:
   ```bash
   # In the root directory
   npm run start:dev
   ```

### Docker Deployment

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

- `/src` - Frontend React application
  - `/components` - React components
  - `/locales` - Translation files
  - `/utils` - Utility functions

- `/backend` - Python FastAPI backend
  - `/endpoints` - API routes
  - `/schemas` - Data models and validation
  - `/services` - Business logic
  - `/utils` - Helper functions

- `/docs` - Documentation and database initialization files
- `/public` - Static assets and mock data

## Configuration

### Environment Variables

Frontend (/.env):
```
REACT_APP_API_URL=http://localhost:8000
```

Backend (/backend/config.yaml):
```yaml
mongodb:
  uri: mongodb://localhost:27017/timeline
environment: development
```

## API Documentation

The API documentation is available at `/docs` when the backend server is running. It provides detailed information about all available endpoints and their usage.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
