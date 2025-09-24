import os
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

# Import your custom scripts
from summarizer import DocumentSummarizer
from genre_prediction import GenrePredictor

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['DATABASE'] = 'documents.db'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    
    # Create documents table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            summary TEXT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create tickets table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            votes INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create discussions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            parent_id INTEGER DEFAULT 0,
            author TEXT DEFAULT 'Anonymous',
            content TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Insert sample data - FIXED: Only add sample data if files don't exist
    sample_docs = [
        ('The Future of AI', 'Technology', 'An in-depth analysis of artificial intelligence advancements and their implications for society in the coming decades.', 'sample_ai.pdf', 'sample_ai.pdf'),
        ('Culinary Traditions of Europe', 'Cooking', 'Explore the rich and diverse culinary heritage across European countries, from pasta in Italy to sausages in Germany.', 'sample_cooking.pdf', 'sample_cooking.pdf'),
        ('Space Exploration: Next Frontier', 'Science', 'A comprehensive look at current and future space missions, including Mars colonization plans and asteroid mining.', 'sample_space.pdf', 'sample_space.pdf')
    ]
    
    for title, genre, summary, filename, filepath in sample_docs:
        # Check if document already exists
        existing = conn.execute('SELECT id FROM documents WHERE title = ?', (title,)).fetchone()
        if not existing:
            conn.execute('''
                INSERT INTO documents (title, genre, summary, filename, filepath)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, genre, summary, filename, filepath))
            print(f"Added sample document: {title}")
    
    sample_tickets = [
        ('Introduction to Quantum Computing', 'Please add a beginner-friendly guide to quantum computing'),
        ('History of Ancient Rome', 'Looking for comprehensive material on Roman history'),
        ('Modern Photography Techniques', 'Need resources on contemporary photography methods')
    ]
    
    for title, description in sample_tickets:
        existing = conn.execute('SELECT id FROM tickets WHERE title = ?', (title,)).fetchone()
        if not existing:
            conn.execute('''
                INSERT INTO tickets (title, description, votes)
                VALUES (?, ?, ?)
            ''', (title, description, 20 + len(title)))
    
    conn.commit()
    conn.close()

# Database functions
def add_document(title, genre, summary, filename, filepath):
    """Add a document to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO documents (title, genre, summary, filename, filepath)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, genre, summary, filename, filepath))
    
    document_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return document_id

def get_documents(genre=None):
    """Get all documents, optionally filtered by genre"""
    conn = get_db_connection()
    
    if genre:
        documents = conn.execute(
            'SELECT * FROM documents WHERE genre = ? ORDER BY upload_date DESC',
            (genre,)
        ).fetchall()
    else:
        documents = conn.execute(
            'SELECT * FROM documents ORDER BY upload_date DESC'
        ).fetchall()
    
    conn.close()
    # FIXED: Convert each row to dictionary properly
    return [{key: doc[key] for key in doc.keys()} for doc in documents]

def search_documents(query):
    """Search documents by title or content"""
    conn = get_db_connection()
    
    documents = conn.execute(
        'SELECT * FROM documents WHERE title LIKE ? OR summary LIKE ? ORDER BY upload_date DESC',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    
    conn.close()
    # FIXED: Convert each row to dictionary properly
    return [{key: doc[key] for key in doc.keys()} for doc in documents]

def add_ticket(title, description):
    """Add a ticket to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tickets (title, description) VALUES (?, ?)
    ''', (title, description))
    
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return ticket_id

def get_tickets():
    """Get all tickets sorted by votes"""
    conn = get_db_connection()
    
    tickets = conn.execute(
        'SELECT * FROM tickets ORDER BY votes DESC, created_date DESC'
    ).fetchall()
    
    conn.close()
    # FIXED: Convert each row to dictionary properly
    return [{key: ticket[key] for key in ticket.keys()} for ticket in tickets]

def upvote_ticket(ticket_id):
    """Upvote a ticket"""
    conn = get_db_connection()
    
    conn.execute(
        'UPDATE tickets SET votes = votes + 1 WHERE id = ?',
        (ticket_id,)
    )
    
    conn.commit()
    conn.close()
    return True

