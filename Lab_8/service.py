from node_setup.node import RESTNode
from models.scooter import ElectroScooter
from models.database import db

from flask import Flask, request, jsonify
import requests
import time
import random
import sys

service_info = {
    "host" : "127.0.0.1",
    "port" : int(sys.argv[1])
}

time.sleep(random.randint(1, 3))
# node = RAFTFactory(service_info).create_server()
node = RESTNode(False)
node.to_string()

db_name = 'scooter'
# if not node.leader:
#     db_name += str(random.randint(1, 3))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}.db'
db.init_app(app)


@app.route('/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
    
    if scooter is not None:
        return jsonify({
        "id": scooter.id,
        "name": scooter.name,
        "battery_level": scooter.battery_level
        }), 200
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404
    

@app.route('/electro-scooters', methods=['GET'])
def get_electro_scooters():
    scooters = ElectroScooter.query.all()
    response = {}
    response["scooters"] = []
    
    if len(scooters) != 0:
        for scooter in scooters:
            response["scooters"].append({
                                "id": scooter.id,
                                "name": scooter.name,
                                "battery_level": scooter.battery_level
                                })
        return jsonify(response), 200
    
    else:
        return jsonify({"error": "No Electro Scooters in the database"}), 404


@app.route('/electro-scooters', methods=['POST'])
def create_electro_scooter():
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message" : "Access denied!"
        }, 403
    else:
        try:
            data = request.get_json()
            name = data['name']
            battery_level = data['battery_level']
            electro_scooter = ElectroScooter(name=name, battery_level=battery_level)

            db.session.add(electro_scooter)
            db.session.commit()

            if node.leader:
                for follower in node.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/electro-scooters",
                                    json = request.json,
                                    headers = {"Token" : "Leader"})
            
            return jsonify({"message": "Electro Scooter created successfully"}), 201
        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400
    

@app.route('/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message" : "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                data = request.get_json()
        
                scooter.name = data.get('name', scooter.name)
                scooter.battery_level = data.get('battery_level', scooter.battery_level)

                db.session.commit()

                if node.leader:
                    for follower in node.followers:
                        requests.put(f"http://{follower['host']}:{follower['port']}/electro-scooters",
                                        json = request.json,
                                        headers = {"Token" : "Leader"})

                return jsonify({"message": "Electro Scooter updated successfully"}), 200
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    

@app.route('/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message" : "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                password = request.headers.get('Delete-Password')
            
                if password == 'confirm_deletion':
                    db.session.delete(scooter)
                    db.session.commit()

                    if node.leader:
                        for follower in node.followers:
                            requests.delete(f"http://{follower['host']}:{follower['port']}/electro-scooters",
                                            json = request.json,
                                            headers = {"Token" : "Leader"})

                    return jsonify({"message": "Electro Scooter deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(
        host=service_info["host"],
        port=service_info["port"]
    )