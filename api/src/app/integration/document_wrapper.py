import json
import logging
import requests
from globals import Globals

url = Globals.open_ai_api_key
class document_wrapper:
    
    def document_completion(messages,token):
        res = {}
        try:
            url = Globals.document_api_url
            payload = json.dumps({
                "query": messages[-1]['content'],
            })
            
            headers = {
                "Authorization" : f"Bearer {token}",
                "Content-Type": "application/json"
            }
            res = requests.request("POST", url + "/qa", headers=headers, data=payload).json()
            logging.info("response From document_completion: "+str(res))
        except Exception as e:
            logging.error("error: "+str(e))
        return res
    

