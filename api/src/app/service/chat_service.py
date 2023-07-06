import logging
from oidc import get_current_user_email
from repo.db import conversation_context
from repo.postgres import SqlAudits
from integration.openai_wrapper import openai_wrapper
from integration.document_wrapper import document_wrapper
from integration.presidio_wrapper import presidio_wrapper
from presidio_anonymizer.entities import RecognizerResult
from integration.nsfw_model_wrapper import NSFWModelWrapper
from integration.keycloak_wrapper import keycloak_wrapper
from service.pii_service import pii_service
import uuid
from typing import TypedDict,Optional
from datetime import datetime
import json
import requests

override_message = "You chose to Override the warning, proceeding to Open AI."
nsfw_warning = "Warning From Guardrails: We've detected that your message contains NSFW content. Please refrain from posting such content in a work environment, You can choose to override this warning if you wish to continue the conversation, or you can get your manager's approval before continuing."

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
    msg_info: Optional[dict]


class chat_service:
    def chat_completion(data,current_user_email,token):
        try:
            task = str(data["task"]) if "task" in data else None
            isPrivate = bool(data["isPrivate"]) if "isPrivate" in data else False
            piiScan = True 
            nsfwScan = True

            prompt = str(data["message"])
            isOverride = bool(data["isOverride"])
            conversation_id = None
            manage_conversation_context = False
            model = data.get('model_name', None)
            if(model =="private-docs" or model == "private-docs-private-llm"):
                isOverride = True
            
            if('conversation_id'  in data and  data['conversation_id']):
                conversation_id = data['conversation_id']
                manage_conversation_context = True


            stop_conversation,stop_response,updated_prompt,role = chat_service.validate_prompt(prompt,isOverride,piiScan,nsfwScan,current_user_email,conversation_id)
            chat_service.update_conversation(conversation_id,updated_prompt,'user',current_user_email,model)
            
            current_completion = ''
            user_action_required = False
            msg_info = None

            if stop_conversation:

                chunk  =  json.dumps({
                        "role": "guardrails",
                        "content": stop_response,
                        "user_action_required": True
                    })
                yield (chunk)

                current_completion = stop_response
                role = "guardrails"
                user_action_required = True
            else:
                messages = []
                role = "assistant"
                if(manage_conversation_context):
                    messages = chat_service.get_history_for_bot(conversation_id, current_user_email)
                    

                if(model =="gpt-3.5-turbo"):
                    response = openai_wrapper.chat_completion(messages, model)
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
                elif(model =="private-docs" or model == "private-docs-private-llm" ):
                    try:
                        is_private = False
                        if(model == "private-docs-private-llm"):
                            is_private = True
                        logging.info("calling document completion")
                        res = document_wrapper.document_completion(messages,token, is_private,prompt)
                        answer = res['answer']
                        if res['sources']:
                            sources = res['sources'][0]
                            source = json.loads(sources)['metadata']['source'].split('/')[-1]
                        msg_info={
                            "source": source,
                        }
                        chunk = json.dumps({
                                        "role": "assistant",
                                        "content": answer,
                                        "msg_info": msg_info,
                                    })
                        yield (chunk)
                        current_completion += answer
                    except Exception as e:
                        yield("Sorry. Some error occured. Please try again.")
                        logging.error("error: "+str(e))
                else:
                    yield (json.dumps({"error": "Invalid model type"}))
                
            chat_service.save_chat_log(current_user_email, updated_prompt)
            chat_service.update_conversation(conversation_id,current_completion,role,current_user_email,model,msg_info,user_action_required)
        except Exception as e:
            yield (json.dumps({"error": "error"}))
            logging.info("error: ", e)
            return

    def validate_prompt(prompt,isOverride, pii_scan, nsfw_scan,current_user_email,conversation_id):
        logging.info("piiScan: ", pii_scan)
        logging.info("nsfwScan: ", nsfw_scan)
        stop_conversation = False
        stop_response = ""
        role = "guardrails"
        nsfw_threshold = 0.94

        if(isOverride):
            return stop_conversation,stop_response,prompt,role

        if(nsfw_scan):
            nsfw_score = NSFWModelWrapper.analyze(prompt)
            print (nsfw_score)
            if nsfw_score > nsfw_threshold:
                stop_response =  nsfw_warning
                stop_conversation = True
                logging.info("returning from nsfw")
                return stop_conversation,stop_response,prompt,role
            
        if(pii_scan):
            updated_prompt = pii_service.anonymize(prompt,current_user_email,conversation_id)
            stop_conversation = False
            
            logging.info("returning from pii")
            return stop_conversation,stop_response,updated_prompt,role
        
    def create_Conversation(prompt,email,model,msg_info,id=None,):
        message = message_obj(
            id= str(uuid.uuid4()),
            role="user",
            content=prompt,
            created=datetime.now(),
            children=[],
            msg_info=msg_info
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

    def update_conversation(conversation_id, content, role,user_email, model ,msg_info=None, user_action_required = False):
        conversation = conversation_context.get_conversation_by_id(conversation_id,user_email)
        if(conversation == None):
            chat_service.create_Conversation(content,user_email,model,msg_info,conversation_id)
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
            user_action_required = user_action_required,
            msg_info = msg_info
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

    def save_chat_log(user_email, text):
        SqlAudits.insert_chat_log(user_email, text)

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
