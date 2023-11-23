from __future__ import print_function

import sys
import base64
import firebase_admin
from PIL import Image
from firebase_admin import credentials, firestore
from flask import Flask, redirect, render_template, request, url_for
from transformers.models import openai

from ai_lib import id_img_to_text, image_path_to_np_array, request_json_from_id_text, compare_faces

from openai import OpenAI

from firestore_utils import get_object, save_image, save_base64_image

app = Flask(__name__)  # Initialze flask constructor

# initialize firebase
cred = credentials.Certificate("firestore/hacathon-405514-firebase-adminsdk-8k34v-49ee4584ff.json")
firebase_app = firebase_admin.initialize_app(cred)

db = firestore.client()
# Initialze person as dictionary
person = {"is_logged_in": False, "email": ""}

openai.api_key = "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"




@app.route("/")
def home_page():
    return render_template("home.html")


# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if person['is_logged_in']:
        return render_template("download.html")
    return render_template("login.html")


# Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"]:
        return render_template("welcome.html", email=person["email"])
    else:
        return redirect(url_for('login'))


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        form = request.form  # Get the data
        cnp = form["cnp"]
        password = form["password"]

        try:
            doc_ref = db.collection('users').document(cnp)
            doc = doc_ref.get()
            if doc.exists:
                administrator = doc.to_dict().get("password")

                if administrator == password:  # success login scenario
                    global person
                    person["is_logged_in"] = True
                    person["cnp"] = cnp

                    global my_object
                    my_object = get_object(db, cnp)

                    save_image(my_object)

                    return redirect(url_for('welcome'))

                return redirect(url_for('login'))  # log in failed
            else:
                    # If there is any error, redirect back to login

                return redirect(url_for('login'))

        except:
            # If there is any error, redirect back to login
            # print("Autentificare nereușită!", file=sys.stderr)
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"]:
            return redirect(url_for('welcome'))
        else:
            print("Autentificare nereușită4!", file=sys.stderr)
            return redirect(url_for('login'))


api_key = "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"

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="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",
)


def get_completion(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    # print(response, file=sys.stderr)
    return response.choices[0].message.content


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response = get_completion(userText)
    # return str(bot.get_response(userText))
    return response

@app.route("/validate_identity", methods=["POST", "GET"])
def validate_identity():
    if request.method == "POST":
        try:
            image_data = request.form.get("image_data")

            save_base64_image(image_data, file_name='static/input_face.jpg')


            if compare_faces("static/input_face.jpg", "static/face.jpg"):
                #modificare
                return redirect(url_for('see_download_files'))

            else:
                return redirect(url_for('welcome'))

        except:
            return redirect(url_for('welcome'))

@app.route("/see_download_files")
def see_download_files():
    return render_template("download.html")

# Route to trigger the redirect to the root URL
@app.route('/redirect_to_root')
def redirect_to_root():
    # Redirect to the root URL using url_for() and redirect()
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
