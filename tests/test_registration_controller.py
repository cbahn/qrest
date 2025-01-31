import pytest
from marino.registration.controller import validate_username


@pytest.mark.parametrize(
    "input_username, expected_result",
    [
        ("NumbersOK123", (True, "Numbers")),   # ✅ Valid username
        ("_ValidName_", (True, "_ValidName_")),     # ✅ Underscores allowed
        ("ab", (False, "Username too short")),      # ❌ Too short
        ("thisisaverylongusername", (False, "Username too long")),  # ❌ Too long
        ("invalid@user", (False, "Invalid characters")),  # ❌ Special characters not allowed
        ("", (False, "Username too short")),        # ❌ Empty string
        ("user name", (False, "Invalid characters")),  # ❌ Spaces not allowed
    ],
)
def test_validate_username(input_username, expected_result):
    (result, _) = validate_username(input_username)
    assert result == expected_result[0]