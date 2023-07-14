from flask import Flask, Blueprint, Response
from flask_restful import Resource, Api, reqparse, request
from service.userdata_service import userdata_service
from flask_smorest import Blueprint as SmorestBlueprint
from oidc import oidc
from oidc import get_current_user_email

userdataendpoints = SmorestBlueprint('user', __name__)


@userdataendpoints.route('/folders', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_folder_data():
    user_email = get_current_user_email()
    result = userdata_service.get_all_folders(user_email)
    return result if result else {}
    



@userdataendpoints.route('/folders', methods=['PUT'])
@oidc.accept_token(require_token=True)
def upsert_folders():
    data = request.get_json(silent=True)
    user_email = get_current_user_email()
    userdata_service.upsert_folders(data,user_email)
    return {"result":"success"}



@userdataendpoints.route('/prompts', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_prompts_data():
    user_email = get_current_user_email()
    result = userdata_service.get_all_prompts(user_email)
    return result if result else {}
    



@userdataendpoints.route('/prompts', methods=['PUT'])
@oidc.accept_token(require_token=True)
def upsert_prompts():
    data = request.get_json(silent=True)
    user_email = get_current_user_email()
    userdata_service.upsert_prompts(data,user_email)
    return {"result":"success"}