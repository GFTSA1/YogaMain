import pytest

from app.utils.auth.google import GoogleVerifier, GoogleIdentity


class _StubVerifier(GoogleVerifier):
    def __init__(self, claims):
        self._claims = claims

    def _verify_raw(self, id_token: str):
        return self._claims


def test_verifier_returns_identity_on_verified_email():
    v = _StubVerifier(
        {
            "sub": "google-sub-123",
            "email": "u@example.com",
            "email_verified": True,
            "given_name": "Test",
            "family_name": "User",
        }
    )
    identity = v.verify("fake-id-token")
    assert identity == GoogleIdentity(
        sub="google-sub-123",
        email="u@example.com",
        first_name="Test",
        last_name="User",
    )


def test_verifier_rejects_unverified_email():
    v = _StubVerifier(
        {
            "sub": "google-sub-123",
            "email": "u@example.com",
            "email_verified": False,
            "given_name": "Test",
            "family_name": "User",
        }
    )
    with pytest.raises(ValueError):
        v.verify("fake-id-token")


def test_verifier_handles_missing_family_name():
    v = _StubVerifier(
        {
            "sub": "google-sub-123",
            "email": "u@example.com",
            "email_verified": True,
            "given_name": "Mononym",
        }
    )
    identity = v.verify("fake-id-token")
    assert identity.last_name is None


def test_verifier_rejects_when_raw_verify_raises():
    class _Broken(_StubVerifier):
        def _verify_raw(self, id_token: str):
            raise ValueError("bad signature")

    v = _Broken({})
    with pytest.raises(ValueError):
        v.verify("fake-id-token")
