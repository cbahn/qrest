from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class User:
    userID: str = None
    password: str = None
    friendlyName: str = None
    sessionID: str = None
    role: str = None
    fingerprint: str = None
    admin: None | bool = None
    ephemeralID: None | str = None
    coins: None | int = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Location:
    locationID: str = None
    fullName: str = None
    slug: str = None
    imageFile: str = None
    description: str = None
    puzzleText: str = None
    puzzleAnswer: str = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
    
@dataclass
class Comment:
    friendlyName: str
    timestamp: datetime
    chicago_time: str
    comment: str