from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from converter import convert_c_to_js
import sys
import os

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app = Flask(__name__, static_folder=frontend_path, template_folder=frontend_path, static_url_path='')
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

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
    try:
        from waitress import serve
        print("Server running on http://127.0.0.1:5000")
        serve(app, host="0.0.0.0", port=5000)
    except ImportError:
        print("Waitress not installed. Using Flask dev server (pip install waitress)")
        app.run(debug=True)
