# This code creates an api that takes in a video file and returns the result of the video analysis

import os
import main
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process_videos', methods=['POST'])
def process_videos():
    try:
        data = request.get_json()
        directory = data.get('directory')
        rubric_path = data.get('rubric_path', "rubric.txt")

        if not directory:
            return jsonify({"error": "directory field is required"}), 400

        main.process_videos(directory, rubric_path)

        return jsonify({"message": "Videos processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
