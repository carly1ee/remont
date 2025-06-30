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

# Инициализация расширений
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
DatabaseManager.initialize(config)

# Регистрация блюпринтов
app.register_blueprint(main_blueprint)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)