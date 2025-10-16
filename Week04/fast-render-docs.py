from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'  # chỉ để Swagger đọc file YAML, không có endpoint API nào

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Demo OpenAPI Only"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/openapi.yaml')
def send_yaml():
    return send_from_directory('.', 'openapi.yaml')

if __name__ == '__main__':
    app.run(debug=False)
