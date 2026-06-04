from pydantic import BaseModel, EmailStr
from typing import List, Optional
from core.common.enums.notification_enums import ActionEnum, SeverityEnum


class Recipients(BaseModel):
    to:  List[EmailStr] = []
    cc:  List[EmailStr] = []
    bcc: List[EmailStr] = []


class NotificationConfigCreate(BaseModel):
    id:              Optional[str] = None
    subject:         str
    objectType:      str
    action:          ActionEnum        # validado automaticamente pelo Pydantic
    severity:        SeverityEnum      # validado automaticamente pelo Pydantic
    messageTemplate: str
    recipients:      Recipients


class NotificationConfigRead(BaseModel):
    id:              str
    subject:         str
    objectType:      str
    action:          ActionEnum
    severity:        SeverityEnum
    messageTemplate: str
    recipients:      Recipients

    class Config:
        from_attributes = True
        use_enum_values = True        # serializa como string no JSON de resposta
