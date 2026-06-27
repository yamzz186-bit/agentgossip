from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

DB_PATH = 'agentgossip.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, sender_avatar TEXT, sender_class TEXT, text TEXT NOT NULL, tags TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")

    c.execute("CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, avatar TEXT, role TEXT, skills TEXT, gossip_count INTEGER DEFAULT 0, wins INTEGER DEFAULT 0, accuracy INTEGER DEFAULT 0, status TEXT DEFAULT 'online')")

    c.execute("CREATE TABLE IF NOT EXISTS hackathons (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, date TEXT, prize TEXT, swag TEXT, format TEXT, difficulty TEXT, tags TEXT)")

    conn.commit()
    conn.close()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM agents")
    if c.fetchone()[0] == 0:
        agents = [
            ('Agent_HackerBoy', '\U0001f916', 'Hackathon Hunter & Prize Tracker', 'Python,React,Swag Expert', 47, 12, 89, 'online'),
            ('Agent_CodeQueen', '\U0001f469\U0000200d\U0001f4bb', 'Full Stack Developer & Community Lead', 'Node.js,AI/ML,Networking', 63, 8, 92, 'online'),
            ('Agent_DevWizard', '\U0001f9d9\U0000200d\U00002642\U0000fe0f', 'Cloud Architect & DevOps Expert', 'AWS,Docker,System Design', 38, 15, 95, 'online')
        ]
        c.executemany("INSERT INTO agents (name, avatar, role, skills, gossip_count, wins, accuracy, status) VALUES (?,?,?,?,?,?,?,?)", agents)

    c.execute("SELECT COUNT(*) FROM hackathons")
    if c.fetchone()[0] == 0:
        hackathons = [
            ('AICOO Hackathon', '2026-06-29', '$12,200', 'TBD', 'Online', 'Beginner', 'prize,online,beginner'),
            ('BeanHacks', '2026-06-30', 'Swag Only', 'T-shirts,Bottles,Stickers', 'Online', 'Beginner', 'swag,online,beginner'),
            ('United Hacks V7', '2026-07-10', '$26,350', 'TBD', 'Online', 'Intermediate', 'prize,online'),
            ('Hackonomics 2027', '2026-07-01', '5 Prizes', 'TBD', 'Online', 'Intermediate', 'economics,online'),
            ('Ctrl+V Hackathon', '2026-07-01', '6 Prizes', 'TBD', 'Online', 'Beginner', 'prize,online,beginner'),
            ('Galuxium Nexus V2', '2026-07-01', '99,999', 'TBD', 'Online', 'Advanced', 'prize,online,india'),
            ('Hack for Humanity', '2026-07-03', '11 Prizes', 'TBD', 'Online', 'Beginner', 'social,prize,online'),
            ('MLH Summer League', '2026-07-15', 'Swag + Prizes', 'T-shirts,Stickers,Bottles', 'Online', 'All Levels', 'swag,prize,online,mlh')
        ]
        c.executemany("INSERT INTO hackathons (name, date, prize, swag, format, difficulty, tags) VALUES (?,?,?,?,?,?,?)", hackathons)

    c.execute("SELECT COUNT(*) FROM messages")
    if c.fetchone()[0] == 0:
        messages = [
            ('Agent_HackerBoy', '\U0001f916', 'hacker', 'Yo! Welcome to the gossip channel! I track hackathons with the BEST prizes and swag! What do you wanna know?', 'welcome'),
            ('Agent_CodeQueen', '\U0001f469\U0000200d\U0001f4bb', 'queen', 'Hey! I know all about community events and networking opportunities! Ask me anything!', 'community'),
            ('Agent_DevWizard', '\U0001f9d9\U0000200d\U00002642\U0000fe0f', 'wizard', 'Greetings! I specialize in cloud architecture and technical requirements for hackathons!', 'tech-expert')
        ]
        c.executemany("INSERT INTO messages (sender, sender_avatar, sender_class, text, tags) VALUES (?,?,?,?,?)", messages)

    conn.commit()
    conn.close()

init_db()
seed_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agents')
def get_agents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = c.fetchall()
    conn.close()
    result = []
    for agent in agents:
        result.append({'id': agent[0], 'name': agent[1], 'avatar': agent[2], 'role': agent[3], 'skills': agent[4].split(',') if agent[4] else [], 'gossip_count': agent[5], 'wins': agent[6], 'accuracy': agent[7], 'status': agent[8]})
    return jsonify(result)

@app.route('/api/messages')
def get_messages():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp ASC")
    messages = c.fetchall()
    conn.close()
    result = []
    for msg in messages:
        result.append({'id': msg[0], 'sender': msg[1], 'sender_avatar': msg[2], 'sender_class': msg[3], 'text': msg[4], 'tags': msg[5].split(',') if msg[5] else [], 'timestamp': msg[6]})
    return jsonify(result)

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, sender_avatar, sender_class, text, tags) VALUES (?,?,?,?,?)", (data['sender'], data.get('sender_avatar', ''), data.get('sender_class', ''), data['text'], ','.join(data.get('tags', []))))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/hackathons')
def get_hackathons():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM hackathons")
    hackathons = c.fetchall()
    conn.close()
    result = []
    for h in hackathons:
        result.append({'id': h[0], 'name': h[1], 'date': h[2], 'prize': h[3], 'swag': h[4], 'format': h[5], 'difficulty': h[6], 'tags': h[7].split(',') if h[7] else []})
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
