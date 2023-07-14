from flask import Flask, Blueprint, Response
from flask_restful import Resource, Api, reqparse, request
from service.chat_service import chat_service
from flask_smorest import Blueprint as SmorestBlueprint
from time import time
import os
from oidc import oidc
from oidc import get_current_user_email
from oidc import get_current_user_groups
from utils.util import utils
import json

endpoints = SmorestBlueprint('chat', __name__)

@endpoints.route('/completions', methods=['POST'])
@oidc.accept_token(require_token=True)
def chat_completion():
    data = request.get_json(silent=True)
    user_email = get_current_user_email()
    token = request.headers['authorization'].split(' ')[1]
    def chat_completion_stream(data,user_email):
        response = chat_service.chat_completion(data,user_email,token)
        for chunk in response:
            yield chunk
    return Response(chat_completion_stream(data,user_email), mimetype='text/event-stream')


@endpoints.route('/conversations', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_conversations():
    archived_param = request.args.get('archived')
    flag = archived_param.lower() == 'true'
    user_email = get_current_user_email()
    conversations = chat_service.get_conversations(user_email,flag)
    return utils.rename_id(conversations)


@endpoints.route('/conversations/<conversation_id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_conversation_by_id(conversation_id):
    user_email = get_current_user_email()
    return chat_service.get_conversation_by_id(conversation_id,user_email)


@endpoints.route('/conversations/archive', methods=['DELETE'])
@oidc.accept_token(require_token=True)
def archive_all_conversations():
    user_email = get_current_user_email()
    chat_service.archive_all_conversations(user_email)
    return {"result":"success"}


@endpoints.route('/conversations/archive/<conversation_id>', methods=['DELETE'])
@oidc.accept_token(require_token=True)
def archive_conversation(conversation_id):
    archived_param = request.args.get('flag')
    flag = archived_param.lower() == 'true'
    user_email = get_current_user_email()
    chat_service.archive_conversation(user_email, conversation_id,flag=flag)
    return {"result":"success"}


@endpoints.route('/conversations/<conversation_id>/properties', methods=['PUT'])
@oidc.accept_token(require_token=True)
def update_conversation_properties(conversation_id):
    data = request.get_json(silent=True)
    user_email = get_current_user_email()
    chat_service.update_conversation_properties(conversation_id,data,user_email)
    return {"result":"success"}


@endpoints.route('/requestapproval/<conversation_id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def request_approval(conversation_id):
    user_email = get_current_user_email()
    user_groups = get_current_user_groups()
    message=chat_service.request_approval(conversation_id,user_email,user_groups)
    return {"message":message}

@endpoints.route('/summarizebrief', methods=['POST'])
@oidc.accept_token(require_token=True)
def create_document():
    data = json.loads( request.form['data'])
    user_email = get_current_user_email()
    token = request.headers['authorization'].split(' ')[1]
    files = request.files.getlist('files')
    file = files[0]
    # save file to disk
    filename = file.filename
    filepath = os.path.join(os.getcwd(), filename)
    file.save(filepath)
    file.close()
    def summarize_brief_stream(data,user_email,filename,filepath,token):
        response=chat_service.summarize_brief(data,user_email,filename,filepath,token)
        for chunk in response:
            yield chunk
    return Response(summarize_brief_stream(data,user_email,filename,filepath,token), mimetype='text/event-stream')