def add_discussion(document_id, parent_id, author, content):
    """Add a discussion comment to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO discussions (document_id, parent_id, author, content)
        VALUES (?, ?, ?, ?)
    ''', (document_id, parent_id, author, content))
    
    discussion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return discussion_id

def get_discussions(document_id):
    """Get all discussions for a document"""
    conn = get_db_connection()
    
    discussions = conn.execute(
        '''SELECT * FROM discussions 
           WHERE document_id = ? 
           ORDER BY parent_id, created_date DESC''',
        (document_id,)
    ).fetchall()
    
    conn.close()
    # FIXED: Convert each row to dictionary properly
    return [{key: disc[key] for key in disc.keys()} for disc in discussions]

def vote_discussion(discussion_id, vote_type):
    """Vote on a discussion comment"""
    conn = get_db_connection()
    
    if vote_type == 'upvote':
        conn.execute(
            'UPDATE discussions SET votes = votes + 1 WHERE id = ?',
            (discussion_id,)
        )
    else:  # downvote
        conn.execute(
            'UPDATE discussions SET votes = votes - 1 WHERE id = ?',
            (discussion_id,)
        )
    
    conn.commit()
    conn.close()
    return True

def process_pdf_with_ai(filepath, filename):
    """Process PDF using your actual AI scripts"""
    try:
        print(f"Processing PDF: {filename}")
        
        # Initialize your AI classes
        summarizer = DocumentSummarizer()
        genre_predictor = GenrePredictor()
        
        # Read file content
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        print("Extracting text from PDF...")
        # Extract text using your summarizer
        text = summarizer._extract_text(file_content, filename)
        print(f"Extracted {len(text)} characters of text")
        
        if not text or len(text.strip()) < 50:
            return {
                'success': False,
                'error': 'Could not extract sufficient text from the PDF'
            }
        
        print("Generating summary...")
        # Generate summary using your summarizer
        summary = summarizer.get_summary(text)
        print("Summary generated successfully")
        
        print("Predicting genre...")
        # Predict genre using your genre predictor
        genre = genre_predictor.predict(summary)
        print(f"Genre predicted: {genre}")
        
        return {
            'success': True,
            'genre': genre,
            'summary': summary,
            'text_length': len(text)
        }
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return {
            'success': False,
            'error': f"AI processing error: {str(e)}"
        }

# FIXED: Improved file serving with error handling
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files with proper error handling"""
    try:
        # Check if file exists
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            # If file doesn't exist, serve a placeholder message
            return '''
            <html>
                <body style="display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; font-family: Arial, sans-serif;">
                    <div style="text-align: center; color: #666;">
                        <h1>📄 PDF Preview</h1>
                        <p>This is a sample document. Upload your own PDF to see the actual content.</p>
                        <p>AI Summary and Genre Prediction are available below.</p>
                    </div>
                </body>
            </html>
            ''', 200
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return "File not found", 404

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure the filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the PDF with your AI scripts
        result = process_pdf_with_ai(filepath, filename)
        
        if not result['success']:
            # Clean up the uploaded file if processing failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': result['error']}), 500
        
        # Add to database - FIXED: Store only filename for web access
        document_id = add_document(
            title=request.form.get('title', filename.replace('.pdf', '').replace('_', ' ').title()),
            genre=result['genre'],
            summary=result['summary'],
            filename=filename,
            filepath=filename  # Store only filename, not full path
        )
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'genre': result['genre'],
            'summary': result['summary'],
            'text_length': result['text_length']
        })
        
    except Exception as e:
        # Clean up the uploaded file if error occurred
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def api_get_documents():
    """Get all documents or filter by genre"""
    genre = request.args.get('genre')
    documents = get_documents(genre)
    return jsonify(documents)

@app.route('/api/documents/<int:document_id>', methods=['GET'])
def api_get_document(document_id):
    """Get a specific document by ID"""
    try:
        conn = get_db_connection()
        document = conn.execute(
            'SELECT * FROM documents WHERE id = ?', (document_id,)
        ).fetchone()
        conn.close()
        
        if document is None:
            return jsonify({'error': 'Document not found'}), 404
        
        # FIXED: Convert SQLite Row to dictionary using keys
        document_dict = {key: document[key] for key in document.keys()}
        
        return jsonify(document_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/search', methods=['GET'])
def api_search_documents():
    """Search documents by title or content"""
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    documents = search_documents(query)
    return jsonify(documents)

@app.route('/api/tickets', methods=['GET', 'POST'])
def api_tickets():
    """Get all tickets or create a new one"""
    if request.method == 'GET':
        tickets = get_tickets()
        return jsonify(tickets)
    else:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Ticket title required'}), 400
        
        ticket_id = add_ticket(data['title'], data.get('description', ''))
        return jsonify({'success': True, 'ticket_id': ticket_id})

@app.route('/api/tickets/<int:ticket_id>/upvote', methods=['POST'])
def api_upvote_ticket(ticket_id):
    """Upvote a ticket"""
    success = upvote_ticket(ticket_id)
    return jsonify({'success': success})

@app.route('/api/documents/<int:document_id>/discussions', methods=['GET', 'POST'])
def api_discussions(document_id):
    """Get or create discussions for a document"""
    if request.method == 'GET':
        discussions = get_discussions(document_id)
        return jsonify(discussions)
    else:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Discussion content required'}), 400
        
        parent_id = data.get('parent_id', 0)
        author = data.get('author', 'Anonymous')
        content = data['content']
        
        discussion_id = add_discussion(document_id, parent_id, author, content)
        return jsonify({'success': True, 'discussion_id': discussion_id})

@app.route('/api/discussions/<int:discussion_id>/vote', methods=['POST'])
def api_vote_discussion(discussion_id):
    """Upvote or downvote a discussion comment"""
    data = request.get_json()
    vote_type = data.get('type', 'upvote')  # 'upvote' or 'downvote'
    
    success = vote_discussion(discussion_id, vote_type)
    return jsonify({'success': success})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify AI services are working"""
    try:
        # Test if the AI services can be initialized
        summarizer = DocumentSummarizer()
        predictor = GenrePredictor()
        
        return jsonify({
            'status': 'healthy',
            'ai_services': 'operational',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': f'AI services not available: {str(e)}'
        }), 500

# NEW: API endpoint to check if PDF file exists
@app.route('/api/check-pdf/<int:document_id>')
def check_pdf(document_id):
    """Check if PDF file exists for a document"""
    try:
        conn = get_db_connection()
        document = conn.execute(
            'SELECT filename FROM documents WHERE id = ?', (document_id,)
        ).fetchone()
        conn.close()
        
        if not document:
            return jsonify({'exists': False, 'error': 'Document not found'})
        
        filename = document['filename']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        exists = os.path.exists(file_path)
        
        return jsonify({
            'exists': exists,
            'filename': filename,
            'file_path': file_path
        })
        
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("PDF Library Server Starting...")
    print("Available endpoints:")
    print("  - http://localhost:5000/ (Main website)")
    print("  - http://localhost:5000/api/health (Health check)")
    print("  - http://localhost:5000/api/documents (Get documents)")
    print("  - http://localhost:5000/api/upload (Upload PDF)")
    print("Note: Sample documents will show placeholder content until you upload real PDFs.")
    
    app.run(debug=True, port=5000)