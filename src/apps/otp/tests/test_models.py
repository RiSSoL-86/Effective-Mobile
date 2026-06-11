import pytest

from apps.otp.tests.factories import OTPCodeFactory


@pytest.mark.django_db
class TestOTPCode:
    def test_str_returns_id(self):
        otp = OTPCodeFactory.create()

        assert str(otp) == str(otp.id)

    def test_timestamps_are_populated(self):
        otp = OTPCodeFactory.create()

        assert otp.created_timestamp is not None
        assert otp.updated_timestamp is not None
