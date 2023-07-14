import requests
from globals import *
class superset:
    def get_access_token():
        url = Globals.superset_url+ '/api/v1/security/login'
        body = {
            "password": Globals.superset_admin_password,
            "provider": "db",
            "refresh": "true",
            "username": Globals.superset_admin_username
        }
        response = requests.post(url=url, json=body)
        tokens = response.json()
        
        return tokens["access_token"], tokens["refresh_token"],response.cookies

    def get_guest_token():
        access_token, refresh_token, cookie = superset.get_access_token()
        url = format(Globals.superset_url)+'/api/v1/security/guest_token'

        headers = {"Authorization": f'Bearer {access_token}'}
        body = {
            "resources": [
                {
                    "id": Globals.superset_dashboardid,
                    "type": "dashboard"
                }
            ],
            "rls": [
            ],
            "user": {
                "first_name": Globals.superset_guestuser_firstname,
                "last_name": Globals.superset_guestuser_lastname,
                "username": Globals.superset_guestuser_username
            }
        }
        response = requests.post(url=url, json=body, headers=headers, cookies=cookie)
        return response.json()