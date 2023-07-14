from sqlalchemy import Column, Integer, String, Text,MetaData,Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from globals import Globals

metadata_obj = MetaData(schema=Globals.pg_schema)
Base = declarative_base(metadata=metadata_obj)

class PredefinedRuleEntity(Base):
    __tablename__ = 'predefined_rules'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255))
    provider = Column(String(255))
    is_active = Column(Boolean)
    details = Column(String(255))
    criticality = Column(String(255))
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'provider': self.provider,
            'is_active': self.is_active,
            'details': self.details,
            'criticality': self.criticality
        }


class ChatLogEntity(Base):
    __tablename__ = 'chat_log'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_email = Column(Text)
    text = Column(Text)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'created_at': self.created_at,
            'user_email': self.user_email,
            'text': self.text
        }


class AnonymizeAuditEntity(Base):
    __tablename__ = 'anonymize_audit'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    original_text = Column(Text)
    anonymized_text = Column(Text)
    flagged_text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_email = Column(Text)
    analysed_entity = Column(Text)
    criticality = Column(Text)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'original_text': self.original_text,
            'anonymized_text': self.anonymized_text,
            'flagged_text': self.flagged_text,
            'created_at': self.created_at,
            'user_email': self.user_email,
            'analysed_entity': self.analysed_entity,
            'criticality': self.criticality
        }


class AnalysisAuditEntity(Base):
    __tablename__ = 'analysis_audit'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_email = Column(Text)
    flagged_text = Column(Text)
    analysed_entity = Column(Text)
    criticality = Column(Text)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'text': self.text,
            'created_at': self.created_at,
            'user_email': self.user_email,
            'flagged_text': self.flagged_text,
            'analysed_entity': self.analysed_entity,
            'criticality': self.criticality
        }


class CustomRuleEntity(Base):
    __tablename__ = 'custom_rules'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255))
    type = Column(String(255))
    value = Column(String(255))
    created_at = Column(TIMESTAMP)
    criticality = Column(String(255))
    is_active = Column(Boolean)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'created_at':self.created_at,
            'criticality':self.criticality,
            'is_active':self.is_active
        }

class OrganisationEntity(Base):
    __tablename__ = 'organisation'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255))
    email = Column(String(255))
    details = Column(Text)
    openai_key = Column(String(255))
    created_at = Column(TIMESTAMP)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'details': self.details,
            'openai_key': self.openai_key,
            'created_at': self.created_at
        }

class DocumentEntity(Base):
    __tablename__ = 'documents'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String())
    folder_id = Column(Integer())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'folder_id': self.folder_id
        }
