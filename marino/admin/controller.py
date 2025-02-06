from marino.models import Location
from marino.db import LocationsDB
from flask import Request
import re
import os

def validate_new_location_data(
        fullName: str,
        slug: str,
        description: str,
        puzzleText: str,
        puzzleAnswer: str,
) -> tuple[None | Location, str]:
    """
    Ensures that all fields are valid and that 
    fields that don't allow duplicates are available
    """
    fullName = fullName.strip()

    # silently clean up slug
    allowed_chars = "a-z0-9-"
    slug = re.sub(f"[^{allowed_chars}]", "", slug)
    duplicates = LocationsDB.lookup(Location(slug=slug))
    if duplicates is not None:
        return None, f"location already using URL-safe name '{slug}'"
    
    if len(slug) == 0:
        return None, "URL-safe name must have at least one valid character"

    description = description.strip()

    puzzleText = puzzleText.strip()    

    # throw a fit if puzzleAnswer isn't valid
    puzzleAnswer = puzzleAnswer.strip()
    allowed_chars = "a-z0-9"
    if not puzzleAnswer == re.sub(f"[^{allowed_chars}]", "", puzzleAnswer):
        return None, f"puzzle answer contains invalid characters"
    
    if len(puzzleAnswer) == 0:
        return None, "puzzle answer must have at least one character"

    return Location(
        fullName=fullName,
        slug=slug,
        description=description,
        puzzleText=puzzleText,
        puzzleAnswer=puzzleAnswer,
    ), ""

def extract_image_from_request(request: Request, allowed_extensions):
    if 'file' not in request.files:
        return None
    
    file = request.files['file']

    _,file_extension = os.path.splitext(file.filename)
    
    print(f"file_extension is {file_extension}")
    if file_extension not in allowed_extensions:
        return None
    
    return file