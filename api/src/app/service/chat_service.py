import logging
from oidc import get_current_user_email
from repo.db import conversation_context, anonymize_audit_context,analysis_audit_context,folders_context,prompts_context
from repo.postgres import SqlAudits
from integration.openai_wrapper import openai_wrapper
from integration.document_wrapper import document_wrapper
from integration.presidio_wrapper import presidio_wrapper
from presidio_anonymizer.entities import RecognizerResult
from integration.nsfw_model_wrapper import NSFWModelWrapper
from integration.keycloak_wrapper import keycloak_wrapper
import uuid
from typing import TypedDict
from datetime import datetime
import json
import requests


class conversation_obj(TypedDict):
    _id: str
    title : str
    root_message: str
    last_node: str
    is_active: bool
    messages: list
    created: datetime
    updated: datetime
    user_email: str
    state : str
    assigned_to : list
    
class message_obj(TypedDict):
    id: str 
    role: str
    content: str
    created: datetime
    children: list
    user_action_required: bool

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


class chat_service:
    def analyze(message):
        presidio_analysis = presidio_wrapper.analyze_message(message)
        
        result = chat_service.format_and_filter_analysis(presidio_analysis, message)
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
            chat_service.save_analysis_audit(message, result,get_current_user_email())
        return result

    def chat_completion(data,current_user_email,token):
        try:
            prompt = str(data["message"])
            isOverride = bool(data["isOverride"])
            conversation_id = None
            manage_conversation_context = False
            model = data.get('model_name', None)
            
            if('conversation_id'  in data and  data['conversation_id']):
                conversation_id = data['conversation_id']
                manage_conversation_context = True
            if(isOverride):
                anonymized_prompt = chat_service.anonymize(prompt,current_user_email,conversation_id)
                chat_service.update_conversation(conversation_id,"You chose to Override the warning, proceeding to Open AI.",'guardrails',current_user_email,model)
                stop_conversation = False
                stop_response = ''
            else:
                stop_conversation,stop_response,anonymized_prompt = chat_service.validate_prompt(prompt,conversation_id,current_user_email)
                chat_service.update_conversation(conversation_id,anonymized_prompt,'user',current_user_email,model)
            current_completion = ''

            if stop_conversation:
                chunk  =  json.dumps({
                        "role": "guardrails",
                        "content": stop_response,
                        "user_action_required": True
                    })
                yield (chunk)
                chat_service.save_chat_log(current_user_email, anonymized_prompt)
                chat_service.update_conversation(conversation_id,stop_response,'guardrails',current_user_email,model,user_action_required=True)
                return

            messages = []
            if(manage_conversation_context):
                messages = chat_service.get_history_for_bot(conversation_id, current_user_email)
                if (len(messages) > 1):
                    conversation = conversation_context.get_conversation_by_id(conversation_id, current_user_email)
                    # if(conversation and 'model_name' in conversation and conversation['model_name']):
                    #     model = conversation['model_name']
                    #     print(model)
                    # else:
                    #     model = "gpt-3.5-turbo"
                    #     print("else")
            if(model =="gpt-3.5-turbo"):
                response = openai_wrapper.chat_completion(messages, model)
                # yield (conversation_id)
                for chunk in response:
                    if (
                        chunk["choices"][0]["delta"]
                        and "content" in chunk["choices"][0]["delta"]
                    ):
                        chunk_to_yeild = chunk["choices"][0]["delta"]["content"]
                        current_completion += chunk["choices"][0]["delta"]["content"]
                        chunk = json.dumps({
                                "role": "assistant",
                                "content": chunk_to_yeild,
                            })
                        yield (chunk)
                response.close()
            elif(model =="private-docs"):
                try:
                    logging.info("calling document completion")
                    res = document_wrapper.document_completion(messages,token)
                    answer = res['answer']
                    if res['sources']:
                        sources = res['sources'][0]
                        source = json.loads(sources)['metadata']['source'].split('/')[-1]
                        answer = answer + "  \n  \n" + "Source: " + source  #adding double space + \n because ReactMarkdown in chatbot-ui needs this for next line
                    chunk = json.dumps({
                                    "role": "assistant",
                                    "content": answer,
                                    "sources": res['sources']
                                })
                    yield (chunk)
                    current_completion += answer
                except Exception as e:
                    yield("Sorry. Some error occured. Please try again.")
                    logging.error("error: "+str(e))
            else:
                yield (json.dumps({"error": "Invalid model type"}))
                
        
            chat_service.save_chat_log(current_user_email, anonymized_prompt)
            chat_service.update_conversation(conversation_id,current_completion,'assistant',current_user_email,model)
        except Exception as e:
            yield (json.dumps({"error": "error"}))
            print("error: ", e)
            return

    def validate_prompt(prompt,conversation_id,current_user_email):
        nsfw_score = NSFWModelWrapper.analyze(prompt)
        anonymized_prompt = chat_service.anonymize(prompt,current_user_email)

        updated_prompt = anonymized_prompt
        stop_conversation = False
        stop_response = ''
        #decide if we should stop the conversation
        if nsfw_score > 0.9:
            stop_response =  "Warning From Guardrails: We've detected that your message contains NSFW content. Please refrain from posting such content in a work environment, You can choose to override this warning if you wish to continue the conversation, or you can get your manager's approval before continuing."
            stop_conversation = True
        
        blocked_content = ["Technology Alpha"]
        for word in blocked_content:
             lower_word = word.lower()
             if lower_word in prompt.lower():
                stop_response =  f"Warning From Guardrails: We've detected that your message might contain sensitive info. Please be careful when talking about confidential topics.\n Refer to your company's policy on what is considered confidential information [here](https://synergy-ai.us).\n You can choose to override this warning if you wish to continue the conversation, or you can get your manager's approval before continuing."
                stop_conversation = True
        return stop_conversation,stop_response,updated_prompt
        


    def anonymize(message,email = None, conversaton_id = None):
        if not email:
            email = get_current_user_email()
        analysis = presidio_wrapper.analyze_message(message)
        anonymized_message = presidio_wrapper.anonymyze_message(message, analysis)
        if message != anonymized_message:
            chat_service.save_anonymize_audit(message, chat_service.format_and_filter_analysis(analysis, message), anonymized_message,email,conversaton_id)
        return anonymized_message

    def create_Conversation(prompt,email,model,id=None,):
        message = message_obj(
            id= str(uuid.uuid4()),
            role="user",
            content=prompt,
            created=datetime.now(),
            children=[],
        )
        
        messages = [message]
        conversation = conversation_obj(
            _id= id if id else str(uuid.uuid4()),
            root_message=message['id'],
            last_node=message['id'],
            created=datetime.now(),
            messages= messages,
            user_email=email,
            title= openai_wrapper.gen_title(prompt,model),
            model_name = model,
            state = 'active',
            assigned_to = []
        )
        new_conversation_id = conversation_context.insert_conversation(conversation)
        return new_conversation_id

    def update_conversation(conversation_id, content, role,user_email, model , user_action_required = False):
        conversation = conversation_context.get_conversation_by_id(conversation_id,user_email)
        if(conversation == None):
            chat_service.create_Conversation(content,user_email,model,conversation_id)
            return
        if(model is None or not model):
            model = conversation['model']
        messages = conversation['messages']
        message = message_obj(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            created=datetime.now(),
            children=[],
            user_action_required = user_action_required
        )

       #find message with last node id

        for m in messages:
            m['user_action_required'] = False
            if m['id'] == conversation['last_node']:
                m['children'].append(message['id'])
                break


        conversation['last_node'] = message['id']
        conversation['updated'] = datetime.now()
        conversation['model'] = model

        messages.append(message)
        conversation_context.update_conversation(conversation_id, conversation)

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
            SqlAudits.insert_analysis_audits(text = message, user_email = user_email, flagged_text = flag['flagged_text'],  analysed_entity = flag['entity_type'], criticality = 'SEVERE')
        


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
            SqlAudits.insert_anonymize_audits(original_text = message, anonymized_text  = anonymized_message, flagged_text = flag['flagged_text'] , user_email= user_email, analysed_entity = flag['entity_type'], criticality = 'SEVERE')
    
    def save_chat_log(user_email, text):
        SqlAudits.insert_chat_log(user_email, text)

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
    
    def get_conversations(user_email,flag = False):
        cursor = conversation_context.get_conversations_by_user_email(user_email,flag)
        conversations = []
        for conversation in cursor:
            conversations.append(conversation)
        conversations.sort(key=lambda x: x.get('created'), reverse=True)
        return conversations

    def get_conversation_by_id(conversation_id,user_email):
        return conversation_context.get_conversation_by_id(conversation_id,user_email)
    
    def archive_all_conversations(user_email):
        conversation_context.archive_all_conversations(user_email)

    def archive_conversation(user_email,conversation_id, flag = True):
        conversation_context.archive_unarchive_conversation(user_email,conversation_id,flag)

    
    def get_all_folders(user_email):
        return folders_context.get_folder_data(user_email)
        
        
    
    def upsert_folders(folders,user_email):
        user_folder_data = {
            "user_email": user_email,
            "folders": folders
        }
        folders_context.upsert_folders_by_user_email(user_folder_data,user_email)


    def get_all_prompts(user_email):
        return prompts_context.get_prompts_data(user_email)
        
        
    
    def upsert_prompts(prompts,user_email):
        user_prompts_data = {
            "user_email": user_email,
            "prompts": prompts
        }
        prompts_context.upsert_prompts_by_user_email(user_prompts_data,user_email)


    
    def get_history_for_bot(conversation_id,user_email):
        conversation = conversation_context.get_conversation_by_id(conversation_id,user_email)
        messages = conversation['messages']
        result = []
        for m in messages:
            if(m['role'] == 'assistant'):
                result.append({"role": "assistant", "content": m['content']})
            elif(m['role'] == 'user'):
                result.append({"role": "user", "content": m['content']})
        return result

    def update_conversation_properties(conversation_id,data,user_email):
        conversation_context.update_conversation_properties(conversation_id,data,user_email)

    def request_approval(conversation_id,user_email,user_groups):
        current_group = user_groups[0]   #needs to be updated for multiple groups
        group_managers = keycloak_wrapper.get_users_by_role_and_group("manager", current_group)
        group_managers_emails = [user['email'] for user in group_managers]
        conversation_context.request_approval(conversation_id,group_managers_emails)

        csv_email = ','.join(group_managers_emails)
        message = f"Request sent for approval to: {csv_email}"
        chat_service.update_conversation(conversation_id,message,'guardrails',user_email,model=None,user_action_required=False)
        return message
