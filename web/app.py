"""
Registration of a user 0 token
Each user gets 10 tokens
Store a token on our database for 1 token
Retrieve a token from our database for 1 token 
"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import bcrypt
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]


class Register(Resource):
    def post(self):
        #step 1 is to get posted data by the user
        postedData = request.get_json()

        #Get the data
        username = postedData['username']
        password = postedData['password']
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), salt)

        #store the username and password into the database
        users.insert({
           "Username": username,
           "Password": hashed_pw,
           "Sentence": "",
           "Tokens": 6
        })

        retJson = {
          "status": 200,
          "msg": "You successfully sign up for the API"
        }

        return jsonify(retJson)


#verifyPw function
def verifyPw(username,password):
    hashed_pw = users.find({
     "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'),hashed_pw)== hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
      "Username": username
    })[0]["Tokens"]
    return tokens

#store Resource
class Store(Resource):
    def post(self):
        #step 1 get the posted data
        postedData = request.get_json()
        #step 2 read the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]
        #step 3 verify if the username and password match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
             "status": 302
            }
            return jsonify(retJson)

        #step 4 verify that user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
             "status": 301
            }
            return jsonify(retJson)
        #step 5 store the sentence, take one token and return 200
        users.update({
         "Username":username
        },{
         "$set":{
         "Sentence":sentence,
         "Tokens":num_tokens-1
         }
        })

        retJson = {
          "status": 200,
          "msg": "Sentence saved successful"
        }

        return jsonify(retJson)


class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        #step 3 verify if the username and password match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
             "status": 302
            }
            return jsonify(retJson)

        #step 4 verify that user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
             "status": 301
            }
            return jsonify(retJson)

        #Make the user pay
        users.update({
         "Username":username
        },{
         "$set":{
         "Tokens":num_tokens-1
         }
        })

        sentence = users.find({
          "Username": username,

        })[0]["Sentence"]

        retJson = {
         "status":200,
         "sentence": str(sentence)
        }
        return jsonify(retJson)


api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')



if __name__ == '__main__':
    app.run(host = '0.0.0.0')
