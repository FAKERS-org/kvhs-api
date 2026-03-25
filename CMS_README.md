# KVHS School Management System with CMS API

A comprehensive Content Management System (CMS) API built for state high schools using FastAPI, SQLAlchemy, and JWT authentication.

## Features

### Core School Management
- **Student Management**: CRUD operations for student records
- **Teacher Management**: CRUD operations for teacher records
- **Course Management**: Course creation and assignment
- **Enrollment Management**: Student-course enrollment tracking

### CMS Features
- **Content Management**: Create, read, update, delete content (pages, announcements, policies, lesson plans, syllabi, assignments, course materials)
- **Document Management**: Upload and manage documents with file metadata
- **Calendar System**: Create and manage school events with date ranges
- **Department Organization**: Organize content by departments
- **Tagging System**: Tag content for better organization and search
- **Hierarchical Content**: Support for parent-child content relationships
- **Publishing Workflow**: Simple publish/unpublish content status

### Academic Performance Tracking
- **Attendance Tracking**: Record student attendance per course
- **Assignment Scores**: Track student assignment submissions and grades

### Advanced Features
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Admin, Teacher, Staff, and Student roles
- **Search Functionality**: Full-text search with filters for tags, categories, and departments
- **CORS Support**: Configurable CORS for frontend integration

## Technology Stack

- **Framework**: FastAPI 0.129.0+
- **ORM**: SQLAlchemy 2.0.46+ with modern declarative mapping
- **Database**: SQLite (default), MySQL, PostgreSQL supported
- **Authentication**: JWT with python-jose, passlib with bcrypt
- **Python**: 3.12+
- **Package Manager**: UV

## Installation

### Prerequisites
- Python 3.12 or higher
- UV package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
cd kvhs-api
```

2. Create a virtual environment and install dependencies:
```bash
# Using UV (recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Edit `.env` file and update the SECRET_KEY:
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
```

5. Run the application:
```bash
# Using UV
uv run uvicorn app.main:app --reload

# Or using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## User Roles and Permissions

### Admin
- Full access to all CMS features
- Can create, update, delete any content
- Can manage departments and tags
- Can manage all users

### Teacher
- Can create and manage course-related content
- Can only update/delete their own content
- Can view all published content
- Can create calendar events and documents

### Staff
- Similar to Admin but focused on announcements and policies
- Can manage school-wide content

### Student
- Read-only access to published content
- Can view their own academic records
- Can view calendar events

## Quick Start Guide

### 1. Register Users

#### Register an Admin
The first admin can be registered publicly. Subsequent admin registrations require an existing admin's authorization.

```bash
curl -X POST "http://localhost:8000/auth/register/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "ADM001",
    "name": "John Admin",
    "email": "admin@school.com",
    "password": "securepass123"
  }'
```

#### Register a Teacher
Requires admin or staff authorization.

```bash
curl -X POST "http://localhost:8000/auth/register/teacher" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "teacher_id": "TCH001",
    "name": "Jane Teacher",
    "email": "teacher@school.com",
    "department": "Mathematics",
    "hired_date": "2024-01-01",
    "password": "securepass123"
  }'
```

#### Register a Student
Requires admin or staff authorization.

```bash
curl -X POST "http://localhost:8000/auth/register/student" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "student_id": "STU001",
    "name": "Bob Student",
    "email": "student@school.com",
    "grade_level": 10,
    "enrolled_date": "2024-01-15",
    "password": "securepass123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the API with Authentication

Use the `access_token` in the Authorization header:

```bash
curl -X GET "http://localhost:8000/content/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Endpoints Overview

### Authentication
- `POST /auth/register/admin` - Register admin user (Public for first admin, then Admin only)
- `POST /auth/register/teacher` - Register teacher user (Admin/Staff only)
- `POST /auth/register/student` - Register student user (Admin/Staff only)
- `POST /auth/login` - Login and get tokens

### Content Management
- `POST /content/` - Create content (teacher/admin)
- `GET /content/` - List content (with filters)
- `GET /content/{id}` - Get specific content
- `PUT /content/{id}` - Update content (owner/admin)
- `DELETE /content/{id}` - Delete content (owner/admin)
- `POST /content/{id}/publish` - Publish content
- `POST /content/{id}/unpublish` - Unpublish content

### Documents
- `POST /documents/` - Upload document
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document
- `PUT /documents/{id}` - Update document metadata
- `DELETE /documents/{id}` - Delete document

### Calendar
- `POST /calendar/events` - Create event
- `GET /calendar/events` - List events (with date filters)
- `GET /calendar/events/{id}` - Get event
- `PUT /calendar/events/{id}` - Update event
- `DELETE /calendar/events/{id}` - Delete event

