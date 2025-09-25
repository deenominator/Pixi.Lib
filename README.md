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
[Build Gemini Prompt with Context and emotion]
    │
    ▼
[Gemini 1.5 Flash Response]
    │
    ▼
[Log to Session File]
    │
    ▼
[Feedback Prompt (Gemini-generated)]
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

<img width="1348" height="598" alt="image" src="https://github.com/user-attachments/assets/865e43ca-91ff-4054-bcaf-4979af4548e3" />
<img width="1351" height="602" alt="image" src="https://github.com/user-attachments/assets/e20d6cd2-c16d-4acb-9ac0-249c4e838e3b" />
<img width="1350" height="606" alt="image" src="https://github.com/user-attachments/assets/a1e0918c-244b-4fcb-b9b1-7505f64a7419" />
<img width="1365" height="605" alt="image" src="https://github.com/user-attachments/assets/1faf9992-d047-4730-830e-79aec2bb438a" />
<img width="1365" height="606" alt="image" src="https://github.com/user-attachments/assets/2b8ec097-431d-46e2-9c62-758fb92f4a14" />
<img width="1347" height="608" alt="image" src="https://github.com/user-attachments/assets/d34ada34-b858-481a-9df2-6db2fa6cc2a5" />
<img width="367" height="574" alt="image" src="https://github.com/user-attachments/assets/476c9f11-41ae-446f-87ce-7a7d488f0310"  />
<img width="1365" height="609" alt="image" src="https://github.com/user-attachments/assets/60780a50-3c63-45e1-8577-2d18f265a860" />
<img width="1346" height="605" alt="image" src="https://github.com/user-attachments/assets/ae4abc42-9bda-4dfa-a15d-c66a1aa41d4d" />

<img width="1350" height="613" alt="image" src="https://github.com/user-attachments/assets/3b480e2c-e825-4985-95f5-68ab018f2966" />
<img width="1352" height="609" alt="image" src="https://github.com/user-attachments/assets/17994514-e9c7-4533-9386-5035bfda708f" />
<img width="1352" height="601" alt="image" src="https://github.com/user-attachments/assets/77bda796-cd98-4678-8e47-eaca50242eae" />












---
## Current Status

- These modules have been implemented and tested but features like a study buddy and integrated pomodoro system has not been integrated on the main platform workflow due to time limitations.
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


