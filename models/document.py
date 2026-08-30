from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from .base import Base  


class Document(Base):
    __tablename__ = "documents"
    
    # Exemple : id UUID primary key avec génération auto
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # TON TOUR pour les autres champs !
    source_type: Mapped [str] 
    



"""CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author VARCHAR(255),
    published_date TIMESTAMP,
    raw_content JSONB NOT NULL,
    metadata JSONB,
    is_official BOOLEAN DEFAULT FALSE,
    is_canon BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""