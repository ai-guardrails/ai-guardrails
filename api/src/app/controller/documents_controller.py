from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint, Response, jsonify
from flask_restful import Resource, Api, reqparse, request
from flask_smorest import Blueprint as SmorestBlueprint
from service.document_service import DocumentService
from database.models import DocumentEntity
from globals import Globals
import os
from oidc import oidc
from time import time


documentsendpoints = SmorestBlueprint('documents', __name__)

# GET all documents
@documentsendpoints.route('/documents', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_documents():
    sort = request.args.get('sort', default=None, type=str)
    range_ = request.args.get('range', default=None, type=str)
    filter_ = request.args.get('filter', default=None, type=str)
    
    return DocumentService.get_documents(DocumentEntity,sort, range_, filter_)


# GET a single document
@documentsendpoints.route('/documents/<int:document_id>', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_document(document_id):
    return DocumentService.get_document(DocumentEntity,document_id)


# CREATE a new document
@documentsendpoints.route('/documents', methods=['POST'])
@oidc.accept_token(require_token=True)
def create_document():
    files = request.files.getlist('files')
    temp_dir_name = "temp-" + str(time())
    os.mkdir(temp_dir_name)
    for file in files:
        file.save(os.path.join(temp_dir_name, file.filename))
    return DocumentService.create_documents(files=files, location=temp_dir_name)
    


# UPDATE an existing document
@documentsendpoints.route('/documents/<int:document_id>', methods=['PUT'])
@oidc.accept_token(require_token=True)
def update_document(document_id):
    title= request.json.get('title'),
    description= request.json.get('description'),
    location= request.json.get('location')
    folder_id= request.json.get('folder_id')
    return DocumentService.update_document(document_id=document_id ,title=title, description=description, location=location, folder_id=folder_id)
    

# DELETE a document
@documentsendpoints.route('/documents/<int:document_id>', methods=['DELETE'])
@oidc.accept_token(require_token=True)
def delete_document(document_id):
    return DocumentService.delete_document(document_id)





