from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestCustomAccountManager:

    def test_create_user_success(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            firstname='John',
            lastname='Doe',
            password='password123',
            
        )

        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.firstname == 'John'
        assert user.lastname == 'Doe'
        assert user.check_password('password123')
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match='You must provide an email address'):
            User.objects.create_user(
                email='',
                username='testuser',
                firstname='John',
                lastname='Doe',
                password='password123',
            )

    def test_create_superuser_success(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            firstname='Admin',
            lastname='User',
            password='adminpass',
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                username='adminuser',
                firstname='Admin',
                lastname='User',
                password='adminpass',
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                username='adminuser',
                firstname='Admin',
                lastname='User',
                password='adminpass',
                is_superuser=False,
            )


@pytest.mark.django_db
class TestCustomUserModel:

    def test_str_returns_username(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )
        assert str(user) == 'testuser'

    def test_get_absolute_url(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )

        assert user.get_absolute_url() == reverse(
            "django_openuser:profile_details",
            kwargs={"username": user.username},
        )

    def test_is_online_true(self):
        user = User.objects.create_user(
            email='online@example.com',
            username='onlineuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )
        user.last_online = timezone.now() - timedelta(minutes=3)
        assert user.is_online is True

    def test_is_online_false(self):
        user = User.objects.create_user(
            email='offline@example.com',
            username='offlineuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )
        user.last_online = timezone.now() - timedelta(minutes=10)
        assert user.is_online is False

    def test_is_online_none(self):
        user = User.objects.create_user(
            email='none@example.com',
            username='noneuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )
        user.last_online = None
        assert user.is_online is False

    def test_member_id_format(self):
        user = User.objects.create_user(
            email='member@example.com',
            username='memberuser',
            firstname='John',
            lastname='Doe',
            password='password123',
        )

        mid = user.member_id
        assert mid.startswith("JD")
        assert len(mid) == 7

    def test_save_generates_member_id(self):
        user = User.objects.create_user(
            email='save@example.com',
            username='saveuser',
            firstname='Alice',
            lastname='Wonder',
            password='password123',
        )

        assert user.member_id is not None

    def test_save_does_not_override_member_id(self):
        user = User.objects.create_user(
            email='keep@example.com',
            username='keepuser',
            firstname='A',
            lastname='B',
            password='password123',
        )

        original = user.member_id
        user.firstname = "Changed"
        user.lastname = "Name"
        user.save()

        assert user.member_id == original

    def test_username_invalid(self):
        user = User(
            email="bad@test.com",
            username="bad-user!",
            firstname="A",
            lastname="B",
        )
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_username_too_short(self):
        user = User(
            email="short@test.com",
            username="abc",
            firstname="A",
            lastname="B",
            password="securepassword",
            city="A city",
        )
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_username_valid(self):
        user = User(
            email="ok@test.com",
            username="validuser123",
            firstname="A",
            lastname="B",
            password="securepassword",
            city="A city",
        )
        user.full_clean()

    def test_optional_fields(self):
        user = User.objects.create_user(
            email="opt@test.com",
            username="optuser",
            firstname="A",
            lastname="B",
            password="securepassword",
            city="A city",
            
        )

        assert user.address is ''
        assert user.phonenumber is ''


    def test_create_superuser_forces_flags(self):
        user = User.objects.create_superuser(
            email="admin@test.com",
            username="adminuser",
            firstname="Admin",
            lastname="User",
            password="pass123",
            
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_rejects_invalid_flags(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin@test.com",
                username="adminuser",
                firstname="Admin",
                lastname="User",
                password="pass123",
                is_staff=False,
            )



    def test_member_id_collision_retry(self):
        existing = User.objects.create_user(
            email="existing@test.com",
            username="existing",
            firstname="Jane",
            lastname="Smith",
            password="pass123",
        )

        existing.member_id = "JS" + str(timezone.now().year)[-2:] + "123"
        existing.save()

        with patch("random.randint", side_effect=[123, 456]):
            user = User.objects.create_user(
                email="new@test.com",
                username="newuser",
                firstname="Jane",
                lastname="Smith",
                password="pass123",
            )

            assert user.member_id != existing.member_id


    def test_member_id_fail_after_100_attempts(self):

        with patch("random.randint", return_value=111):

            existing = User.objects.create_user(
                email="existing@test.com",
                username="existing",
                firstname="J",
                lastname="S",
                password="pass123",
                
            )

            existing.member_id = "JS" + str(timezone.now().year)[-2:] + "111"
            existing.save()

            user = User(
                email="fail@test.com",
                username="failuser",
                firstname="J",
                lastname="S",
            )

            with pytest.raises(ValueError):
                user.generate_member_id()