from sqlalchemy import Column, String, JSON, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from core.common.enums.notification_enums import ActionEnum, SeverityEnum
from datetime import datetime
from core.models.models import GenericModel
from core.utils.id_generator import generate_custom_id

Base = declarative_base()


class NotificationConfig(GenericModel):
    __tablename__ = "notification_configs"

    id = Column(String, primary_key=True, default=generate_custom_id)
    subject = Column(String, nullable=False)
    objectType = Column(String, nullable=False)
    action = Column(Enum(ActionEnum), nullable=False)
    severity = Column(Enum(SeverityEnum), nullable=False)
    messageTemplate = Column(String, nullable=False)
    recipients = Column(JSON, nullable=False)
    
