from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.grocerydb
collection = db.prices

# Utility function to convert ObjectId to string
def to_json(data):
    if isinstance(data, list):
        for item in data:
            item["_id"] = str(item["_id"])
    else:
        data["_id"] = str(data["_id"])
    return data

# Endpoint to update prices
@app.route('/update-prices', methods=['POST'])
def update_prices():
    data = request.json
    if 'prices' in data:
        for price in data['prices']:
            filter = {"Item": price["Item"], "Store": price["Store"]}
            update = {
                "$set": {
                    "Category": price["Category"],
                    "Price": price["Price"],
                    "Date": price["Date"]
                }
            }
            collection.update_one(filter, update, upsert=True)
        return jsonify({"message": "Prices updated successfully."}), 200
    else:
        return jsonify({"error": "Invalid data format."}), 400

# Endpoint to add a new item
@app.route('/add-item', methods=['POST'])
def add_item():
    data = request.json
    if data:
        result = collection.insert_one(data)
        return jsonify({"message": "Item added successfully.", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data format."}), 400

# Endpoint to fetch all items
@app.route('/get-items', methods=['GET'])
def get_items():
    items = list(collection.find({}, {'_id': 0}))
    return jsonify(items), 200

# Endpoint to fetch an item by ID
@app.route('/get-item/<item_id>', methods=['GET'])
def get_item(item_id):
    item = collection.find_one({"_id": ObjectId(item_id)})
    if item:
        return jsonify(to_json(item)), 200
    else:
        return jsonify({"error": "Item not found."}), 404

# Endpoint to update an item by ID
@app.route('/update-item/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    if data:
        filter = {"_id": ObjectId(item_id)}
        update = {"$set": data}
        result = collection.update_one(filter, update)
        if result.matched_count:
            return jsonify({"message": "Item updated successfully."}), 200
        else:
            return jsonify({"error": "Item not found."}), 404
    else:
        return jsonify({"error": "Invalid data format."}), 400

# Endpoint to delete an item by ID
@app.route('/delete-item/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    filter = {"_id": ObjectId(item_id)}
    result = collection.delete_one(filter)
    if result.deleted_count:
        return jsonify({"message": "Item deleted successfully."}), 200
    else:
        return jsonify({"error": "Item not found."}), 404

# Start the Flask server
if __name__ == '__main__':
    app.run(port=8000, debug=True)
