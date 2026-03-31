# KVHS CMS API Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     KVHS CMS API (FastAPI)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Authentication Layer                   │ │
│  │  - JWT Token Generation/Validation                        │ │
│  │  - Password Hashing (Bcrypt)                              │ │
│  │  - Role-Based Access Control (RBAC)                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                      API Routes                           │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ /auth          - Authentication (Login, Register)         │ │
│  │ /content       - Content Management (CRUD)                │ │
│  │ /documents     - Document Management (CRUD)               │ │
│  │ /calendar      - Calendar Events (CRUD)                   │ │
│  │ /cms           - Departments & Tags (CRUD)                │ │
│  │ /search        - Search Functionality                     │ │
│  │ /students      - Student Management (Original)            │ │
│  │ /teachers      - Teacher Management (Original)            │ │
│  │ /courses       - Course Management (Original)             │ │
│  │ /enrollments   - Enrollment Management (Original)         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Business Logic Layer                    │ │
│  │  - Content Publishing Workflow                            │ │
│  │  - Permission Checks                                      │ │
│  │  - Search Algorithms                                      │ │
│  │  - Data Validation (Pydantic)                             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                  Data Access Layer (ORM)                  │ │
│  │  - SQLAlchemy 2.0+ Models                                 │ │
│  │  - Database Session Management                            │ │
│  │  - Relationship Management                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │     Database     │
                    │  SQLite/MySQL/   │
                    │   PostgreSQL     │
                    └──────────────────┘
```

## Database Entity Relationship

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Student    │       │   Teacher    │       │    Admin     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │       │ id           │       │ id           │
│ student_id   │       │ teacher_id   │       │ admin_id     │
│ name         │       │ name         │       │ name         │
│ email        │       │ email        │       │ email        │
│ grade_level  │       │ department   │       │ role         │
│ role         │       │ role         │       │ password     │
│ password     │       │ password     │       └──────────────┘
└──────┬───────┘       └──────┬───────┘              │
       │                      │                       │
       │ enrollments          │ courses               │ contents
       │                      │                       │
       ▼                      ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Enrollment   │──────▶│   Course     │◀──────│   Content    │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │       │ id           │       │ id           │
│ student_id   │       │ course_code  │       │ title        │
│ course_id    │       │ name         │       │ slug         │
│ grade        │       │ description  │       │ content_type │
│ enrolled_date│       │ credits      │       │ body         │
└──────────────┘       │ teacher_id   │       │ status       │
                       └──────┬───────┘       │ department_id│
                              │               │ course_id    │
                              │ contents      │ parent_id    │
                              │ documents     └──────┬───────┘
                              │ events               │
                              │                      │ tags (M2M)
                              ▼                      │
                       ┌──────────────┐              ▼
                       │  Document    │       ┌──────────────┐
                       ├──────────────┤       │ ContentTag   │
                       │ id           │       ├──────────────┤
                       │ title        │       │ id           │
                       │ filename     │       │ name         │
                       │ file_path    │       └──────────────┘
                       │ content_id   │
                       │ course_id    │
                       └──────────────┘
                              
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Department   │       │CalendarEvent │       │  Attendance  │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │       │ id           │       │ id           │
│ name         │       │ title        │       │ student_id   │
│ description  │       │ event_type   │       │ course_id    │
└──────────────┘       │ start_date   │       │ date         │
                       │ end_date     │       │ status       │
                       │ department_id│       └──────────────┘
                       │ course_id    │
                       └──────────────┘       ┌──────────────┐
                                             │AssignmentScore│
                                             ├──────────────┤
                                             │ id           │
                                             │ student_id   │
                                             │ content_id   │
                                             │ score        │
                                             │ feedback     │
                                             └──────────────┘
```

## User Role Hierarchy & Permissions

```
┌─────────────────────────────────────────────────────────┐
│                      ADMIN/STAFF                        │
├─────────────────────────────────────────────────────────┤
│ ✓ Full CMS access                                       │
│ ✓ Manage all content                                    │
│ ✓ Manage departments & tags                             │
│ ✓ Manage users                                          │
│ ✓ Create/Edit/Delete any content                        │
│ ✓ Publish/Unpublish any content                         │
│ ✓ View all content (including drafts)                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                       TEACHER                           │
├─────────────────────────────────────────────────────────┤
│ ✓ Manage course-related content                         │
│ ✓ Create/Edit/Delete own content                        │
│ ✓ Publish/Unpublish own content                         │
│ ✓ Upload documents                                      │
│ ✓ Create calendar events                                │
│ ✓ View all published content                            │
│ ✓ Track attendance & grades                             │
│ ✗ Cannot manage other teachers' content                 │
│ ✗ Cannot manage departments/tags                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                       STUDENT                           │
├─────────────────────────────────────────────────────────┤
│ ✓ View published content (read-only)                    │
│ ✓ View own academic records                             │
│ ✓ View calendar events                                  │
│ ✓ View course materials                                 │
│ ✓ Search published content                              │
│ ✗ Cannot create/edit/delete content                     │
│ ✗ Cannot view drafts                                    │
│ ✗ Cannot access admin features                          │
└─────────────────────────────────────────────────────────┘
```

