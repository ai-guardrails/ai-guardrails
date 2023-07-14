import logging
from oidc import get_current_user_email
from repo.db import anonymize_audit_context,analysis_audit_context
from database.repository import Persistence
from integration.presidio_wrapper import presidio_wrapper
from integration.nsfw_model_wrapper import NSFWModelWrapper
import uuid
from datetime import datetime
from typing import TypedDict


class analysis_audit_obj(TypedDict):
    _id: str
    message: str
    analysis: list
    created: datetime
    user_email: str

class anonymize_audit_obj(TypedDict):
    _id: str
    original_message: str
    anonymized_message: list
    created: datetime
    user_email: str
    conversation_id: str
    analysis: list



class pii_service:
    def analyze(message):
        presidio_analysis = presidio_wrapper.analyze_message(message)
        
        result = pii_service.format_and_filter_analysis(presidio_analysis, message)
        result.sort(key=lambda x: x["start"], reverse=False)

        nsfw_score = NSFWModelWrapper.analyze(message)
        if nsfw_score > 0.9:
            result.append(
                {
                    "entity_type": "NSFW",
                    "start": 0,
                    "end": len(message),
                    "score": nsfw_score,
                    "flagged_text": message,
                    "block": True,
                }
            )

        if len(result):
            pii_service.save_analysis_audit(message, result,get_current_user_email())
        return result

    
    def anonymize(message,email = None, conversaton_id = None):
        if not email:
            email = get_current_user_email()
        analysis = presidio_wrapper.analyze_message(message)
        anonymized_message = presidio_wrapper.anonymyze_message(message, analysis)
        if message != anonymized_message:
            pii_service.save_anonymize_audit(message, pii_service.format_and_filter_analysis(analysis, message), anonymized_message,email,conversaton_id)
        return anonymized_message


    def format_and_filter_analysis(results,message):
        response = []
        for result in results:
                if result.score > 0.3:
                    response.append(
                        {
                            "entity_type": str(result.entity_type).replace("_", " ").title(),
                            "start": result.start,
                            "end": result.end,
                            "score": result.score,
                            "flagged_text": message[result.start : result.end],
                            "block": False,
                        }
                    )
        return response


    def save_analysis_audit(message,analysis,user_email):
        analysis_audit = analysis_audit_obj(
            _id=str(uuid.uuid4()),
            message=message,
            analysis=analysis,
            created=datetime.now(),
            user_email=user_email,
        )
        analysis_audit_context.insert_analysis_audit(analysis_audit)
        for flag in analysis:   
            Persistence.insert_analysis_audits(text = message, user_email = user_email, flagged_text = flag['flagged_text'],  analysed_entity = flag['entity_type'], criticality = 'SEVERE')
        


    def save_anonymize_audit(message,analysis,anonymized_message,user_email,conversation_id = None):
        anonymize_audit =  anonymize_audit_obj(
            _id=str(uuid.uuid4()),
            original_message=message,
            anonymized_message=anonymized_message,
            analysis=analysis,
            created=datetime.now(),
            user_email=user_email,
            conversation_id= conversation_id
        )    
        anonymize_audit_context.insert_anonymize_audit(anonymize_audit)
        for flag in analysis:   
            Persistence.insert_anonymize_audits(original_text = message, anonymized_text  = anonymized_message, flagged_text = flag['flagged_text'] , user_email= user_email, analysed_entity = flag['entity_type'], criticality = 'SEVERE')
  