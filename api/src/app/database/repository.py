import json
from sqlalchemy import create_engine, text, func ,or_,and_
from sqlalchemy.orm import sessionmaker
from database.models import Base, AnalysisAuditEntity, AnonymizeAuditEntity, ChatLogEntity,DocumentEntity, OrganisationEntity,CustomRuleEntity,PredefinedRuleEntity
from globals import Globals
from utils.apiResponse import ApiResponse
from flask import jsonify
from service.ingestion_service import IngestionService
import logging


from database.postgres import session , engine

class Persistence:
    
    def insert_analysis_audits(text, user_email, flagged_text, analysed_entity, criticality):
        try:
            audit = AnalysisAuditEntity(text=text, user_email=user_email, flagged_text=flagged_text, analysed_entity=analysed_entity, criticality=criticality)
            session.add(audit)
            session.commit()
        except Exception as ex:
            logging.error(f"Exception while inserting analysis audit: {ex}")
            session.rollback()
        finally:
            session.close()

    def insert_anonymize_audits(original_text, anonymized_text, flagged_text, user_email, analysed_entity, criticality):
        try:
            audit = AnonymizeAuditEntity(original_text=original_text, anonymized_text=anonymized_text, flagged_text=flagged_text, user_email=user_email, analysed_entity=analysed_entity, criticality=criticality)
            session.add(audit)
            session.commit()
        except Exception as ex:
            logging.error(f"Exception while inserting anonymize audit: {ex}")
            session.rollback()
        finally:
            session.close()

    def insert_chat_log(user_email, text):
        try:
            log = ChatLogEntity(user_email=user_email, text=text)
            session.add(log)
            session.commit()
        except Exception as ex:
            logging.error(f"Exception while inserting chat log: {ex}")
            session.rollback()
        finally:
            session.close()
            
    def insert_document(title, description, location, folder_id):
        try:
            document = DocumentEntity(
                    title=title,
                    description=description,
                    location=location,
                    folder_id=folder_id
                )
            session.add(document)
            session.commit()
            return jsonify({"message": "success", "document": document.to_dict()}), 200
        except Exception as e:
            logging.error(f"Exception while inserting document: {ex}")
            session.rollback()
            return jsonify({"message": "error"}), 500
        finally:
            session.close()
    
    def insert_documents(files,location):
        try:
            for file in files:
                doc = DocumentEntity(
                    title=file.filename,
                    description="",
                    location= location + "/" + file.filename,
                    folder_id=1)
                session.add(doc)
                session.commit()
            return jsonify({"message": "success"}), 200
        except Exception as e: 
            session.rollback() 
            logging.error(e)
            return jsonify({"message": "error"}), 500
        finally:
            session.close()
        

    
    def get_chat_log():
        try:
            logs = session.query(ChatLogEntity).all()
            result = []
            for log in logs:
                result.append({
                    'id': str(log.id),
                    'created_at': log.created_at.isoformat(),
                    'user_email': log.user_email,
                    'text': log.text
                })
            return json.dumps(result)
        except Exception as ex:
            logging.error(f"Exception while getting chat logs: {ex}")
        finally:
            session.close()

    def get_org(name):
        try:
            org = session.query(OrganisationEntity).filter(OrganisationEntity.name == name).first()
            if org:
                return {
                    'id': str(org.id),
                    'name': org.name,
                    'email': org.email,
                    'details': org.details,
                    'openai_key': org.openai_key,
                    'created_at': org.created_at.isoformat()
                }
            else:
                return None
        except Exception as ex:
            logging.error(f"Exception while getting organisation: {ex}")
        finally:
            session.close()

    def save_org(data):
        try:
            org = OrganisationEntity(name=data['name'], email=data['email'], details=data['details'], openai_key=data['openai_key'])
            session.add(org)
            session.commit()
        except Exception as ex:
            logging.error(f"Exception while inserting organisation: {ex}")
            session.rollback()
        finally:
            session.close()

    def get_list_query(Entity, sort, range_, filter_):
        try:
            query = session.query(Entity)
            
            # Apply filter conditions
            filter_dict = eval(filter_)
            if len(filter_dict) != 0:
                filter_field = filter_dict['filterField']
                filter_operator = filter_dict['filterOperator']
                filter_value = filter_dict['filterValue']
                
                if filter_operator == 'contains':
                    query = query.filter(func.lower(getattr(Entity, filter_field)).like(func.lower(f"%{filter_value}%")))
                elif filter_operator == 'equals':
                    query = query.filter(func.lower(getattr(Entity, filter_field)) == func.lower(filter_value))
                elif filter_operator == 'startsWith':
                    query = query.filter(func.lower(getattr(Entity, filter_field)).like(func.lower(f"{filter_value}%")))
                elif filter_operator == 'endsWith':
                    query = query.filter(func.lower(getattr(Entity, filter_field)).like(func.lower(f"%{filter_value}")))
                elif filter_operator == 'isEmpty':
                    query = query.filter(or_(getattr(Entity, filter_field) == None,
                         getattr(Entity, filter_field) == ''))
                elif filter_operator == 'isNotEmpty':
                    query = query.filter(and_(getattr(Entity, filter_field) != None,
                         getattr(Entity, filter_field) != ''))
                elif filter_operator == 'isAnyOf':
                    if len(filter_value) > 0:
                        query = query.filter(func.lower(getattr(Entity, filter_field)).in_(filter_value))
                    
            #total rows count
            total_rows = query.count()

            # Apply sort conditions
            if sort:
                sort_list = eval(sort)
                sort_field_name = sort_list[0]
                sort_value=sort_list[1]
                column = getattr(Entity, sort_field_name)
                if sort_value == 'asc':
                    query = query.order_by(column.asc())
                elif sort_value == 'desc':
                    query = query.order_by(column.desc())

            # Apply range conditions
            if range_:
                range_list = eval(range_)
                start = range_list[0]
                end = range_list[1]
                query = query.slice(start, end + 1)

            # Execute the query and retrieve documents
            documents = query.all()
            serialized_documents = [doc.to_dict() for doc in documents]
          
            data = {
                "rows": serialized_documents,
                "totalRows": total_rows
            }
            
            return jsonify({"data":data,"success":True,"message":"Successfully retrieved data"})
        except Exception as e:
            logging.error(f"Exception while getting list: {ex}")
            return jsonify({"data":{},"success":False,"message": "Error in retrieving data"}), 500
        finally:
            session.close()
    
    def get_one_query(Entity, id):     
        try:
            document = session.query(Entity).filter(Entity.id == id).first()
            
            if not document:
                return jsonify({"data":{},"success":False,"message": "Cannot find the data"}), 500

            return jsonify({"data":document.to_dict(),"success":True,"message":"Successfully retrieved data"})
            
        except Exception as ex:
            logging.error(f"Exception while getting one item: {ex}")
            return jsonify({"data":{},"success":False,"message": "Error in retrieving data"}), 500
        finally:
            session.close()

     #Get rules name from provider
    def get_all_enabled_entities(Entity, provider_name):
        enabled_entities = []
        
        try:
            enabled_entities = session.query(Entity).filter(and_(Entity.provider == provider_name,Entity.is_active==True)).first()
            if not enabled_entities:
                enabled_entities = []
            return enabled_entities
        except Exception as ex:
            logging.error(f"Exception while getting enabled entities: {ex}")
            return []
        finally:
            session.close()


    def update_document(document_id, title, description, location, folder_id):
        try:
            document = session.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()
            if not document:
                return jsonify({"message": "not found"}), 404
            if title:
                document.title = title
            if description:
                document.description = description
            if location:
                document.location = location
            if folder_id:
                document.folder_id = folder_id
            session.commit()
            return jsonify({"message": "success", "document": document.to_dict()}), 200
        except Exception as e:
            session.rollback()
            return jsonify({"message": "error"}), 500
        finally:
            session.close()
    
    def delete_document(document_id):
        try:
            document = session.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()
            session.delete(document)
            session.commit()
            return jsonify({"message": "success"}), 200
        except Exception as e:
            session.rollback()
            return jsonify({"message": "error"}), 500
        finally:
            session.close()