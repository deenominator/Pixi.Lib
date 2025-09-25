// Chat Widget functionality
let chatVisible = false;
let currentDocumentId = null;

function toggleChat() {
    const chatWidget = document.getElementById('chatWidget');
    if (!chatWidget) return;
    
    chatVisible = !chatVisible;
    
    if (chatVisible) {
        chatWidget.classList.add('active');
        setTimeout(() => {
            const chatInput = document.getElementById('chatInput');
            if (chatInput) chatInput.focus();
        }, 100);
    } else {
        chatWidget.classList.remove('active');
    }
}

function suggestQuestion(question) {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = question;
        sendMessage();
    }
}

// Modal functionality
function showRaiseTicketModal() {
    const modal = document.getElementById('raiseTicketModal');
    if (modal) modal.classList.add('active');
    toggleChat();
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
    currentDocumentId = null;
}

// Document voting
async function voteDocument(docId, type) {
    try {
        const response = await fetch(`/api/documents/${docId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type: type })
        });
        
        const data = await response.json();
        
        // Update UI
        const card = document.querySelector(`[data-document-id="${docId}"]`);
        if (card) {
            const upvoteBtn = card.querySelector('.upvote .count');
            const downvoteBtn = card.querySelector('.downvote .count');
            
            if (upvoteBtn) upvoteBtn.textContent = data.upvotes;
            if (downvoteBtn) downvoteBtn.textContent = data.downvotes;
        }
    } catch (error) {
        console.error('Error voting:', error);
    }
}

// Ticket upvoting
async function upvoteTicket(ticketId) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}/upvote`, {
            method: 'POST'
        });
        
        const data = await response.json();
        location.reload();
    } catch (error) {
        console.error('Error upvoting ticket:', error);
    }
}

// Search and filter functionality
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const searchQuery = searchInput.value.trim();
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('search', searchQuery);
    window.location.href = currentUrl.toString();
}

function filterByGenre(genre) {
    const currentUrl = new URL(window.location.href);
    
    if (genre) {
        currentUrl.searchParams.set('genre', genre);
    } else {
        currentUrl.searchParams.delete('genre');
    }
    
    window.location.href = currentUrl.toString();
}

function toggleMoreGenres() {
    const moreGenres = document.getElementById('moreGenres');
    if (moreGenres) {
        const isVisible = moreGenres.style.display === 'block';
        moreGenres.style.display = isVisible ? 'none' : 'block';
    }
}

// FIXED: Document viewing with PDF + Discussion
async function openDocument(docId) {
    currentDocumentId = docId;
    
    try {
        const response = await fetch(`/api/documents/${docId}`);
        if (!response.ok) {
            throw new Error('Document not found');
        }
        
        const documentData = await response.json(); // Renamed to avoid conflict
        
        // CORRECTED: Use the global document object
        const titleElement = document.getElementById('modalDocumentTitle');
        const genreElement = document.getElementById('modalDocumentGenre');
        const dateElement = document.getElementById('modalDocumentDate');
        const pdfViewer = document.getElementById('pdfViewer');
        const modal = document.getElementById('documentModal');
        
        if (titleElement) titleElement.textContent = documentData.title;
        if (genreElement) genreElement.textContent = documentData.genre;
        if (dateElement) dateElement.textContent = documentData.upload_date;
        
        // Load PDF
        if (pdfViewer) {
            pdfViewer.src = `/static/uploads/${documentData.filename}`;
        }
        
        // Load discussions
        await loadDiscussions(docId);
        
        // Show modal
        if (modal) {
            modal.classList.add('active');
        }
    } catch (error) {
        console.error('Error loading document:', error);
        alert('Error loading document: ' + error.message);
    }
}

// Discussion functionality
async function loadDiscussions(docId) {
    try {
        const response = await fetch(`/api/discussions/${docId}`);
        if (!response.ok) return;
        
        const discussions = await response.json();
        
        const thread = document.getElementById('discussionThread');
        const commentCount = document.getElementById('commentCount');
        
        if (commentCount) {
            commentCount.textContent = `(${discussions.length} comments)`;
        }
        
        if (thread) {
            thread.innerHTML = '';
            
            if (discussions.length === 0) {
                thread.innerHTML = '<div class="no-comments"><p>No comments yet. Be the first to comment!</p></div>';
            } else {
                discussions.forEach(discussion => {
                    const commentHtml = `
                        <div class="comment" data-comment-id="${discussion.id}">
                            <div class="comment-header">
                                <span class="comment-author">${discussion.author}</span>
                                <span class="comment-date">${new Date(discussion.created_date).toLocaleDateString()}</span>
                            </div>
                            <div class="comment-content">
                                <p>${discussion.content}</p>
                            </div>
                            <div class="comment-actions">
                                <button class="comment-vote-btn" onclick="voteDiscussion(${discussion.id}, 'up')">
                                    <i class="fas fa-arrow-up"></i> ${discussion.upvotes || 0}
                                </button>
                                <button class="comment-vote-btn" onclick="voteDiscussion(${discussion.id}, 'down')">
                                    <i class="fas fa-arrow-down"></i> ${discussion.downvotes || 0}
                                </button>
                            </div>
                        </div>
                    `;
                    thread.innerHTML += commentHtml;
                });
            }
        }
    } catch (error) {
        console.error('Error loading discussions:', error);
    }
}

