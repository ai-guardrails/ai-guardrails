from repo.postgres import SqlAudits
from repo.db import conversation_context
from globals import *
from service.chat_service import chat_service

pg_schema = Globals.pg_schema
class admin_service:

    #SqlAudits
    def get_org():
        return SqlAudits.get_org()
    
    def save_org(request_data):
        return SqlAudits.save_org(request_data)
    
    def get_all_list(table_name, sort, range_, filter_):
        table=f'{pg_schema}.{table_name}'
        total_count=SqlAudits.count_query(table, filter_)
        rows=SqlAudits.get_list_query(table, sort, range_, filter_)
    
        if total_count['success'] and rows['success']:
            data={"rows":rows['data'],"totalRows":total_count['data']}
            return {"data":data,"success":True,"message":"Successfully retrieved the data"}
        else:
            return {"data":{},"success":False,"message":"Error in retrieving the data"}

    
    def get_one_data(table_name, id):
        table=f'{pg_schema}.{table_name}'
        return SqlAudits.get_one_query(table, id)
    
    def update_data(table_name, id, data):
        table=f'{pg_schema}.{table_name}'
        return SqlAudits.update_query(table, id, data)
    
    def insert_data(table_name, data):
        table=f'{pg_schema}.{table_name}'
        return SqlAudits.create_query(table, data)

    #mongodb
    def get_conversation_list(sort, range_, filter_):
        total_count=conversation_context.get_conversation_list_count(filter_)
        rows=conversation_context.get_conversation_list(sort, range_, filter_)
        
        if total_count['success'] and rows['success']:
            data={"rows":rows['data'],"totalRows":total_count['data']}
            return {"data":data,"success":True,"message":"Successfully retrieved the data"}
        else:
            return {"data":{},"success":False,"message":"Error in retrieving the data"}
    
    def get_conversation_approval_requests_list( user_email,sort, range_, filter_):
        total_count=conversation_context.get_conversation_approval_requests_count(user_email, filter_)
        rows=conversation_context.get_conversation_approval_requests(user_email, sort, range_, filter_)

        if total_count['success'] and rows['success']:
            data={"rows":rows['data'],"totalRows":total_count['data']}
            return {"data":data,"success":True,"message":"Successfully retrieved the data"}
        else:
            return {"data":{},"success":False,"message":"Error in retrieving the data"}

    def approve_escalation(conversation_id, user_email):
        data=conversation_context.approve_escalation(conversation_id)
        message = f"Request Approved by: {user_email}"
        chat_service.update_conversation(conversation_id,message,'guardrails',user_email,model=None,user_action_required=False)
        return data

    def reject_escalation(conversation_id, user_email):
        data=conversation_context.reject_escalation(conversation_id)
        message = f"Request Rejected by: {user_email}"
        chat_service.update_conversation(conversation_id,message,'guardrails',user_email,model=None,user_action_required=False)
        return data