### CMS Utilities
- `POST /cms/departments` - Create department (admin)
- `GET /cms/departments` - List departments
- `GET /cms/departments/{id}` - Get department
- `PUT /cms/departments/{id}` - Update department (admin)
- `DELETE /cms/departments/{id}` - Delete department (admin)
- `POST /cms/tags` - Create tag (admin)
- `GET /cms/tags` - List tags
- `DELETE /cms/tags/{id}` - Delete tag (admin)

### Search
- `POST /search/` - Advanced search with filters
- `GET /search/?q=query` - Simple text search

### School Management (Original)
- `GET /students/` - List students
- `POST /students/` - Create student
- `GET /students/{id}` - Get student
- `PUT /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student

Similar endpoints exist for `/teachers/`, `/courses/`, and `/enrollments/`

## Database Models

### CMS Models

#### Content
- Supports multiple content types: pages, announcements, policies, lesson plans, syllabi, assignments, course materials
- Hierarchical organization (parent-child relationships)
- Publishing workflow (draft, published, unpublished)
- Tags for categorization
- Department and course associations

#### Document
- File metadata storage
- Association with content or courses
- Tracks uploader (teacher/admin)

#### CalendarEvent
- Date/time ranges
- All-day event support
- Course and department associations
- Event types (exam, holiday, meeting, etc.)

#### Department
- Organizes content and teachers
- Description field

#### ContentTag
- Simple tagging system
- Many-to-many with Content

### Academic Models

#### Attendance
- Track student presence in courses
- Status: present, absent, late, excused
- Notes field for additional info

#### AssignmentScore
- Links to Content (assignments)
- Score and max_score tracking
- Submission and grading timestamps
- Feedback field

## Content Types

The system supports the following content types:
- `page` - General pages
- `announcement` - School announcements
- `policy` - School policies
- `lesson_plan` - Teacher lesson plans
- `syllabus` - Course syllabi
- `assignment` - Student assignments
- `course_material` - General course materials

## Publishing Workflow

Content can have three statuses:
- `draft` - Not visible to students
- `published` - Visible to all users
- `unpublished` - Previously published but now hidden

## Search Capabilities

The search system supports:
- Full-text search in title and body
- Filter by content type
- Filter by department
- Filter by tags (multiple)
- Filter by publish status (admin/teacher only)

## Security Considerations

1. **Change the SECRET_KEY**: Always use a strong, random secret key in production
2. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
3. **Database**: Use PostgreSQL or MySQL in production instead of SQLite
4. **Password Policy**: Implement minimum password requirements
5. **Rate Limiting**: Add rate limiting middleware for production
6. **Input Validation**: All inputs are validated using Pydantic schemas

## Environment Variables

See `.env.example` for all configuration options:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiration (default: 7)
- `ALLOWED_ORIGINS` - CORS allowed origins
- `UPLOAD_DIR` - Directory for file uploads
- `MAX_UPLOAD_SIZE` - Maximum upload size in bytes

## Development

### Running Tests
```bash
# Tests will be added in future updates
pytest
```

### Database Migrations
Currently using `Base.metadata.create_all()` for auto-creation. For production:
1. Install Alembic: `uv add alembic`
2. Initialize: `alembic init alembic`
3. Create migrations: `alembic revision --autogenerate -m "message"`
4. Apply migrations: `alembic upgrade head`

## Docker Deployment

A `docker-compose.yml` is provided in the root directory with PostgreSQL setup:

```bash
docker-compose up -d
```

Update `DATABASE_URL` in `.env` to use PostgreSQL:
```
DATABASE_URL=postgresql://kvhs:kvhs@localhost:5432/kvhs
```

## Project Structure

```
kvhs-api/
├── app/
│   ├── core/               # Core utilities
│   │   ├── config.py       # Settings and configuration
│   │   ├── security.py     # JWT and password utilities
│   │   └── dependencies.py # Auth dependencies
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication
│   │   ├── content.py      # Content management
│   │   ├── documents.py    # Document management
│   │   ├── calendar.py     # Calendar events
│   │   ├── cms_utils.py    # Departments and tags
│   │   ├── search.py       # Search functionality
│   │   ├── students.py     # Student management
│   │   ├── teachers.py     # Teacher management
│   │   ├── courses.py      # Course management
│   │   └── enrollments.py  # Enrollment management
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # Database configuration
│   └── main.py             # FastAPI application
├── .env.example            # Environment template
├── pyproject.toml          # Dependencies
└── README.md               # This file
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines]

## Support

For issues and questions, please open an issue on GitHub.
