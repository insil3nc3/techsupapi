from flask import Flask, request, jsonify
import mysql.connector
import os  # Добавьте этот импорт
from mysql.connector import Error

app = Flask(__name__)

# Настройки подключения к базе данных MySQL
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Функция для создания подключения к базе данных
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# 1. Получить все тикеты
@app.route('/tickets', methods=['GET'])
def get_all_tickets():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(tickets)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 2. Добавить новый тикет
@app.route('/tickets', methods=['POST'])
def add_ticket():
    data = request.json
    customer_name = data.get('customer_name')
    issue_description = data.get('issue_description')
    status = data.get('status', 'open')

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO tickets (customer_name, issue_description, status) VALUES (%s, %s, %s)",
                       (customer_name, issue_description, status))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Ticket added successfully"}), 201
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 3. Обновить статус тикета
@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.json
    status = data.get('status')

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE tickets SET status = %s, updated_at = NOW() WHERE id = %s", (status, ticket_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Ticket updated successfully"})
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 4. Удалить тикет
@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": f"Ticket with ID {ticket_id} deleted successfully"})
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 5. Поиск тикетов
@app.route('/tickets/search', methods=['GET'])
def search_tickets():
    search_text = request.args.get('query')
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets WHERE customer_name LIKE %s OR issue_description LIKE %s",
                       (f"%{search_text}%", f"%{search_text}%"))
        tickets = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(tickets)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 6. Выборка тикетов по статусу
@app.route('/tickets/status/<string:status>', methods=['GET'])
def get_tickets_by_status(status):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets WHERE status = %s", (status,))
        tickets = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(tickets)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# 7. Получение статистики по статусам
@app.route('/tickets/statistics', methods=['GET'])
def get_ticket_statistics():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT status, COUNT(*) AS count FROM tickets GROUP BY status")
        stats = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(stats)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

# Запуск приложения Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Получаем порт из переменной окружения PORT
    app.run(host='0.0.0.0', port=port)        # Запуск на всех интерфейсах
