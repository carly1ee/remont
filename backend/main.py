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


CORS(app, origins=["http://localhost:4200"])

jwt = JWTManager(app)
DatabaseManager.initialize(config)

# Регистрация блюпринтов
app.register_blueprint(main_blueprint)

@app.route('/')
def root():
    return 'Backend работает должным образом.'



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)