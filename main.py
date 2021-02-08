from flask import Flask, render_template, g, redirect, url_for, request, flash, render_template_string
from dotenv import load_dotenv
import os
from flask_oidc import OpenIDConnect
import requests
from okta.client import Client
from okta import api_client
from okta import models
import asyncio
from wtforms import Form, StringField, PasswordField, validators, SubmitField


# New User Registration form description
class RegistrationForm(Form):
    firstName = StringField('First Name', [validators.DataRequired(), validators.Length(min=6, max=25)])
    lastName = StringField('Last Name', [validators.DataRequired(), validators.Length(min=6, max=25)])
    email = StringField('Email Address', [validators.DataRequired(), validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Add User')


app = Flask(__name__)

#Load config from the eviroment and client_secrets.json
load_dotenv()
app.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
app.config["OIDC_COOKIE_SECURE"] = False                        #no need for SSL since this will be run locally
app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config["SECRET_KEY"] = os.environ.get('APP_SECRET')
app.config["OIDC_ID_TOKEN_COOKIE_NAME"] = "oidc_token"

#obtained from the Okta Dev Portal
base_url = os.environ.get('BASE_URL')
okta_api_token = os.environ.get('OKTA_API_TOKEN')  
admin_group_id = os.environ.get("ADMIN_GROUP_ID")

#set up app and client
config = {
    'orgUrl': base_url,
    'token': okta_api_token} 

oidc = OpenIDConnect(app)
okta_client = Client(config)

#Verify before user reqeusts anything.
@app.before_request
def before_request():
    if oidc.user_loggedin:
        g.user = okta_client.get_user(oidc.user_getfield("sub"))
    else:
        g.user = None

#Home route that shows an open landing page. Available without authentication
@app.route("/")
def index():
    return render_template("index.html", oidc=oidc)

'''
All routes from here will require the user to authenticate.
Trying to navigate to these pages will result in a redirect to Okta's Login Page 
if the user doesn't have an active session
'''

#User Home page with links to tools if a user has admin Privlages
@app.route("/dashboard", methods=['GET', 'POST'])
@oidc.require_login
def dashboard():
    
    groups = []
    user_info = []
    
    #API Call to get User's Groups check for Admin Ststus
    async def get_usersGroup():
        users_groups, resp, err = await okta_client.list_user_groups(oidc.user_getfield("sub"))
        for i in  range(len(users_groups)):
             groups.append(users_groups[i].profile.name)

    #API Call to get User's data to display on the webpage         
    async def get_usersinfo():
        user, resp, err = await okta_client.get_user(oidc.user_getfield("sub"))
        user_info.extend((user.id, user.profile.first_name, user.profile.last_name))

    asyncio.run(get_usersGroup())   
    asyncio.run(get_usersinfo())
    

    if 'Admins' not in groups:
        return render_template("dashboard_user.html", name = user_info[1], id = user_info[0])

    else:
        return render_template("dashboard_admin.html", name = user_info[1], id = user_info[0])


#Form for adding new users
#Mehtod for add_user API call
@app.route("/user_new", methods=['GET', 'POST'])
@oidc.require_login
def user_new():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # Create Password
        password = models.PasswordCredential({
            'value': form.password.data
                })

        # Create User Credentials
        user_creds = models.UserCredentials({
            'password': password
            })

        # Create User Profile and CreateUser Request
        user_profile = models.UserProfile()
        user_profile.first_name = form.firstName.data
        user_profile.last_name = form.lastName.data
        user_profile.email = form.email.data
        user_profile.login = form.email.data

        create_user_req = models.CreateUserRequest({
        'credentials': user_creds,
        'profile': user_profile
        })

        async def user_add():
            # Create User
            user, resp, err = await okta_client.create_user(create_user_req)
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")

        asyncio.run(user_add())

        flash('Thanks for registering')
    
        return redirect(url_for("dashboard"))
    
    return render_template("user_add.html", form=form)

'''
This route only executes API calls
This redirects to dashboard on seccesful completetion 
Throws the approriate error if call fails.
'''
@app.route("/user_upgrade")
@oidc.require_login
def upgrade():
    # List of Keys 
    keyList = ["first_name", "last_name", "id", "email"] 
    user_dict = {} 
    user_list = []
    async def get_users():
            # Get Users
            user, resp, err = await okta_client.list_users()
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
            for i in range(len(user)):
                user_dict = {
                    'first_name': user[i].profile.first_name, 
                    'last_name': user[i].profile.last_name, 
                    'id' : user[i].id, 
                    'email' : user[i].profile.login
                        }
                user_list.append(user_dict)

              
    asyncio.run(get_users())
    
    for i in range(len(user_list)):

    #API Call to get User's Groups check for Admin Ststus
        groups = []
        async def get_usersGroup():
            users_groups, resp, err = await okta_client.list_user_groups(user_list[i]['id'])
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
            for j in  range(len(users_groups)):
                groups.append(users_groups[j].profile.name)
            
        asyncio.run(get_usersGroup())
        user_list[i].update({'groups':groups})

    item = []
    for i in range(len(user_list)):
        if 'Admins' not in user_list[i]['groups'] :
             item.append(user_list[i])

        
    return render_template("user_upgrade.html", items = item )

@app.route("/user_mgmt")
@oidc.require_login
def mgmt():
    # List of Keys  for user profile
    keyList = ["first_name", "last_name", "id", "email"] 
  
    user_dict = {} 
    user_list = []
    async def get_users():
            # Get Users
            user, resp, err = await okta_client.list_users()
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
            for i in range(len(user)):
                user_dict = {
                    'first_name': user[i].profile.first_name, 
                    'last_name': user[i].profile.last_name, 
                    'id' : user[i].id, 
                    'email' : user[i].profile.login
                        }
                user_list.append(user_dict)

              
    asyncio.run(get_users())
        
    return render_template("user_mgmt.html", items = user_list )   

'''
This route only executes API calls
This redirects to dashboard on seccesful completetion 
Throws the approriate error if the API call fails.
'''

#This route adds user to the Admins group for elevagted privlages.
@app.route("/up_user", methods=['GET', 'POST'])
@oidc.require_login
def upgrade_user():
    
    if request.method == 'POST' :
        user_id = request.form['Add to Admin']
        async def add_to_admin():
            resp, err = await okta_client.add_user_to_group(admin_group_id, user_id) 
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
        
        asyncio.run(add_to_admin())    
        return redirect(url_for("dashboard"))
    
    return redirect(url_for("up_user"))

#This route performs the two step user deletion request.

@app.route("/rm_user", methods=['GET', 'POST'])
@oidc.require_login
def rm_user():
    
    if request.method == 'POST' :
        user_id = request.form['Remove User']
        async def deactivate_user():
            resp, err = await okta_client.deactivate_or_delete_user(user_id) 
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
        async def remove_user():
            resp, err = await okta_client.deactivate_or_delete_user(user_id)
            if (resp._status != 200):
                return render_template_string("Could not fulfil request. Please try again.")
        asyncio.run(deactivate_user())    
        asyncio.run(remove_user())

        return redirect(url_for("dashboard"))
    
    return redirect(url_for("rm_user"))


# Login Route redirects to Okta Hosted Login and then to user dashboard if authneticated securely.
@app.route("/login")
@oidc.require_login
def login():
    return redirect(url_for("dashboard"))

#Performs Local session Logout. 
#Ends user session in the browser. User still logged in on Okta's server.
@app.route("/logout")
@oidc.require_login
def logout():
    oidc.logout()
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)   