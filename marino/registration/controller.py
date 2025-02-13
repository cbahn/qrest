from marino.db import UsersDB
from marino.util import Util
from marino.models import User
from pymongo.errors import DuplicateKeyError
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

def create_user_d(friendlyName: str, password: str, fingerprint: str) -> tuple[None | User, str]:
    """
    On success, return (User,"")
    On failure, return (None, "Error cause")
    """
    (valid_name, err) = validate_username(friendlyName)
    if valid_name is None:
        return err
    
    def try_to_generate_a_unique_userID(n):
        for _ in range(n):
            new_userID = Util.generate_new_userID()
            if UsersDB.lookup(User(userID=new_userID)) is None:
                return new_userID
        raise RuntimeError(f"Failed to generate a new userID after {n} attmpts!")

    try:
        newUser = User(
            friendlyName = friendlyName,
            password = password,
            fingerprint=fingerprint,            
            userID = try_to_generate_a_unique_userID(20),
        )
        UsersDB.create(newUser)
    except DuplicateKeyError as e:
        return str(e)

    # No exception from UsersDB.create() indicates success

    return UsersDB.lookup(User(friendlyName=friendlyName)), ""