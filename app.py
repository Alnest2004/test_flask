from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Integer, nullable=False)

    def __init__(self, username, balance):
        self.username = username
        self.balance = balance

    @staticmethod
    def add_user(username, balance):
        user = User(username=username, balance=balance)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_balance(username, new_balance):
        user = User.query.filter_by(username=username).first()
        if user:
            user.balance = new_balance
            db.session.commit()

    @staticmethod
    def delete_user(username):
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()

# Создание таблицы в базе данных
with app.app_context():
    db.create_all()
    if not User.query.all():
        # Создаем 5 пользователей с балансом от 5000 до 15000
        for i in range(1, 6):
            username = f"user{i}"
            balance = random.randint(5000, 15000)
            User.add_user(username, balance)


# Функция для получения текущей погоды
def fetch_weather(city):
    api_key = '4c286fc34326ad03f341e809a6e15ea0'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temperature = data['main']['temp']
            return temperature
        else:
            print(f"Failed to fetch weather data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/add_user')
def add_user_route():
    username = "new_user"
    balance = 10000
    User.add_user(username, balance)
    return "User added successfully!"

@app.route('/update_balance')
def update_balance_route():
    username = request.args.get('username')
    city = request.args.get('city')
    temperature = fetch_weather(city)
    if temperature is not None:
        user = User.query.filter_by(username=username).first()
        if user:
            new_balance = user.balance + temperature
            if new_balance >= 0:  # Проверка, чтобы баланс не стал отрицательным
                user.balance = new_balance
                db.session.commit()  # Применяем изменения в реальном времени
                return f"Balance updated successfully! New balance: {new_balance}"
            else:
                return f"Failed to update balance. Balance cannot be negative."
        else:
            return f"User {username} not found"
    else:
        return f"Failed to fetch current temperature for {city}"

@app.route('/delete_user')
def delete_user_route():
    username = "existing_user"
    User.delete_user(username)
    return "User deleted successfully!"

# Маршрут для отображения текущей температуры для указанного города
@app.route('/weather/<city>')
def get_weather(city):
    temperature = fetch_weather(city)
    if temperature is not None:
        return f"The current temperature in {city} is {temperature}°C"
    else:
        return f"Failed to fetch current temperature for {city}"

if __name__ == '__main__':
    app.run(debug=True)
