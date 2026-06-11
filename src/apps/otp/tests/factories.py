import factory
from factory.django import DjangoModelFactory

from apps.otp.choices import OTPCodeStatus
from apps.otp.models import OTPCode


class OTPCodeFactory(DjangoModelFactory[OTPCode]):
    class Meta:
        model = OTPCode

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    code = 1111
    otp_token = factory.Sequence(lambda n: f"otp-token-{n}")
    status = OTPCodeStatus.SENT
