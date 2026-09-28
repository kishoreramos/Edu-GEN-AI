# Phase 7: Project Documentation — User Guide
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Introduction
Welcome to **EduGenie**, your personal AI-powered learning companion. EduGenie is designed to help you study smarter by answering academic questions, breaking down hard concepts with relatable analogies, testing your recall with interactive quizzes, summarizing long articles, and mapping out structured learning roadmaps.

---

### 2. Getting Started with the Interface

When you open `http://127.0.0.1:8000`, you will see the **EduGenie Home Workspace**:
- **Brand & Sparkle:** `✦ EduGenie` at the top and center.
- **Hero Title:** *"Learn anything. Understand everything."*
- **Floating Input Composer:** A clean single-box input prompt at the center of the screen.
- **Task Selector Chips:** Quick-mode buttons right beneath the input field:
  - `Auto`: Lets EduGenie automatically figure out what you want.
  - `Explain`: Forces simplified concept explanation mode.
  - `Q&A`: Direct academic question answering mode.
  - `Quiz`: Generates a 3-question multiple-choice quiz.
  - `Summary`: Summarizes pasted study text or notes.
  - `Learning Path`: Builds a step-by-step roadmap from beginner to advanced.

---

### 3. How to Use the Five Core Capabilities

#### 3.1 Academic Question & Answer (Q&A)
Use this when you need a clear, factual answer to an academic or technical question.
- **Example Prompts:**
  - *"What is polymorphism in Java?"*
  - *"Why does ice float on water?"*
  - *"What caused the fall of the Roman Empire?"*
- **How to Submit:**
  - Type your question and press `Enter` (or click the arrow button).
  - The answer will appear immediately in a high-contrast message bubble.

---

#### 3.2 Simplified Concept Explanation
Use this when a textbook explanation feels too dense or confusing, and you want a plain-English breakdown with analogies.
- **Example Prompts:**
  - *"Explain recursion like I am five"*
  - *"What is blockchain in simple terms?"*
  - *"Can you explain quantum computing with a real-life analogy?"*
- **Output:**
  - You will receive a breakdown that avoids unnecessary jargon and compares the concept to an everyday object or scenario.

---

#### 3.3 Interactive Multiple-Choice Quizzes
Use this to test your understanding through active recall.
- **Example Prompts:**
  - *"Quiz me on photosynthesis"*
  - *"Test my knowledge on Python list comprehensions"*
  - *"Create a 3-question quiz on World War 2"*
- **Interactive Quiz Feature:**
  - EduGenie renders a clean card containing 3 multiple-choice questions with 4 clickable option buttons each.
  - Click on your chosen option to see immediate visual feedback:
    - **Green:** Correct answer!
    - **Red:** Incorrect! The correct answer will be highlighted.

---

#### 3.4 Educational Text Summarization
Use this when you have long study notes, research paragraphs, or articles that you need condensed.
- **Example Prompts:**
  - *"Summarize this: [paste your 3-paragraph study text]"*
- **Output:**
  - **Key Takeaways:** Bulleted highlights of the core arguments.
  - **3-Sentence Summary:** High-density conceptual summary.

---

#### 3.5 Structured Learning Paths
Use this when starting to study a new subject and needing a clear roadmap.
- **Example Prompts:**
  - *"Create a learning path for Machine Learning"*
  - *"How should I learn web development from scratch?"*
- **Output:**
  - **Beginner Level:** Prerequisites and basic fundamentals.
  - **Intermediate Level:** Practical patterns, tools, and libraries.
  - **Advanced Level:** Architecture, performance, and advanced mastery.

---

### 4. Conversational Follow-Up & Memory
EduGenie remembers what you are studying in the current session. You do not have to repeat the topic name:
1. **Turn 1:** *"What is polymorphism in Java?"* $\rightarrow$ EduGenie answers.
2. **Turn 2:** *"Can you give me a real-world example of that?"* $\rightarrow$ EduGenie provides an example using shapes or animals.
3. **Turn 3:** *"Now quiz me on it"* $\rightarrow$ EduGenie generates a quiz on Java polymorphism.
4. **Turn 4:** *"What should I learn next?"* $\rightarrow$ EduGenie suggests inheritance and abstract classes.

---

### 5. Helpful Keyboard Shortcuts & Controls
- **Send Message:** Press `Enter ↵`.
- **New Line / Multiline Input:** Press `Shift + Enter`.
- **Start Fresh Session:** Click the `+ New Chat` button in the top-right header at any time.
