# Okta_dev_challenge
This repository hosts the code written by Anushrav Vatsa for a technical exercise. 
This application leverages Okta's authentication services and web API to manage users.
This app is built with Flask as the backend and HTML and CSS for webpages.

## Getting Started

These instructions are for unix-like systems. 

### Pre-requisites to run this code:
- Python (3.6<)
- Okta Developer Account


### Setup 
1. An Okta Devloper Account (https://developer.okta.com/)
  - Create an App and copy the cleint credentials.  
  - Add `Login redirect URIs` and `Initiate login URI ` as `http://localhost:8080/oidc/callback`
  - Add `Logout redirect URIs` as `http://localhost:8080`
  - Generate an API Token from the API tab. 
  - Make sure to enable CORS and redirect options.

2. Clone this repository, jump to the root folder by running and install dependencies.
```
git init
git clone https://github.com/anushrav/okta_dev_challenge.git
cd okta_dev_challenge
pip3 install requirements.txt

```
3. Configure client_secrets.json by replacing `{DEV_ID}` with your okta account info.

```
{
  "web": {
    "client_id": "CLIENT_ID",
    "client_secret": "CLIENT_SECRET",
    "auth_uri": "https://{DEV_ID}.okta.com/oauth2/default/v1/authorize",
    "token_uri": "https://{DEV_ID}.okta.com/oauth2/default/v1/token",
    "issuer": "https://{DEV_ID}.okta.com/oauth2/default",
    "userinfo_uri": "https://{DEV_ID}.okta.com/oauth2/default/userinfo",
    "redirect_uris": [
      "http://localhost:8080/dashboard"
    ]
  }
}
```
4. Create a .env file by running `nano .env`
   Add the following information to that file: 

```
BASE_URL=https://{DEV_ID}.okta.com
OKTA_API_TOKEN={api-token-from-dev-portal}
ADMIN_GROUP_ID={group-id-for-admin-group}
APP_SECRET={long-random-string}
```
   Press `crtl+ O` to save and `crtl+ X` to exit.
  
5. To start the application run `python3 main.py` from the root directory of the project. 
   Navigate to `http://localhost:8080/` to view the homepage. If configured correctly, 
   the application shoudl open the welcome page. Users and Admins can now login securely from this page.
   
   
## Notes:
1. Regular users have access to thier dashboard Page only.
2. Admins have access to thier dashbaord page and user management tools.
3. Only the open landing page `http://localhost:8080/` is accessible without authentication.


## Reffernces:
1. Okta Python SDK: https://github.com/okta/okta-sdk-python/
2. Okta Web Api: https://developer.okta.com/docs/api/resources/users.html
3. Flask Tutorial: Simple User Registration and Login: https://developer.okta.com/blog/2018/07/12/flask-tutorial-simple-user-registration-and-login
4. Flask Documentation: https://flask.palletsprojects.com/en/1.1.x/
   


