from dataclasses import dataclass, asdict

@dataclass
class User:
    userID: str = None
    friendlyName: str = None
    sessionID: str = None
    role: str = None
    fingerprint: str = None

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