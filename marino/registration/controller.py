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
            pattern = r'^[a-zA-Z_]+$'
        )]

    try:
        new_username = NewUsername(username = raw_input)
        return True, new_username.username
    except ValidationError as e:
        return False, repr(e)


def create_user_d(raw_name: str) -> None | str:

    (valid_name, err) = validate_username(raw_name)

    if valid_name is None:
        return err
    try:
        newUser = User(
            friendlyName = valid_name,
            userId = Util.generate_new_userID(),
        )
        UsersDB.create(newUser)
    except DuplicateDataError as e:
        return str(e)

    # If UsersDB.create() doesn't throw an exception then
    # the new user was created
    return None