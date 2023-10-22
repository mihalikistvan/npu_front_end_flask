"""Python Flask WebApp Auth0 integration example
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for,request

from modules.api import api_connection

api = api_connection()
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Controllers API
@app.route("/")
def home(message = None):

    if request.args.get('query'):
        print (request.args.get('query'))
        creations = api.search_creations_by_bricks(request.args.get('query'))
    else:
        creations = api.search_creations()
    return render_template(
        "home.html",
        session=session.get("user"),
        creations=creations,
        message=request.args.get('message')
    )


@app.route("/rating")
def rating():   
    if request.args.get('creation_id'):
        creation_metadata = api.search_one_creation(request.args.get('creation_id'))
        ratings_for_creation = api.search_creation_ratings(request.args.get('creation_id'))

        return render_template(
            "rating.html",
            creation_metadata=creation_metadata,
            ratings_for_creation=ratings_for_creation
        )
    else:
        return render_template("no_data.html")

@app.route("/rating_success", methods=["POST"])
def rating_success():   
    if session:
        result = api.add_rating(
                        creation_id=request.form.get('creation_id'),
                        uniqueness=request.form.get('uniqueness_range'),
                        creativity=request.form.get('creativity_range'),
                        rated_by=session.get("user")['userinfo']['email'])
        if result =="Successful rating.":
            return redirect(url_for("home", message='rating'))
        else:
            return redirect(url_for("home", message='rating_error'))
    else: 
        return render_template("no_access.html")

@app.route("/brick_list")
def brick_list():   
    brick_dict = api.search_bricks()
    return render_template(
        "brick_list.html",
        brick_dict=brick_dict
    )

@app.route("/upload")
def upload():

    if session:
        brick_dict = api.search_bricks()
        return render_template(
            "upload.html",
            brick_dict=brick_dict,
            session=session.get("user")
        )
    else: 
        return render_template(
            "no_access.html")
    
@app.route("/upload_success", methods=["POST"])
def upload_success():
    if session:
        print (request.form)
        api.upload(form=request.form,
                   files=request.files['creation_file'],
                   email=session.get("user")['userinfo']['email'])
        return redirect(url_for("home", message="upload"))
    else: 
        return render_template(
            "no_access.html")


#auth
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000),debug=True) 
