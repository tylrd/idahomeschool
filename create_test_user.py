#!/usr/bin/env python
"""Create test users for development."""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from idahomeschool.users.models import User


def create_user(username, email, password, is_superuser=False):
    """Create a user if it doesn't exist."""
    if User.objects.filter(username=username).exists():
        print(f"⚠ User '{username}' already exists!")
        return User.objects.get(username=username)

    if is_superuser:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        print(f"✓ Superuser '{username}' created successfully!")
    else:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        print(f"✓ Regular user '{username}' created successfully!")

    return user


# Create test users
print("Creating test users for development...\n")

# Admin/superuser
admin = create_user(
    username="admin", email="admin@example.com", password="admin123", is_superuser=True
)

# Regular test user
test_user = create_user(
    username="testuser",
    email="test@example.com",
    password="test123",
    is_superuser=False,
)

print("\n" + "=" * 60)
print("Test Accounts Created:")
print("=" * 60)
print("\n1. ADMIN ACCOUNT (Superuser)")
print("   Username: admin")
print("   Password: admin123")
print("   Email:    admin@example.com")
print("   Access:   Full admin access")
print("   URL:      http://localhost:8000/admin/")

print("\n2. TEST USER ACCOUNT (Regular User)")
print("   Username: testuser")
print("   Password: test123")
print("   Email:    test@example.com")
print("   Access:   Regular user access")
print("   URL:      http://localhost:8000/accounts/login/")

print("\n" + "=" * 60)
print("Note: Email verification is disabled in local development")
print("=" * 60)
