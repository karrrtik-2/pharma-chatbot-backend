import re
from pydantic import BaseModel, Field, field_validator


class DateTimeModel(BaseModel):
    date: str = Field(description="Properly formatted date", pattern=r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$")

    @field_validator("date")
    def check_format_date(cls, value: str) -> str:
        if not re.match(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$", value):
            raise ValueError("The date should be in format 'DD-MM-YYYY HH:MM'")
        return value


class DateModel(BaseModel):
    date: str = Field(description="Properly formatted date", pattern=r"^\d{2}-\d{2}-\d{4}$")

    @field_validator("date")
    def check_format_date(cls, value: str) -> str:
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", value):
            raise ValueError("The date must be in the format 'DD-MM-YYYY'")
        return value


class IdentificationNumberModel(BaseModel):
    id: int = Field(description="Identification number (7 or 8 digits long)")

    @field_validator("id")
    def check_format_id(cls, value: int) -> int:
        if not re.match(r"^\d{7,8}$", str(value)):
            raise ValueError("The ID number should be a 7 or 8-digit number")
        return value
