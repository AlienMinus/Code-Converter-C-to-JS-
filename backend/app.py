from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import convert_c_to_js
import sys

app = Flask(__name__)
CORS(app)

@app.route("/convert", methods=["POST"])
def convert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        c_code = data.get("code", "")
        result = convert_c_to_js(c_code)

        # Handle both old & new converter outputs safely
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"js": result, "undeclared": []})

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
