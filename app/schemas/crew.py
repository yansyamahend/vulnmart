from pydantic import BaseModel


class CrewRegisterRequest(BaseModel):
    full_name: str
    username: str
    email: str
    password: str


class CrewLoginRequest(BaseModel):
    username: str
    password: str


class CrewOTPRequest(BaseModel):
    username: str
    otp: str | None = None