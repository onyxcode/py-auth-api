import bcrypt
import json
import pymongo
import sanic
from sanic.exceptions import abort
import os

PORT = 6969
if (os.getenv('PORT') != ""):
    PORT = os.getenv('PORT')

app = sanic.app.Sanic("Authentication")
with open("config.json") as config:
    config = json.load(config)
mongo = pymongo.MongoClient(config["MONGO_URL"])


def open_account(username, slt, hash):
    db = mongo.web_users
    db[f"{username}"].insert_one({"_id": "credentials",
                                  "salt": slt,
                                  "hashed": hash
                                  })


def change_password(username, request, new_password):
    db = mongo.web_users
    col_list = db.list_collection_names()
    new_password = new_password.encode('utf-8')
    if request.json['username'] in col_list:
        passwd = request.json['password'].encode('utf-8')
        user_doc = db[f"{request.json['username']}"].find_one({"_id": "credentials"})
        if bcrypt.checkpw(passwd, user_doc['hashed']):
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(new_password, salt)
            db[f"{username}"].update_one({"_id": "credentials"},{"$set":{
                                          "salt": salt,
                                          "hashed": hashed
                                          }}, True)
            return ({"Success": "PasswordChanged"})
        else:
            return ({"Error": "IncorrectPassword"})
    else:
        return ({"Error": "UserNotFound"})


@app.route('/v1/check-creds', methods=['POST'])
async def post_handler(request):
    db = mongo.web_users
    col_list = db.list_collection_names()
    if request.json['username'] in col_list:
        user_doc = db[f"{request.json['username']}"].find_one({"_id": "credentials"})
        passwd = request.json['password'].encode('utf-8')
        if bcrypt.checkpw(passwd, user_doc['hashed']):
            abort(200)
        else:
            abort(401)
    else:
        abort(401)


@app.route('/v1/create-user', methods=['POST'])
async def post_handler(request):
    db = mongo.web_users
    col_list = db.list_collection_names()
    passwd = request.json['password'].encode('utf-8')
    if request.json['username'] and request.json['password']:
        if request.json['username'] in col_list:
            abort(400)
        else:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passwd, salt)
            open_account(request.json['username'], salt, hashed)
            abort(201)
    else:
        abort(400)


@app.route('v1/update-password', methods=['POST'])
async def post_handler(request):
    if request.json['username'] and request.json['password'] and request.json['new_password']:
        change = change_password(request.json['username'], request, request.json['new_password'])
        if change == {"Success": "PasswordChanged"}:
            abort(200)
        elif change == {"Error": "IncorrectPassword"}:
            abort(401)
        elif change == {"Error": "UserNotFound"}:
            abort(400)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, workers=2)
