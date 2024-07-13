"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def handle_hello():
    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = members
    return jsonify(response_body), 200


@app.route('/member/<int:id>', methods=['GET'])
def get_member(id):
    member = jackson_family.get_member(id)
    if member:
        return jsonify(member), 200
    else:
        return jsonify({"msg": f"Member with ID {id} not found"}), 404


@app.route('/member', methods=['POST'])
def new_member():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "Debes enviar informacion en el body"}), 400
    if "first_name" not in body:
        return jsonify({"msg": "El campo first_name es obligatorio"}), 400
    print(body)
    
    # Verificar si el usuario proporcionó un ID
    if "id" in body:
        new_member_data = {
            "id": body["id"],
            "first_name": body["first_name"],
            "last_name": jackson_family.last_name,
            "age": body["age"],
            "lucky_numbers": body["lucky_numbers"]
        }
    else:
        new_member_data = {
            "id": jackson_family._generateId(),
            "first_name": body["first_name"],
            "last_name": jackson_family.last_name,
            "age": body["age"],
            "lucky_numbers": body["lucky_numbers"]
        }


    jackson_family.add_member(new_member_data)
    return jsonify({"msg": "New member added"}), 200


@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member(id):
    result = jackson_family.delete_member(id)
    if result["msg"] == f"Member with ID {id} deleted":
        return jsonify({"done": True}), result["status_code"]
    else:
        return jsonify({"done": False}), result["status_code"]

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
