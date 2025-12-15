from pydantic import BaseModel


class BaseSettings(BaseModel):
    class Config:
        extra = "ignore"


def SettingsConfigDict(**kwargs):
    return kwargs
