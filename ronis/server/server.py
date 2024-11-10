from flask import Flask, jsonify
from flask_cors import CORS

# app instance
app = Flask(__name__)
CORS(app)


@app.route("/api/home", methods=["GET"])
def return_home():
    return jsonify([
        { "Month": "January", "desktop": 186, "mobile": 80 },
        { "Month": "January", "desktop": 186, "mobile": 80 },
        { "Month": "January", "desktop": 186, "mobile": 20 },
        { "Month": "January", "desktop": 186, "mobile": 80 },
        { "Month": "January", "desktop": 186, "mobile": 50 }
    ])

@app.route("/api/test", methods=["GET"])
def return_test():
    return jsonify([
        { "Key": "Test", "Val": 72, "Val2": 20},
        { "Key": "Test2", "Val": 45, "Val2": 12},
        { "Key": "Test3", "Val": 23, "Val2": 32},
        { "Key": "Test4", "Val": 98, "Val2": 45},
        { "Key": "Test5", "Val": 65, "Val2": 65},
    ])

if __name__ == "__main__":
    app.run(debug = True, port=8080)