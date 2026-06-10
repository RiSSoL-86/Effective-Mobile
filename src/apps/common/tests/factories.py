"""Factories for models without a dedicated app (django-oauth-toolkit).

Per-app model factories live next to their app (e.g. ``UserFactory`` in
``apps.users.tests.factories``); this module only hosts the OAuth2 token
and application factories.
"""

from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.settings import oauth2_settings

from apps.users.tests.factories import UserFactory


class ApplicationFactory(DjangoModelFactory[Application]):
    class Meta:
        model = Application

    name = factory.Sequence(lambda n: f"app-{n}")
    client_type = "confidential"
    authorization_grant_type = "password"
    client_secret = "secret"


class AccessTokenFactory(DjangoModelFactory[AccessToken]):
    class Meta:
        model = AccessToken

    user = factory.SubFactory(UserFactory)
    application = factory.SubFactory(ApplicationFactory)
    token = factory.Sequence(lambda n: f"access-token-{n}")
    scope = " ".join(oauth2_settings.DEFAULT_SCOPES)
    expires = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=1))


class RefreshTokenFactory(DjangoModelFactory[RefreshToken]):
    class Meta:
        model = RefreshToken

    access_token = factory.SubFactory(AccessTokenFactory)
    # Keep the user/application consistent with the access token.
    user = factory.SelfAttribute("access_token.user")
    application = factory.SelfAttribute("access_token.application")
    token = factory.Sequence(lambda n: f"refresh-token-{n}")
