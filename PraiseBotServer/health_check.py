def setup_health_check(flask_app, handler):

    @flask_app.route('/health', methods=['GET'])
    def health_check():
        print("Health check received.")
        return "OK", 200