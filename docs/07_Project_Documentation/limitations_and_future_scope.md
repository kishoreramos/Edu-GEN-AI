# Phase 7: Project Documentation — Limitations & Future Scope
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Honest System Boundary Evaluation

While EduGenie has successfully achieved all five core document requirements and introduced modern conversational orchestration, it is important to clearly outline the current technical boundaries of the submission:

#### 1.1 Text-Only Ingestion Boundary
- **Current State:** EduGenie accepts student inputs via textual prompts or pasted notes.
- **Limitation:** Direct binary upload and parsing of complex academic PDFs, mathematical figures, slide presentations, or handwritten formula images is not yet supported.

#### 1.2 Synchronous Quiz Generation
- **Current State:** Quizzes are generated as complete 3-question sets in a single pass.
- **Limitation:** While interactive answer feedback is immediate, the system does not dynamically alter question difficulty in real time (e.g., computer adaptive testing) based on earlier questions within the same quiz set.

#### 1.3 Local Hugging Face Model Footprint
- **Current State:** EduGenie contains code to run `MBZUAI/LaMini-Flan-T5-783M` locally for concept explanations.
- **Limitation:** Running the local transformer requires ~3GB to 4GB of available RAM and PyTorch installation. On constrained hardware, local model loading is skipped, and the system relies entirely on Google Gemini.

#### 1.4 Single-User Local SQLite Scope
- **Current State:** Persistent conversational state uses an embedded SQLite database (`edugenie.db`).
- **Limitation:** Designed for local single-user or small workgroup instances. Production deployment across thousands of concurrent learners would require migrating to PostgreSQL or MySQL with connection pooling.

---

### 2. Strategic Future Scope

The architecture of EduGenie was intentionally designed in modular layers to allow seamless integration of future capabilities without refactoring core logic:

#### 2.1 Multimodal Document Analysis
- Implement PDF extraction and visual diagram understanding via Gemini Multimodal Vision API.
- Allow students to photograph textbook diagrams or upload syllabus PDFs for automatic quiz and summary generation.

#### 2.2 Voice-Driven Interactive Tutoring
- Integrate Web Speech API and Gemini Audio streaming to provide bidirectional vocal tutoring.
- Enable hands-free audio study sessions ideal for language learning and verbal revision.

#### 2.3 Long-Term Student Mastery & Spaced Repetition (SRS)
- Implement an automated SM-2 or FSRS spaced repetition scheduling algorithm in SQLite.
- Track retention over days and weeks, resurfacing previously missed quiz questions at optimal intervals to maximize long-term retention.

#### 2.4 Collaborative Peer Learning Rooms
- Implement WebSockets to allow multiple students to join a shared study session with EduGenie acting as an AI facilitator and moderator.
