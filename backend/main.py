from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Settings
from db_manager import DatabaseManager
from api import main_blueprint

config = Settings()

app = Flask(__name__)

# Конфигурация
app.config['JWT_SECRET_KEY'] = config.SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Для теста

# CORS configuration
cors_origins = ['http://localhost:4200', 'http://127.0.0.1:4200']
CORS(app,
    origins=cors_origins,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
    expose_headers=['Content-Type', 'Authorization'],
    supports_credentials=True)

jwt = JWTManager(app)
DatabaseManager.initialize(config)

# Регистрация блюпринтов
app.register_blueprint(main_blueprint)

@app.route('/')
def root():
    return 'Backend работает должным образом.'



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
