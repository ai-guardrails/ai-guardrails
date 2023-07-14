from flask import jsonify
from database.models import DocumentEntity
from database.postgres import session
from service.ingestion_service import IngestionService
from database.repository import Persistence
from sqlalchemy import func ,or_,and_
import logging
class DocumentService:
    def create_document(title, description, location, folder_id):
        return Persistence.insert_document(title, description, location, folder_id)
    
    def create_documents(files,location):
        ingestion_service = IngestionService()
        ingestion_service.ingest_files(location)
        return Persistence.insert_documents(files,location)

    def get_documents(Entity,sort, range_, filter_):
        return Persistence.get_list_query(Entity, sort, range_, filter_)
        
    def get_document(Entity,document_id):
        return Persistence.get_one_query(Entity, document_id)
    
    def update_document(document_id, title, description, location, folder_id):
        return Persistence.update_document(document_id, title, description, location, folder_id)
    
    def delete_document(document_id):
        return Persistence.delete_document(document_id)
        