# Phase 3: Project Design Phase — API Design & Specification
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. API Overview
EduGenie provides a standards-compliant RESTful API built on **FastAPI** with auto-generated OpenAPI documentation available at `/docs` and `/redoc`. The system features dual interfaces:
1. **Documented Baseline Direct Endpoints:** Programmatic, direct access to the five core educational modules.
2. **Conversational Orchestration Endpoints:** Session-aware, intent-classified multi-turn learning endpoints.

---

### 2. Documented Direct Endpoints (Original Baseline)

#### 2.1 Academic Q&A
- **Route:** `POST /qa` *(Also supports `GET /qa?question=<string>` for backwards compatibility)*
- **Request Body (`POST`):**
  ```json
  {
    "question": "What is polymorphism in Java?"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "question": "What is polymorphism in Java?",
    "answer": "Polymorphism in Java is a core Object-Oriented Programming (OOP) concept that allows objects of different classes to be treated as objects of a common superclass..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: `{"detail": "Question cannot be empty"}`
  - `500 Internal Server Error`: `{"detail": "Failed to process Q&A request"}`

---

#### 2.2 Concept Explanation
- **Route:** `POST /explain`
- **Request Body:**
  ```json
  {
    "topic": "Recursion in Computer Science"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "topic": "Recursion in Computer Science",
    "explanation": "### What is Recursion?\nRecursion is a programming technique where a function solves a problem by calling a smaller instance of itself...\n\n**Real-World Analogy:**\nThink of Russian nesting dolls (Matryoshka)..."
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: `{"detail": "Topic cannot be empty"}`

---

#### 2.3 Multiple-Choice Quiz Generation
- **Route:** `POST /quiz`
- **Request Body:**
  ```json
  {
    "text": "Photosynthesis"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "quiz": [
      {
        "question": "What is the primary pigment responsible for absorbing sunlight in plants?",
        "options": ["Chlorophyll", "Carotenoid", "Anthocyanin", "Hemoglobin"],
        "answer": "Chlorophyll"
      },
      {
        "question": "Which gas is absorbed by plants during photosynthesis?",
        "options": ["Carbon Dioxide", "Oxygen", "Nitrogen", "Argon"],
        "answer": "Carbon Dioxide"
      },
      {
        "question": "What is the primary sugar produced during photosynthesis?",
        "options": ["Glucose", "Sucrose", "Lactose", "Fructose"],
        "answer": "Glucose"
      }
    ]
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: `{"detail": "Input text or topic cannot be empty"}`

---

#### 2.4 Text Summarization
- **Route:** `POST /summarize`
- **Request Body:**
  ```json
  {
    "text": "The Industrial Revolution was a period of global transition of the human economy towards more widespread, efficient and stable manufacturing processes..."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "summary": "### Key Takeaways:\n- Shifted human labor to mechanized factory production.\n- Fueled urbanization and rapid technological innovation.\n- Transformed global trade, economics, and labor structures.\n\n### Summary in 3 Sentences:\nThe Industrial Revolution marked a pivotal shift from agrarian economies to mechanized industrial production. It fundamentally reshaped social structures, driving urbanization and global commerce. The technological advancements laid the foundation for modern manufacturing."
  }
  ```

---

#### 2.5 Learning Path Recommendations
- **Route:** `POST /learn/recommendations` *(Also supports `GET /learn/recommendations?topic=<string>`)*
- **Request Body (`POST`):**
  ```json
  {
    "topic": "Python Programming"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "topic": "Python Programming",
    "recommendations": {
      "topic": "Python Programming",
      "beginner": [
        "Variables, Data Types, and Operators",
        "Control Flow (if-else, loops)",
        "Functions and Scope"
      ],
      "intermediate": [
        "Object-Oriented Programming (Classes & Inheritance)",
        "File I/O, Error Handling, and Modules",
        "List Comprehensions and Generators"
      ],
      "advanced": [
        "Decorators, Context Managers, and Metaclasses",
        "Asynchronous Programming with asyncio",
        "Performance Profiling and Packaging"
      ]
    }
  }
  ```

---

### 3. Conversational Orchestrator API (Enhanced)

#### 3.1 Unified Conversational Chat
- **Route:** `POST /api/chat`
- **Request Body:**
  ```json
  {
    "message": "Can you quiz me on sorting algorithms?",
    "session_id": "session_f590c4a85c9d",
    "task_override": "auto"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "intent": "QUIZ",
    "reply": "Here is a 3-question quiz on sorting algorithms to test your knowledge!",
    "data": {
      "quiz": [ ... ]
    },
    "session_id": "session_f590c4a85c9d",
    "topic": "Sorting Algorithms",
    "latency_ms": 1120
  }
  ```

---

#### 3.2 Session Management Endpoints
- **Create Session (`POST /api/session`):**
  - Response: `{"success": true, "session_id": "session_a8b29f01c3"}`
- **Get Session History (`GET /api/session/{session_id}/history?limit=10`):**
  - Response: `{"session_id": "session_a8b29f01c3", "messages": [...]}`
- **List Recent Sessions (`GET /api/sessions?limit=20`):**
  - Response: `{"sessions": [{"session_id": "...", "title": "...", "updated_at": "..."}]}`
