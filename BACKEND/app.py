from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename
from summarizer import DocumentSummarizer
from genre_prediction import GenrePredictor
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pixi-lib-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DATABASE'] = 'pixi_lib.db'

API_KEY = "AIzaSyAy71Fkj8JzXv2raThpcEYIQm97rpvgGRg"
summarizer = DocumentSummarizer(API_KEY)
genre_predictor = GenrePredictor(API_KEY)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            summary TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            parent_id INTEGER DEFAULT NULL,
            author TEXT DEFAULT 'Anonymous',
            content TEXT NOT NULL,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/read')
def read_page():
    genre_filter = request.args.get('genre', '')
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    
    query = 'SELECT * FROM documents WHERE 1=1'
    params = []
    
    if genre_filter:
        query += ' AND genre = ?'
        params.append(genre_filter)
    
    if search_query:
        query += ' AND (title LIKE ? OR summary LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    query += ' ORDER BY upvotes DESC'
    documents = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('read.html', documents=documents, genre_filter=genre_filter, search_query=search_query)

@app.route('/write')
def write_page():
    return render_template('write.html')

@app.route('/tickets')
def tickets_page():
    conn = get_db_connection()
    tickets = conn.execute('SELECT * FROM tickets ORDER BY votes DESC').fetchall()
    conn.close()
    return render_template('tickets.html', tickets=tickets)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    title = request.form.get('title', 'Untitled Document')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            with open(filepath, "rb") as f:
                file_content = f.read()
            text = summarizer._extract_text(file_content, filename)
            summary = summarizer.get_summary(text)
            genre = genre_predictor.predict(summary)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO documents (title, genre, summary, filename, filepath) VALUES (?, ?, ?, ?, ?)',
                (title, genre, summary, filename, filepath)
            )
            document_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'document_id': document_id,
                'title': title,
                'genre': genre,
                'summary': summary,
                'filename': filename
            })
            
        except Exception as e:
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload PDF or TXT files.'}), 400

@app.route('/api/documents/<int:doc_id>')
def api_get_document(doc_id):
    conn = get_db_connection()
    document = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    
    if document is None:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(dict(document))

@app.route('/api/documents/<int:doc_id>/vote', methods=['POST'])
def api_vote_document(doc_id):
    vote_type = request.json.get('type')
    
    conn = get_db_connection()
    
    if vote_type == 'up':
        conn.execute('UPDATE documents SET upvotes = upvotes + 1 WHERE id = ?', (doc_id,))
    elif vote_type == 'down':
        conn.execute('UPDATE documents SET downvotes = downvotes + 1 WHERE id = ?', (doc_id,))
    
    conn.commit()
    document = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    
    return jsonify({
        'upvotes': document['upvotes'],
        'downvotes': document['downvotes']
    })

@app.route('/api/tickets', methods=['GET', 'POST'])
def api_tickets():
    if request.method == 'POST':
        title = request.json.get('title')
        description = request.json.get('description')
        
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tickets (title, description) VALUES (?, ?)',
            (title, description)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    else:
        conn = get_db_connection()
        tickets = conn.execute('SELECT * FROM tickets ORDER BY votes DESC').fetchall()
        conn.close()
        return jsonify([dict(ticket) for ticket in tickets])

@app.route('/api/tickets/<int:ticket_id>/upvote', methods=['POST'])
def api_upvote_ticket(ticket_id):
    conn = get_db_connection()
    conn.execute('UPDATE tickets SET votes = votes + 1 WHERE id = ?', (ticket_id,))
    conn.commit()
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    conn.close()
    
    return jsonify({'votes': ticket['votes']})

@app.route('/api/discussions', methods=['POST'])
def api_create_discussion():
    document_id = request.json.get('document_id')
    parent_id = request.json.get('parent_id')
    author = request.json.get('author', 'Anonymous')
    content = request.json.get('content')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO discussions (document_id, parent_id, author, content) VALUES (?, ?, ?, ?)',
        (document_id, parent_id, author, content)
    )
    discussion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'discussion_id': discussion_id})

@app.route('/api/discussions/<int:doc_id>')
def api_get_discussions(doc_id):
    conn = get_db_connection()
    discussions = conn.execute(
        'SELECT * FROM discussions WHERE document_id = ? ORDER BY created_date',
        (doc_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(discussion) for discussion in discussions])

@app.route('/api/discussions/<int:discussion_id>/vote', methods=['POST'])
def api_vote_discussion(discussion_id):
    vote_type = request.json.get('type')
    
    conn = get_db_connection()
    
    if vote_type == 'up':
        conn.execute('UPDATE discussions SET upvotes = upvotes + 1 WHERE id = ?', (discussion_id,))
    elif vote_type == 'down':
        conn.execute('UPDATE discussions SET downvotes = downvotes + 1 WHERE id = ?', (discussion_id,))
    
    conn.commit()
    discussion = conn.execute('SELECT * FROM discussions WHERE id = ?', (discussion_id,)).fetchone()
    conn.close()
    
    return jsonify({
        'upvotes': discussion['upvotes'],
        'downvotes': discussion['downvotes']
    })

@app.route('/api/ask', methods=['POST'])
def api_ask_question():
    data = request.get_json()
    question = data.get('question', '')
    
    try:
        response = requests.post(
            'https://iamshubhshrma-ankitapp.hf.space/ask',
            json={'question': question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({'answer': result.get('answer', 'No answer provided')})
        else:
            return jsonify({'answer': 'Sorry, I cannot answer that right now.'})
    
    except Exception as e:
        return jsonify({'answer': f'Error connecting to chatbot: {str(e)}'})

@app.route('/api/health')
def api_health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)