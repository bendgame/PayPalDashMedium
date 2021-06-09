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

import dash_bootstrap_components as dbc
import requests
import json
button = html.Div([dbc.Button("subscribe", id="sub-button", className="mr-2")])
def create_user():
    create = html.Div([ html.H1('Create User Account')
            , dcc.Location(id='create_user', refresh=True)
            , dcc.Input(id="username"
                , type="text"
                , placeholder="user name"
                , maxLength =15)
            , dcc.Input(id="password"
                , type="password"
                , placeholder="password")
            , dcc.Input(id="email"
                , type="email"
                , placeholder="email"
                , maxLength = 50)
            , html.Button('Create User', id='submit-val', n_clicks=0)
            , html.Div(id='container-button-basic')
        ])#end div
    return create

def user_login():
    # if current_user.is_authenticated:
    #     logout_user()
    
    login =  html.Div([dcc.Location(id='url_login', refresh=True)
                , html.H2('''Please log in to continue:''', id='h1')
                , dcc.Input(placeholder='Enter your username',
                        type='text',
                        id='uname-box')
                , dcc.Input(placeholder='Enter your password',
                        type='password',
                        id='pwd-box')
                , html.Button(children='Login',
                        n_clicks=0,
                        type='submit',
                        id='login-button')
                , html.Div(children='', id='output-state')
            ]) #end div
    return login

def login_success_sub():
    success = html.Div([dcc.Location(id='url_login_success', refresh=True)
                , html.Div([html.H2('Login successful.')
                        , html.Br()
                       # , button
                        , html.Br()
                       # , html.Div(id = 'iframe-div')
                        , html.P('Select a Dataset')
                        , dcc.Link('Data', href = '/data')
                    ]) #end div
                , html.Div([html.Br()
                        , html.Button(id='back-button', children='Go back', n_clicks=0)
                    ]) #end div
            ]) #end div
    return success
def login_success2():
    success = html.Div([dcc.Location(id='url_login_success2', refresh=True)
                , html.Div([html.H2('Login successful.')
                        , html.Br()
                        , button
                        , html.Br()
                        , html.Div(id = 'iframe-div')
                        , html.P('Select a Dataset')
                        #, dcc.Link('Data', href = '/data')
                    ]) #end div
                , html.Div([html.Br()
                        , html.Button(id='back-button', children='Go back', n_clicks=0)
                    ]) #end div
            ]) #end div
    return success

def data_page():
    data = html.Div([dcc.Dropdown(
                        id='dropdown',
                        options=[{'label': i, 'value': i} for i in ['Day 1', 'Day 2']],
                        value='Day 1')
                    , html.Br()
                    , html.Div([dcc.Graph(id='graph')])
                ]) #end div
    return data

def failed_login():
    failed = html.Div([ dcc.Location(id='url_login_df', refresh=True)
                , html.Div([html.H2('Log in Failed. Please try again.')
                        , html.Br()
                        , html.Div([user_login()])
                        , html.Br()
                        , html.Button(id='back-button', children='Go back', n_clicks=0)
                    ]) #end div
            ]) #end div
    return failed

def logout_page():

    logout = html.Div([dcc.Location(id='logout', refresh=True)
            , html.Br()
            , html.Div(html.H2('You have been logged out - Please login'))
            , html.Br()
            , html.Div([user_login()])
            , html.Button(id='back-button', children='Go back', n_clicks=0)
        ])#end div
    return logout











