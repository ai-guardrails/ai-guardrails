from flask import Flask, Blueprint, Response
from flask_restful import Resource, Api, reqparse, request
from service.pii_service import pii_service
from flask_smorest import Blueprint as SmorestBlueprint
from oidc import oidc
from oidc import get_current_user_email

piiendpoints = SmorestBlueprint('pii', __name__)

@piiendpoints.route('/analyze', methods=['POST'])
@oidc.accept_token(require_token=True)
def analyze(): 
    data = request.get_json(silent=True)
    message = pii_service.analyze(data['message']) 
    return message


@piiendpoints.route('/anonymize', methods=['POST'])
@oidc.accept_token(require_token=True)
def anonymize(): 
    data = request.get_json(silent=True)
    message = pii_service.anonymize(data['message']) 
    return {"result":message}
