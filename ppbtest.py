import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State
from sqlalchemy import Table, create_engine, update, select
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import warnings
import os
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
import configparser
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from config import client_id, client_secret, plan_id
from layouts import create_user, user_login, login_success_sub,login_success2, data_page, failed_login, logout_page
import dash_bootstrap_components as dbc
import requests
import json
from SubscriptionRequests import SubscriptionRequest, environment, client, SubscriptionActivate

# Creating an environment
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)


warnings.filterwarnings("ignore")

conn = sqlite3.connect('C:\\Users\\MTGro\\Desktop\\online stores\\store.sqlite')
engine = create_engine('sqlite:///C:\\Users\\MTGro\\Desktop\\online stores\\store.sqlite')
db = SQLAlchemy()

config = configparser.ConfigParser()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    subscribed = db.Column(db.Integer)
    status = db.Column(db.String(80))
    orderID = db.Column(db.String(100))

Users_tbl = Table('users', Users.metadata)

app = dash.Dash(__name__)

server = app.server

app.config.suppress_callback_exceptions = True

# config
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI='sqlite:///C:\\Users\\MTGro\\Desktop\\online stores\\store.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(server)
# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

#User as base
# Create User class with UserMixin
class Users(UserMixin, Users):
    pass


app.layout= html.Div([
            html.Div(id='page-content', className='content')
            ,  dcc.Location(id='url', refresh=False)
        ])

# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.callback(
    Output('page-content', 'children')
    , [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return create_user()
    elif pathname == '/login':
        return user_login()
    elif pathname == '/success':
        if current_user.is_authenticated:
            cuid = current_user.get_id()
            conn = sqlite3.connect('C:\\Users\\MTGro\\Desktop\\online stores\\store.sqlite')
            c = conn.cursor()
            c.execute(f"select subscribed from users where id = {cuid}")
            sub = c.fetchone()
            print("sub check")
            print(sub[0])
            if sub[0] ==1:
                return login_success_sub()
            else:
                return login_success2()
        else:
            return failed_login()
    elif pathname =='/data':
        if current_user.is_authenticated:
            return data_page()
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout_page()
        else:
            return logout_page()
    else:
        return '404'

#set the callback for the dropdown interactivity

@app.callback(
   [Output('container-button-basic', "children")]
    , [Input('submit-val', 'n_clicks')]
    , [State('username', 'value'), State('password', 'value'), State('email', 'value')])
def insert_users(n_clicks, un, pw, em):
    hashed_password = generate_password_hash(pw, method='sha256')
    if un is not None and pw is not None and em is not None:
        ins = Users_tbl.insert().values(username=un,  password=hashed_password, email=em,)
        conn = engine.connect()
        conn.execute(ins)
        conn.close()
        return [user_login()]
    else:
        return [html.Div([html.H2('Already have a user account?'), dcc.Link('Click here to Log In', href='/login')])]

@app.callback(
    Output('url_login', 'pathname')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def successful(n_clicks, username, password):
    conn = sqlite3.connect('C:\\Users\\MTGro\\Desktop\\online stores\\store.sqlite')
    c = conn.cursor()
    environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
    client = PayPalHttpClient(environment)   
    user = Users.query.filter_by(username=username).first()
    
    
    if user:
        if check_password_hash(user.password, password):
            login_user(user)
            cuid = current_user.get_id()
           
            print(f"cuid = {cuid}")
            c.execute(f"select orderID from users where id = {cuid}")
            oid = c.fetchone()
            
            print(f"oid = {oid[0]}")
            #url = f'https://api.sandbox.paypal.com/v1/billing/subscriptions/{oid[0]}'

          

            #print(url)
            if oid[0] is not None:
                print ("o1")
                act = SubscriptionActivate(oid[0])
                # r = requests.get(url, headers = headers)
                # r3 = r.json()

                response = client.execute(act)
            
                #if r3['status'] == 'ACTIVE':
                if response.result.status == 'ACTIVE':
                    print ("o2")
                    upd = update(Users).where(Users.id == cuid).values(subscribed=1, status= 'ACTIVE')
                    conn = engine.connect()
                    conn.execute(upd)
                    conn.close()
                else:
                    print ("o3")
                    upd = update(Users).where(Users.id == cuid).values(subscribed=0)
                    conn = engine.connect()
                    conn.execute(upd)
                    conn.close()
                           
            
                return '/success'
            else:
                print("o4")
                upd = update(Users).where(Users.id == cuid).values(subscribed=0)
                conn = engine.connect()
                conn.execute(upd)
                conn.close()
            return '/success'
        else:
            print("o5")
            pass
    else:
        print ("o6")
        pass

@app.callback(
    Output('output-state', 'children')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'Incorrect username or password'
        else:
            return 'Incorrect username or password'
    else:
        return ''

@app.callback(
    Output('url_login_success', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'

@app.callback(
    Output('url_login_success2', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'

@app.callback(
    Output('url_login_df', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
# Create callbacks

@app.callback(
    Output('url_logout', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'

@app.callback(
    Output("iframe-div", "children"),
    [Input('sub-button', 'n_clicks')]
)
def sub(n):
    environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
    client = PayPalHttpClient(environment)
    
    cuid = current_user.get_id()
    print(current_user.get_id())
    sub = SubscriptionRequest()

    sub.prefer('return=representation')

    sub.request_body({
      "plan_id": plan_id,
      "application_context": {
        "brand_name": "your_brand",
        "locale": "en-US",
        "shipping_preference": "SET_PROVIDED_ADDRESS",
        "user_action": "SUBSCRIBE_NOW",
        "payment_method": {
          "payer_selected": "PAYPAL",
          "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
        },
        "return_url": "http://127.0.0.1:9000/login",
        "cancel_url": "http://127.0.0.1:9000/login"
      }
    })
    if n is None:
        n = 0
        alink = ''
    if n > 0:
        response = client.execute(sub)
        subid = response.result.id
        alink = response.result.links[0].href
        status = response.result.status
        upd = update(Users).where(Users.id == cuid).values(orderID=subid, status= status)
        
        conn = engine.connect()
        conn.execute(upd)
        conn.close()

    
    return [html.Iframe(src=alink)]

if __name__ == '__main__':
    app.run_server(port = 9000, debug=True)