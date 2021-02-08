# okta_dev_challenge
This repository hosts the code written by Anushrav Vatsa for a technical exercise. 
This application leverages Okta's authentication services and web API to manage users.
This app is biult with Flask as the backend and HTML and CSS for webpages.

## Getting Started

These instructions are unix-like systems. 

### Pre-requisites:
- Python (3.6<)


### Setup 
1. An Okta Devloper Account (https://developer.okta.com/)
  - Create an App and copy the cleint credentials.  
  - Add `Login redirect URIs` and `Initiate login URI ` as `http://localhost:8080/oidc/callback`
  - Add `Logout redirect URIs` as `http://localhost:8080`

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

```
BASE_URL=https://{DEV_ID}.okta.com
OKTA_API_TOKEN={api-token-from-dev-portal}
ADMIN_GROUP_ID={group-id-for-admin-group}
APP_SECRET={long-random-string}
```
