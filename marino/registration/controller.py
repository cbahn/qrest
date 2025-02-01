from marino.db import UsersDB, DuplicateDataError
from marino.util import Util
from marino.models import User
from pydantic import BaseModel, StringConstraints, ValidationError
from typing_extensions import Annotated

def validate_username(raw_input) -> tuple[None | str,str]:

    class NewUsername(BaseModel):
        username: Annotated[str, StringConstraints(
            strip_whitespace=True,
            min_length = 3,
            max_length = 20,
            pattern = r'^[a-zA-Z0-9_]+$'
        )]

    try:
        new_username = NewUsername(username = raw_input)
        return True, new_username.username
    except ValidationError as e:
        return False, repr(e)

def create_user_d(new_name: str, fingerprint: str) -> tuple[None | User, str]:
    """
    On success, return (User,"")
    On failure, return (None, "Error cause")
    """
    (valid_name, err) = validate_username(new_name)
    if valid_name is None:
        return err
    
    def try_to_generate_a_unique_userId(n):
        for _ in range(n):
            new_userId = Util.generate_new_userID()
            if UsersDB.lookup(User(userId=new_userId)) is None:
                return new_userId
        raise RuntimeError(f"Failed to generate a new userId after {n} attmpts!")

    try:
        newUser = User(
            friendlyName = new_name,
            userId = try_to_generate_a_unique_userId(20),
            fingerprint=fingerprint,
        )
        UsersDB.create(newUser)
    except DuplicateDataError as e:
        return str(e)

    # No exception from UsersDB.create() indicates success

    return UsersDB.lookup(User(friendlyName=new_name)), ""