async function voteDiscussion(discussionId, type) {
    try {
        await fetch(`/api/discussions/${discussionId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type: type })
        });
        
        if (currentDocumentId) {
            await loadDiscussions(currentDocumentId);
        }
    } catch (error) {
        console.error('Error voting on discussion:', error);
    }
}

// Chat message sending
async function sendMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    addChatMessage(message, 'user');
    input.value = '';
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });
        
        const data = await response.json();
        addChatMessage(data.answer, 'bot');
    } catch (error) {
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addChatMessage(text, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Upload functionality
function handleFileSelect(file) {
    const uploadArea = document.getElementById('uploadArea');
    const uploadForm = document.getElementById('uploadForm');
    const fileName = document.getElementById('fileName');
    
    if (uploadArea) uploadArea.style.display = 'none';
    if (uploadForm) uploadForm.style.display = 'block';
    if (fileName) fileName.textContent = file.name;
    
    const titleInput = document.getElementById('documentTitle');
    if (titleInput) {
        const title = file.name.replace(/\.[^/.]+$/, "");
        titleInput.value = title;
    }
}

async function processUpload() {
    const fileInput = document.getElementById('fileInput');
    const titleInput = document.getElementById('documentTitle');
    const uploadForm = document.getElementById('uploadForm');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (!fileInput || !fileInput.files.length) {
        alert('Please select a file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('title', titleInput ? titleInput.value : 'Untitled Document');
    
    if (uploadForm) uploadForm.style.display = 'none';
    if (uploadProgress) uploadProgress.style.display = 'block';
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progressFill) progressFill.style.width = progress + '%';
        if (progress >= 90) clearInterval(progressInterval);
    }, 200);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        if (progressFill) progressFill.style.width = '100%';
        
        const result = await response.json();
        
        if (result.success) {
            showUploadResult(result);
        } else {
            if (progressText) progressText.textContent = 'Error: ' + result.error;
            setTimeout(resetUpload, 3000);
        }
    } catch (error) {
        clearInterval(progressInterval);
        if (progressText) progressText.textContent = 'Upload failed: ' + error.message;
    }
}

function showUploadResult(result) {
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadResult = document.getElementById('uploadResult');
    
    if (uploadProgress) uploadProgress.style.display = 'none';
    if (uploadResult) uploadResult.style.display = 'block';
    
    const resultTitle = document.getElementById('resultTitle');
    const resultGenre = document.getElementById('resultGenre');
    const resultSummary = document.getElementById('resultSummary');
    
    if (resultTitle) resultTitle.textContent = result.title;
    if (resultGenre) resultGenre.textContent = result.genre;
    if (resultSummary) resultSummary.textContent = result.summary;
}

function resetUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const uploadForm = document.getElementById('uploadForm');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadResult = document.getElementById('uploadResult');
    const fileInput = document.getElementById('fileInput');
    const titleInput = document.getElementById('documentTitle');
    const progressFill = document.getElementById('progressFill');
    
    if (uploadArea) uploadArea.style.display = 'block';
    if (uploadForm) uploadForm.style.display = 'none';
    if (uploadProgress) uploadProgress.style.display = 'none';
    if (uploadResult) uploadResult.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (titleInput) titleInput.value = '';
    if (progressFill) progressFill.style.width = '0%';
}

function cancelUpload() {
    resetUpload();
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    // Ticket form
    const ticketForm = document.getElementById('ticketForm');
    if (ticketForm) {
        ticketForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const titleInput = document.getElementById('ticketTitle');
            const descriptionInput = document.getElementById('ticketDescription');
            
            if (!titleInput || !descriptionInput) return;
            
            try {
                const response = await fetch('/api/tickets', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        title: titleInput.value, 
                        description: descriptionInput.value 
                    })
                });
                
                if (response.ok) {
                    closeModal('raiseTicketModal');
                    location.reload();
                }
            } catch (error) {
                console.error('Error creating ticket:', error);
            }
        });
    }
    
    // Comment form
    const commentForm = document.getElementById('commentForm');
    if (commentForm) {
        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const authorInput = document.getElementById('commentAuthor');
            const contentInput = document.getElementById('commentContent');
            
            if (!contentInput) return;
            
            try {
                const response = await fetch('/api/discussions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        document_id: currentDocumentId,
                        author: authorInput ? authorInput.value || 'Anonymous' : 'Anonymous',
                        content: contentInput.value
                    })
                });
                
                if (response.ok) {
                    contentInput.value = '';
                    if (currentDocumentId) await loadDiscussions(currentDocumentId);
                }
            } catch (error) {
                console.error('Error posting comment:', error);
            }
        });
    }
    
    // FAQ functionality
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            if (answer) answer.classList.toggle('active');
        });
    });
    
    // File upload handling
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length) handleFileSelect(e.target.files[0]);
        });
    }
    
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', e => e.preventDefault());
        uploadArea.addEventListener('dragleave', () => uploadArea.style.backgroundColor = '');
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '';
            if (e.dataTransfer.files.length) {
                const fileInput = document.getElementById('fileInput');
                if (fileInput) {
                    fileInput.files = e.dataTransfer.files;
                    handleFileSelect(e.dataTransfer.files[0]);
                }
            }
        });
    }
});