import pytest

from apps.users.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_sets_defaults(self):
        # Act
        user = User.objects.create_user(
            email="user@example.com",
            password="pass",
        )

        # Assert
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_active is True

    def test_create_user_hashes_password(self):
        # Act
        user = User.objects.create_user(
            email="user@example.com",
            password="plain-password",
        )

        # Assert
        assert user.password != "plain-password"
        assert user.check_password("plain-password")

    def test_create_user_normalizes_email_domain(self):
        # Act
        user = User.objects.create_user(
            email="User@EXAMPLE.COM",
            password="pass",
        )

        # Assert - normalize_email lowercases the domain part
        assert user.email == "User@example.com"

    def test_create_user_without_email_raises(self):
        # Act & Assert
        with pytest.raises(ValueError, match="email address"):
            User.objects.create_user(email="", password="pass")

    def test_create_superuser_sets_flags(self):
        # Act
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="pass",
        )

        # Assert
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_requires_is_staff(self):
        # Act & Assert
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="pass",
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser(self):
        # Act & Assert
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="pass",
                is_superuser=False,
            )

    def test_get_by_natural_key_is_case_insensitive(self):
        # Arrange
        user = User.objects.create_user(
            email="user@example.com",
            password="pass",
        )

        # Act
        found = User.objects.get_by_natural_key("USER@EXAMPLE.COM")

        # Assert
        assert found.pk == user.pk
