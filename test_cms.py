#!/usr/bin/env python3
"""
Quick test script to verify the CMS API is working correctly.
This script tests authentication and basic CMS functionality.
"""

import requests
import json
from datetime import date, datetime

BASE_URL = "http://localhost:8000"


def print_response(name, response):
    """Print formatted response."""
    print(f"\n{'=' * 60}")
    print(f"{name}")
    print(f"{'=' * 60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def main():
    print("KVHS CMS API Test Suite")
    print("=" * 60)

    # 1. Health Check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Health Check", response)

    # 2. Register Admin
    print("\n2. Registering Admin...")
    admin_data = {
        "admin_id": "ADM001",
        "name": "Test Admin",
        "email": "admin@test.com",
        "password": "admin123456",
    }
    response = requests.post(f"{BASE_URL}/auth/register/admin", json=admin_data)
    print_response("Register Admin", response)

    # 3. Register Teacher
    print("\n3. Registering Teacher...")
    teacher_data = {
        "teacher_id": "TCH001",
        "name": "Test Teacher",
        "email": "teacher@test.com",
        "department": "Mathematics",
        "hired_date": "2024-01-01",
        "password": "teacher123456",
    }
    response = requests.post(f"{BASE_URL}/auth/register/teacher", json=teacher_data)
    print_response("Register Teacher", response)

    # 4. Register Student
    print("\n4. Registering Student...")
    student_data = {
        "student_id": "STU001",
        "name": "Test Student",
        "email": "student@test.com",
        "grade_level": 10,
        "enrolled_date": "2024-01-15",
        "password": "student123456",
    }
    response = requests.post(f"{BASE_URL}/auth/register/student", json=student_data)
    print_response("Register Student", response)

    # 5. Login as Admin
    print("\n5. Logging in as Admin...")
    login_data = {"email": "admin@test.com", "password": "admin123456"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Admin Login", response)

    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 6. Create Department
        print("\n6. Creating Department...")
        dept_data = {
            "name": "Science Department",
            "description": "Science and Mathematics",
        }
        response = requests.post(
            f"{BASE_URL}/cms/departments", json=dept_data, headers=headers
        )
        print_response("Create Department", response)
        dept_id = response.json().get("id") if response.status_code == 201 else None

        # 7. Create Tag
        print("\n7. Creating Content Tag...")
        tag_data = {"name": "Important"}
        response = requests.post(f"{BASE_URL}/cms/tags", json=tag_data, headers=headers)
        print_response("Create Tag", response)
        tag_id = response.json().get("id") if response.status_code == 201 else None

        # 8. Create Content
        print("\n8. Creating Content...")
        content_data = {
            "title": "Welcome to School",
            "slug": "welcome-to-school",
            "content_type": "announcement",
            "body": "Welcome to the new academic year!",
            "status": "published",
            "department_id": dept_id,
            "tag_ids": [tag_id] if tag_id else [],
        }
        response = requests.post(
            f"{BASE_URL}/content/", json=content_data, headers=headers
        )
        print_response("Create Content", response)
        content_id = response.json().get("id") if response.status_code == 201 else None

        # 9. List Content
        print("\n9. Listing Content...")
        response = requests.get(f"{BASE_URL}/content/", headers=headers)
        print_response("List Content", response)

        # 10. Search Content
        print("\n10. Searching Content...")
        response = requests.get(f"{BASE_URL}/search/?q=welcome", headers=headers)
        print_response("Search Content", response)

        # 11. Create Calendar Event
        print("\n11. Creating Calendar Event...")
        event_data = {
            "title": "First Day of School",
            "description": "Welcome back everyone!",
            "event_type": "school_event",
            "start_date": "2024-09-01T08:00:00",
            "end_date": "2024-09-01T15:00:00",
            "all_day": False,
            "department_id": dept_id,
        }
        response = requests.post(
            f"{BASE_URL}/calendar/events", json=event_data, headers=headers
        )
        print_response("Create Calendar Event", response)

        # 12. List Calendar Events
        print("\n12. Listing Calendar Events...")
        response = requests.get(f"{BASE_URL}/calendar/events", headers=headers)
        print_response("List Calendar Events", response)

    # 13. Login as Student and try to view content
    print("\n13. Logging in as Student...")
    login_data = {"email": "student@test.com", "password": "student123456"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Student Login", response)

    if response.status_code == 200:
        student_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {student_token}"}

        # 14. Student views published content
        print("\n14. Student viewing content (should only see published)...")
        response = requests.get(f"{BASE_URL}/content/", headers=headers)
        print_response("Student View Content", response)

        # 15. Student tries to create content (should fail)
        print("\n15. Student trying to create content (should fail)...")
        content_data = {
            "title": "Student Post",
            "slug": "student-post",
            "content_type": "page",
            "body": "This should fail",
            "status": "draft",
        }
        response = requests.post(
            f"{BASE_URL}/content/", json=content_data, headers=headers
        )
        print_response("Student Create Content (Expected 403)", response)

    print("\n" + "=" * 60)
    print("Test Suite Completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: uv run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nError: {e}")
