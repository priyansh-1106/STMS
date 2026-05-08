from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit
import psycopg2, psycopg2.extras, pandas as pd, numpy as np

app = Flask(__name__)
app.secret_key = 'taskflow_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# ── DB connection string — change password if needed ──────────────────────────
DB = "host='localhost' dbname=task_manager_db user='postgres' password='Priyansh@2006' port=5432"

def get_conn():
    return psycopg2.connect(DB)

def get_analytics():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM tasks WHERE user_id = %s", conn, params=(session['user_id'],))
    conn.close()
    if df.empty:
        return {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0, 'completion_pct': 0.0}
    total = len(df)
    done  = int(np.sum(df['status'] == 'completed'))
    return {
        'total': total,
        'completed': done,
        'pending': int(np.sum(df['status'] == 'pending')),
        'in_progress': int(np.sum(df['status'] == 'in_progress')),
        'completion_pct': float(np.round(done / total * 100, 1)),
    }

# ── Create tables on startup ──────────────────────────────────────────────────
conn = get_conn()
cur  = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80)  UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(120) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low','medium','high')),
        status VARCHAR(20) DEFAULT 'pending' CHECK (status  IN ('pending','in_progress','completed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
cur.close()
conn.close()

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('dashboard' if 'user_id' in session else 'login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            conn = get_conn()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (request.form['username'].strip(), request.form['email'].strip(), request.form['password'])
            )
            conn.commit()
            cur.close(); conn.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Username or email already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (request.form['username'].strip(), request.form['password'])
        )
        user = cur.fetchone()
        cur.close(); conn.close()
        if user:
            session['user_id']  = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', analytics=get_analytics(), username=session['username'])

# ── Task API ──────────────────────────────────────────────────────────────────
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    for r in rows:
        r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M')
        r['updated_at'] = r['updated_at'].strftime('%Y-%m-%d %H:%M')
    return jsonify(rows)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    d    = request.get_json()
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO tasks (user_id, title, description, priority, status) VALUES (%s,%s,%s,%s,%s) RETURNING *",
        (session['user_id'], d['title'], d.get('description', ''), d.get('priority', 'medium'), d.get('status', 'pending'))
    )
    task = dict(cur.fetchone())
    conn.commit(); cur.close(); conn.close()
    task['created_at'] = task['created_at'].strftime('%Y-%m-%d %H:%M')
    task['updated_at'] = task['updated_at'].strftime('%Y-%m-%d %H:%M')
    socketio.emit('task_update', {'action': 'added', 'task': task, 'analytics': get_analytics()})
    return jsonify(task), 201

@app.route('/api/tasks/<int:tid>', methods=['PUT'])
def update_task(tid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    d    = request.get_json()
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """UPDATE tasks SET title=%s, description=%s, priority=%s, status=%s, updated_at=CURRENT_TIMESTAMP
           WHERE id=%s AND user_id=%s RETURNING *""",
        (d['title'], d.get('description', ''), d['priority'], d['status'], tid, session['user_id'])
    )
    task = dict(cur.fetchone())
    conn.commit(); cur.close(); conn.close()
    task['created_at'] = task['created_at'].strftime('%Y-%m-%d %H:%M')
    task['updated_at'] = task['updated_at'].strftime('%Y-%m-%d %H:%M')
    socketio.emit('task_update', {'action': 'updated', 'task': task, 'analytics': get_analytics()})
    return jsonify(task)

@app.route('/api/tasks/<int:tid>', methods=['DELETE'])
def delete_task(tid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (tid, session['user_id']))
    conn.commit(); cur.close(); conn.close()
    socketio.emit('task_update', {'action': 'deleted', 'task_id': tid, 'analytics': get_analytics()})
    return jsonify({'message': 'Task deleted'})

@app.route('/api/analytics')
def analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_analytics())

# ── WebSocket ─────────────────────────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'Live'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