## Content Publishing Workflow

```
┌───────────┐     Publish      ┌────────────┐
│   DRAFT   │─────────────────▶│ PUBLISHED  │
└─────┬─────┘                  └─────┬──────┘
      │                              │
      │ Edit/Update                  │ Unpublish
      │                              │
      │                              ▼
      │                        ┌─────────────┐
      └────────────────────────│ UNPUBLISHED │
                               └─────────────┘

Status Flow:
1. DRAFT - Work in progress (visible to author & admins)
2. PUBLISHED - Live content (visible to all users)
3. UNPUBLISHED - Hidden content (visible to author & admins)
```

## API Request Flow

```
┌─────────────┐
│   Client    │
│ (Browser/   │
│   Mobile)   │
└──────┬──────┘
       │
       │ HTTP Request + JWT Token
       ▼
┌──────────────────────────────┐
│   FastAPI Middleware         │
│   - CORS                     │
│   - Request Logging          │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Authentication Check       │
│   - Decode JWT               │
│   - Verify Signature         │
│   - Check Expiration         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Authorization Check        │
│   - Verify User Role         │
│   - Check Permissions        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Route Handler              │
│   - Validate Input (Pydantic)│
│   - Execute Business Logic   │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Database Operations        │
│   - SQLAlchemy ORM           │
│   - CRUD Operations          │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Response Formation         │
│   - Serialize with Pydantic  │
│   - Return JSON              │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   Client Receives Response   │
└──────────────────────────────┘
```

## Search Architecture

```
Client Query
     │
     ▼
┌─────────────────────────────────┐
│  Search Request                 │
│  - Text query                   │
│  - Filters (type, dept, tags)   │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  Role-Based Filtering           │
│  - Student: published only      │
│  - Teacher/Admin: all content   │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  SQL Query Construction         │
│  - Full-text search (LIKE)      │
│  - JOIN with tags               │
│  - Filter by department         │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  Results Ranking                │
│  - Order by relevance           │
│  - Limit results (100 max)      │
└─────────┬───────────────────────┘
          │
          ▼
     Search Results
```

## File Structure

```
kvhs-api/
├── app/
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Settings & configuration
│   │   ├── security.py          # JWT & password hashing
│   │   └── dependencies.py      # Auth dependencies
│   │
│   ├── routes/                  # API endpoints
│   │   ├── auth.py              # Authentication
│   │   ├── content.py           # Content management
│   │   ├── documents.py         # Document management
│   │   ├── calendar.py          # Calendar events
│   │   ├── cms_utils.py         # Departments & tags
│   │   ├── search.py            # Search functionality
│   │   ├── students.py          # Student CRUD
│   │   ├── teachers.py          # Teacher CRUD
│   │   ├── courses.py           # Course CRUD
│   │   └── enrollments.py       # Enrollment CRUD
│   │
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── database.py              # Database config
│   └── main.py                  # FastAPI app
│
├── .env.example                 # Environment template
├── pyproject.toml               # Dependencies
├── CMS_README.md                # Documentation
├── IMPLEMENTATION_SUMMARY.md    # Summary
├── API_ARCHITECTURE.md          # This file
└── test_cms.py                  # Test script
```

## Key Design Decisions

1. **JWT Authentication**: Stateless, scalable authentication
2. **Role-Based Access**: Fine-grained permission control
3. **SQLAlchemy 2.0+**: Modern ORM with type hints
4. **Pydantic Schemas**: Request/response validation
5. **FastAPI**: High performance, automatic API docs
6. **Hierarchical Content**: Flexible content organization
7. **Simple Publishing**: Draft → Published → Unpublished
8. **Full-Text Search**: LIKE-based search (upgradeable to FTS)
9. **Relationship Tracking**: Author, department, course associations
10. **Extensible Design**: Easy to add new features
