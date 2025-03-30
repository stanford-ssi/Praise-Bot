from flask import request, jsonify

def setup_health_check(flask_app, handler):

    @flask_app.route('/health', methods=['GET'])
    def health_check():
        print("Health check received.")

        if False:#TODO Implement database check
            return jsonify({
                "message": "No response from database."
            }), 503  # Return HTTP 200 if all nodes are online
        # If all nodes are online
        return 200