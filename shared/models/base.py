from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base
import uuid
class BaseModel(Base):
    __abstract__ =  True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
