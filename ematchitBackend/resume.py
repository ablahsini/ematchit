from flask_cors import CORS,cross_origin
from flask_jwt_extended import (
    JWTManager,create_access_token, create_refresh_token, get_jwt_identity,
    verify_jwt_in_request, verify_jwt_refresh_token_in_request
)

from auth import (authenticate_user, deauthenticate_user,
                    refresh_authentication, get_authenticated_user,
                    auth_required, auth_refresh_required, AuthenticationError)
import os
import urllib.request
from flask import Flask, request, abort, make_response,redirect, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from extraction.extracter import extract_blocs
from export.format import write_cv
from database_client import insert_new_cv_for_user, get_inventory_for_user


#fapp = Flask(__name__)

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')


cors = CORS(app, resources={r"/*/*": {"origins": "*"}})
jwt = JWTManager(app)
app.config.from_json(os.path.join(os.getcwd(), 'config.json'))



ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx'])

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024






def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

@app.route('/inventory', methods=['POST'])
@cross_origin()
def get_all_cvs():
    username = request.json.get('username', None)
    cvs = get_inventory_for_user(username)
    return make_response(jsonify({"files": cvs}))

@app.route('/export', methods=['POST'])
@cross_origin()
def export_categories():
    print('printing request values : ')
    req_data = request.get_json()
    filename = write_cv(req_data)
    directory = os.path.join(os.getcwd(), app.config['GENERATE_FOLDER'])
    return send_from_directory(directory=directory, filename=filename, as_attachment=True)

@app.route('/process', methods=['POST'])
@cross_origin()
def upload_file():
    print ("in post process")
    if 'file' not in request.files and 'username' not in request.form:
        resp = jsonify({'message' : 'No file part or username in the request'})
        resp.status_code = 400
        print(resp)
        return resp
    file = request.files['file']
    username = request.form['username']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        print(resp)
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        insert_new_cv_for_user(username, filename)
        blocs = extract_blocs(filepath, get_extension(filename))
        message = {
            'message': 'OK',
            'blocs': blocs
        }
        resp = jsonify(message)
        resp.status_code = 201

        return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, docx, doc'})
        resp.status_code = 400
        print(resp)
        return resp

@app.route('/auth/login', methods=['POST'])
def login_api():
    """
    Login user
    """
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        access_token, refresh_token = authenticate_user(username, password)
        return make_response(jsonify({
            'accessToken': access_token,
            'refreshToken': refresh_token
        }))
    except AuthenticationError as error:
        print(error.msg)
        app.logger.error('authentication error: %s', error)
        abort(403)

@app.route('/auth/info', methods=['GET'])
@auth_required
def login_info_api():
    """
    Get informaiton about currently logged in user
    """
    try:
        user = get_authenticated_user()
        return make_response(jsonify({
            'username': user['username'],
            'enabled': user['enabled'],
            'isAdmin': user['admin']
        }))
    except AuthenticationError as error:
        app.logger.error('authentication error: %s', error)
        abort(403)

@app.route('/auth/logout', methods=['POST'])
@auth_refresh_required
def logout_api():
    """
    Log user out
    """
    deauthenticate_user()
    return make_response()


@app.route('/auth/refresh', methods=['POST'])
@auth_refresh_required
def refresh_api():
    """
    Get a fresh access token from a valid refresh token
    """
    try:
        access_token = refresh_authentication()
        return make_response(jsonify({
            'accessToken': access_token
        }))
    except AuthenticationError as error:
        app.logger.error('authentication error %s', error)
        abort(403)

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html') # Return index.html


if __name__ == '__main__':
    app.run()
    #app.run(debug=True)
