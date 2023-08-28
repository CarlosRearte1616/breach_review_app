from typing import List, Optional
from pydantic import BaseModel, Field

from entities.personal_info import PersonalInfo


class PersonalInfoList(BaseModel):
    data: Optional[List[PersonalInfo]] = Field(description="List of Personally Identifiable information by Person", )
