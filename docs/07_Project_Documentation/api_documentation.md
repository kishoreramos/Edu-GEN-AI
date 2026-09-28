# Phase 7: Project Documentation — API Reference Documentation
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. API Base Information
- **Base URL:** `http://127.0.0.1:8000`
- **Default Format:** JSON (`application/json`)
- **Interactive Documentation:** `http://127.0.0.1:8000/docs` (Swagger UI)
- **Alternative Documentation:** `http://127.0.0.1:8000/redoc` (ReDoc)

---

### 2. Authentication & Headers
- Currently, EduGenie runs as an open local educational service without bearer tokens.
- All JSON POST requests require standard headers:
  ```http
  Content-Type: application/json
  Accept: application/json
  ```

---

### 3. Programmatic Endpoints (Direct Baseline)

#### 3.1 Academic Q&A
- **Endpoint:** `POST /qa`
- **Alternative GET:** `GET /qa?question=<encoded_string>`
- **Request Body:**
  ```json
  {
    "question": "What is the time complexity of binary search?"
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "question": "What is the time complexity of binary search?",
    "answer": "The time complexity of binary search is O(log n)..."
  }
  ```
- **Error Codes:**
  - `400 Bad Request`: `{"detail": "Question cannot be empty"}`
  - `500 Internal Server Error`: `{"detail": "Failed to process Q&A request"}`

---

#### 3.2 Concept Explanation
- **Endpoint:** `POST /explain`
- **Request Body:**
  ```json
  {
    "topic": "Neural Networks"
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "topic": "Neural Networks",
    "explanation": "### What is a Neural Network?\nA neural network is a computational model inspired by the human brain...\n\n**Real-World Analogy:**\nThink of a factory assembly line..."
  }
  ```
- **Error Codes:**
  - `400 Bad Request`: `{"detail": "Topic cannot be empty"}`

---

#### 3.3 Quiz Generation
- **Endpoint:** `POST /quiz`
- **Request Body:**
  ```json
  {
    "text": "Mitochondria and Cellular Respiration"
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "quiz": [
      {
        "question": "What is often referred to as the powerhouse of the cell?",
        "options": ["Mitochondria", "Nucleus", "Ribosome", "Endoplasmic Reticulum"],
        "answer": "Mitochondria"
      },
      {
        "question": "Which molecule is the primary energy currency produced by mitochondria?",
        "options": ["ATP", "DNA", "RNA", "Glucose"],
        "answer": "ATP"
      },
      {
        "question": "During which process in mitochondria is oxygen used?",
        "options": ["Electron Transport Chain", "Glycolysis", "Fermentation", "Photosynthesis"],
        "answer": "Electron Transport Chain"
      }
    ]
  }
  ```

---

#### 3.4 Text Summarization
- **Endpoint:** `POST /summarize`
- **Request Body:**
  ```json
  {
    "text": "Long academic study passage..."
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "summary": "### Key Takeaways:\n- Point 1\n- Point 2\n\n### Summary in 3 Sentences:\nSentence 1. Sentence 2. Sentence 3."
  }
  ```

---

#### 3.5 Learning Path Recommendations
- **Endpoint:** `POST /learn/recommendations`
- **Alternative GET:** `GET /learn/recommendations?topic=<encoded_string>`
- **Request Body:**
  ```json
  {
    "topic": "Data Science"
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "topic": "Data Science",
    "recommendations": {
      "topic": "Data Science",
      "beginner": ["Python Basics", "Linear Algebra", "Pandas and NumPy"],
      "intermediate": ["Exploratory Data Analysis", "Scikit-Learn", "Regression and Classification"],
      "advanced": ["Deep Learning with PyTorch", "Model Deployment & MLOps", "Big Data Tools"]
    }
  }
  ```

---

### 4. Conversational Orchestration Endpoints

#### 4.1 Chat Dispatcher
- **Endpoint:** `POST /api/chat`
- **Request Body:**
  ```json
  {
    "message": "Can you explain that more simply?",
    "session_id": "session_f590c4a85c9d",
    "task_override": "auto"
  }
  ```
- **Response Schema (`200 OK`):**
  ```json
  {
    "success": true,
    "intent": "EXPLAIN",
    "reply": "Here is a simplified explanation...",
    "data": { ... },
    "session_id": "session_f590c4a85c9d",
    "topic": "Binary Search",
    "latency_ms": 840
  }
  ```

---

#### 4.2 Session Management
- **Create Session:** `POST /api/session`
  - Response: `{"success": true, "session_id": "session_123"}`
- **Get History:** `GET /api/session/{session_id}/history?limit=10`
  - Response: `{"session_id": "session_123", "messages": [...]}`
- **List Sessions:** `GET /api/sessions?limit=20`
  - Response: `{"sessions": [...]}`
