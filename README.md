# Pixi.Lib - AI-Powered Document Management System
## Overview

- A web application designed for managing and analyzing PDF documents.

- Automatically classifies and summarizes uploaded PDFs using artificial intelligence.

- Allows users to browse the document library by genre and perform searches.

- Features an integrated system for community-driven discussions and document requests.

---

## Files description

- **app.py:** The main Flask application with all routes, database operations, and API endpoints.

- **summarizer.py:** Module for PDF text extraction and AI-powered summarization.

- **genre_prediction.py:** Module for AI-powered genre classification.

- **index.html:** Single-page frontend file with all UI components and client-side logic.

- **.env:** File for storing environment variables (API keys).

- **uploads/:** Directory where uploaded PDF files are stored.

---

### Architecture Overview for Chatbot

```Text
User input
    │
    ▼                           
[Query Embedding]                
    │                            
    ▼                            
[Semantic Search]    
    │                            
    ▼                            
[Build Gemini Prompt with Context]
    │
    ▼
[Gemini 1.5 Flash Response]
    │
    ▼
[Log to Session File]
    │
    ▼
[Feedback Prompt (manual or Gemini-generated)]
```

---

## System Workflow

### Document Processing Flow

-- **Upload:** User uploads a PDF via the drag-and-drop interface or file browser.

-- **Validation:** Server validates file format (PDF) and size.

-- **Text Extraction:** PyMuPDF library extracts text content.

-- **AI Analysis:** Text is sent to Gemini AI for genre prediction and summarization.

-- **Database Storage:** Metadata and file path are saved to the SQLite database.

-- **Display:** The document becomes available in the library.

### AI Processing Chain
```Text
[PDF File]
    │
    ▼
[Text Extraction] 
    │
    ▼
[Genre Prediction ]
    │
    ▼
[Summary Generation] 
    │
    ▼
[Database Storage]
```
---
## Key Components & Technologies

-- **Framework:** Vanilla JavaScript (ES6+)

-- **Styling:** Pure CSS with CSS Grid and Flexbox for responsive layouts

-- **Framework:** Flask (Python)

-- **Database:** SQLite with the sqlite3 module

-- **File Handling:** Werkzeug for secure file uploads

-- **PDF Processing:** PyMuPDF (fitz)

-- **AI Integration:** Google Generative AI (Gemini 1.5 Flash)

---

## Required Files to Run the System

- Python 3.7+

- A valid Google Gemini API key

---
## Features

### 1. AI-Powered Document Processing
-- Automatic Genre Prediction: Leverages AI to analyze PDF content and classify documents into over 28 distinct genres.

-- Automated Content Summarization: Generates detailed and contextually relevant summaries using the Gemini AI model.

-- PDF Text Extraction: Efficiently extracts text from uploaded PDF documents for processing.

-- Chunk Processing: Intelligently segments large documents into manageable chunks to handle extensive texts.

#### 2. Document Upload System
-- Drag & Drop Interface: A modern interface for uploading files with clear visual feedback.

-- File Validation: Enforces validation for PDF format and file size (16MB maximum).

-- Automated Processing: AI analysis is initiated immediately upon successful file upload.

-- Real-time Progress Indication: Provides users with visual feedback during the AI analysis stage.

-- Title Generation: Automatically generates a document title from the source filename.

### 3. Document Exploration and Search
-- Genre-Based Filtering: Allows users to browse the document library by specific categories.

-- Search Functionality: A robust search feature to find documents by title or keywords with their summary.

-- Document Grid View: Presents documents in a visually organized grid of cards, each displaying genre, title, and summary.

### 4. Document Reading and Interaction
-- Full-screen Reading Mode: Offers a distraction-free reading experience with a discussion sidebar.

-- Metadata Display: Clearly presents key document information, including genre, summary, and upload date.

### 5. Interactive Discussion and Community System
-- Threaded Comments: Supports nested discussion threads for organized conversations.

-- Voting Mechanism: Allows users to upvote or downvote comments and threads.

-- Community Ticket System: Users can submit and vote on requests for specific documents.

### 6. User Interface and Experience
-- AI Chat Assistant: A floating chat widget provides quick access to help and system actions.

-- Comprehensive UI Elements: Includes an expandable FAQ, contact information, and various visual feedback mechanisms.

---
## Current Status

These modules have been implemented and tested but features like a study buddy and integrated pomodoro system has not been integrated on the main platform workflow due to time limitations.
---
## Future Enhancements

-- User Authentication
-- Implement AI-driven routing of document requests to relevant subject matter experts.
-- Perform sentiment analysis on discussion threads to gauge community feedback.
-- Multi-language Support

---
## Summary

Pixi.Lib is an AI-powered document management system that automatically classifies and summarizes PDFs. It also includes tools for community collaboration, such as discussions and document requests.

---


