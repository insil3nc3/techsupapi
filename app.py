from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Настройки подключения к базе данных MySQL
db_config = {
    'host': 'sql7.freesqldatabase.com',
    'user': 'sql7744485',
    'password': 'TZ1mCUQlNt',
    'database': 'sql7744485'
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
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(tickets)

# 2. Добавить новый тикет
@app.route('/tickets', methods=['POST'])
def add_ticket():
    data = request.json
    customer_name = data.get('customer_name')
    issue_description = data.get('issue_description')
    status = data.get('status', 'open')

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tickets (customer_name, issue_description, status) VALUES (%s, %s, %s)",
                   (customer_name, issue_description, status))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Ticket added successfully"}), 201

# 3. Обновить статус тикета
@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.json
    status = data.get('status')

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE tickets SET status = %s, updated_at = NOW() WHERE id = %s", (status, ticket_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Ticket updated successfully"})

# 4. Удалить тикет
@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": f"Ticket with ID {ticket_id} deleted successfully"})

# 5. Поиск тикетов
@app.route('/tickets/search', methods=['GET'])
def search_tickets():
    search_text = request.args.get('query')
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tickets WHERE customer_name LIKE %s OR issue_description LIKE %s",
                   (f"%{search_text}%", f"%{search_text}%"))
    tickets = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(tickets)

# 6. Выборка тикетов по статусу
@app.route('/tickets/status/<string:status>', methods=['GET'])
def get_tickets_by_status(status):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tickets WHERE status = %s", (status,))
    tickets = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(tickets)

# 7. Получение статистики по статусам
@app.route('/tickets/statistics', methods=['GET'])
def get_ticket_statistics():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT status, COUNT(*) AS count FROM tickets GROUP BY status")
    stats = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
