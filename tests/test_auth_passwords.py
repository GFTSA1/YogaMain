from app.utils.auth.passwords import hash_password, verify_password


def test_hash_password_is_not_plaintext():
    h = hash_password("hunter2!")
    assert h != "hunter2!"
    assert h.startswith("$2") or h.startswith("$bcrypt-sha256$")


def test_verify_password_accepts_correct():
    h = hash_password("hunter2!")
    assert verify_password("hunter2!", h) is True


def test_verify_password_rejects_wrong():
    h = hash_password("hunter2!")
    assert verify_password("Hunter2!", h) is False


def test_verify_password_rejects_when_hash_is_none():
    assert verify_password("anything", None) is False
