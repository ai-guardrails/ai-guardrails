from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint, Response, jsonify, abort
from flask_restful import Resource, Api, reqparse, request
from functools import wraps
from integration.superset_wrapper import superset
from service.admin_service import admin_service
from flask_smorest import Blueprint as SmorestBlueprint
from marshmallow import Schema, fields,validate
from oidc import get_current_user_email
from oidc import get_current_user_roles
from oidc import oidc
from database.models import  AnalysisAuditEntity, AnonymizeAuditEntity, ChatLogEntity,CustomRuleEntity,PredefinedRuleEntity


adminendpoints = SmorestBlueprint('admin', __name__)

def require_role(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            roles=get_current_user_roles()
            if role_name in roles:
                return func(*args, **kwargs)
            else:
                abort(403)
        return wrapper
    return decorator

@adminendpoints.route('/fetchguesttoken')
@oidc.accept_token(require_token=True)
def superset_token():
    return superset.get_guest_token()

#predefinedrules get_list, get, put endpoints
@adminendpoints.route('/predefined_rules', methods=['GET'])
@oidc.accept_token(require_token=True)
def predefined_rules_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    
    data=admin_service.get_all_list(PredefinedRuleEntity, sort, range_, filter_)
    return data,200

@adminendpoints.route('/predefined_rules/<id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def predefined_rules_get_one(id):
    return admin_service.get_one_data(PredefinedRuleEntity, id)

@adminendpoints.route('/predefined_rules/<id>', methods=['PUT'])
@oidc.accept_token(require_token=True)
def predefined_rules_update(id):
    data = request.json
    return admin_service.update_data(PredefinedRuleEntity, id, data)


#custom_rules get_list,get,put,post
@adminendpoints.route('/custom_rules', methods=['GET'])
@oidc.accept_token(require_token=True)
def custom_rules_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)

    data=admin_service.get_all_list(CustomRuleEntity, sort, range_, filter_)
    return data,200

@adminendpoints.route('/custom_rules', methods=['POST'])
@oidc.accept_token(require_token=True)
def custom_rules_create():
    data = request.json
    return admin_service.insert_data(CustomRuleEntity, data)


@adminendpoints.route('/custom_rules/<id>', methods=['PUT'])
@oidc.accept_token(require_token=True)
def custom_rules_update(id):
    data = request.json
    return admin_service.update_data(CustomRuleEntity, id, data)

@adminendpoints.route('/custom_rules/<id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def custom_rules_get_one(id):
    return admin_service.get_one_data(CustomRuleEntity, id)

#analysis_audit get_list, get
@adminendpoints.route('/analysis_audit', methods=['GET'])
@oidc.accept_token(require_token=True)
def analysis_audit_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)

    data=admin_service.get_all_list(AnalysisAuditEntity, sort, range_, filter_)
    return data,200


@adminendpoints.route('/analysis_audit/<id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def analysis_audit_get_one(id):
    return admin_service.get_one_data(AnalysisAuditEntity, id)


#anonymize_audit get_list, get
@adminendpoints.route('/anonymize_audit', methods=['GET'])
@oidc.accept_token(require_token=True)
def anonymize_audit_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    
    data=admin_service.get_all_list(AnonymizeAuditEntity, sort, range_, filter_)
    return data,200

@adminendpoints.route('/anonymize_audit/<id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def anonymize_audit_get_one(id):
    return admin_service.get_one_data(AnonymizeAuditEntity, id)


#chat_get get_list, get
@adminendpoints.route('/chat_log', methods=['GET']) 
@oidc.accept_token(require_token=True)
def chat_log_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    
    data=admin_service.get_all_list(ChatLogEntity, sort, range_, filter_)
    return data,200


@adminendpoints.route('/chat_log/<id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def chat_log_get_one(id):
    return admin_service.get_one_data(ChatLogEntity, id)


#conversation_log get_list, get
@adminendpoints.route('/conversation_log', methods=['GET'])
@oidc.accept_token(require_token=True)
def conversation_log_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    
    data=admin_service.get_conversation_list( sort, range_, filter_)
    return data,200

@adminendpoints.route('/escalations', methods=['GET'])
@oidc.accept_token(require_token=True)
@require_role('manager')
def approvalrequests_get_list():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    user_email = get_current_user_email()

    data=admin_service.get_conversation_approval_requests_list( user_email, sort, range_, filter_)
    return data,200

@adminendpoints.route('/approve_escalation/<conversation_id>', methods=['PUT'])
@oidc.accept_token(require_token=True)
@require_role('manager')
def approve_escalation(conversation_id):
    #email of user whose conversation is escalated recieving from admin-ui
    user_email = request.json
    data=admin_service.approve_escalation( conversation_id, user_email )
    return data,200

@adminendpoints.route('/reject_escalation/<conversation_id>', methods=['PUT'])
@oidc.accept_token(require_token=True)
@require_role('manager')
def reject_escalation(conversation_id):
    #email of user whose conversation is escalated recieving from admin-ui
    user_email = request.json
    data=admin_service.reject_escalation( conversation_id, user_email )
    return data,200