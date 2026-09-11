from pydantic import BaseModel


class UpdateProfileRequest(BaseModel):
    full_name: str
    bio: str | None = None