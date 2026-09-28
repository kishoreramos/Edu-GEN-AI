# Phase 8: Project Demonstration — Demonstration Recording Checklist
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### Phase A: Pre-Recording Preparation Checklist
Ensure these prerequisites are satisfied before beginning your screen recording:

- [ ] **Python Environment Ready:** Confirm `.venv` is activated and dependencies are installed (`pip install -r requirements.txt`).
- [ ] **Valid API Key in `.env`:** Verify `GEMINI_API_KEY` is present and active in `EduGenie/.env`.
- [ ] **Clean Database State:** If you want a fresh conversation history, delete or rename `edugenie.db` so a brand-new database is auto-generated upon startup.
- [ ] **Server Launch:** Run `python -m uvicorn main:app --host 127.0.0.1 --port 8000` in your terminal and verify `Uvicorn running on http://127.0.0.1:8000`.
- [ ] **Browser Window Setup:** Open `http://127.0.0.1:8000` in Google Chrome or Microsoft Edge. Set zoom level to 100%. Maximize or set window to 1920x1080 resolution.
- [ ] **Recording Tool Prepared:** Use OBS Studio, Loom, or Windows Xbox Game Bar (`Win + G`). Set recording resolution to 1080p (1920x1080) at 30fps or 60fps.
- [ ] **Microphone & Audio Check:** Conduct a 10-second test recording to verify your voice is loud, clear, and free from background hum or clipping.
- [ ] **Prepared Test Inputs:** Have the demo prompt queries copied in a notepad for smooth pasting:
  1. Q&A: *"What is polymorphism in Java?"*
  2. Concept Explanation: *"Can you explain that more simply with an analogy?"*
  3. Quiz: *"Quiz me on this topic"*
  4. Summarization: [Sample 2-paragraph passage on the Industrial Revolution]
  5. Learning Path: *"Create a learning path for Python Programming"*

---

### Phase B: During-Recording Execution Checklist

- [ ] **Opening:** Clearly state project title, your name, and project purpose.
- [ ] **Visual Showcase:** Allow 5 seconds to showcase the home screen and ambient Lightfall background.
- [ ] **Demonstrate Q&A:** Submit the polymorphism question; highlight the structured answer.
- [ ] **Demonstrate Concept Explanation & Context:** Ask for a simpler analogy without retyping the topic; show context memory working.
- [ ] **Demonstrate Quiz Generation & Interactivity:** Generate the quiz; click correct and incorrect options to demonstrate live color-coded feedback.
- [ ] **Demonstrate Summarization:** Paste passage; point out the Key Takeaways and 3-Sentence Summary.
- [ ] **Demonstrate Learning Path:** Request Python roadmap; highlight Beginner, Intermediate, and Advanced tiers.
- [ ] **Demonstrate Auto Routing & Mobile View:** Submit an unprompted command in Auto mode; briefly open mobile responsive view (F12 $\rightarrow$ device toggle).
- [ ] **Closing:** Click `+ New Chat`, summarize verified capabilities, and conclude politely.

---

### Phase C: Post-Recording & Google Drive Submission Checklist

- [ ] **Review Video Playback:** Watch the recorded video to verify clear audio, smooth video transitions, and complete demonstration of all 5 features.
- [ ] **Upload to Google Drive:** Upload the MP4 video file to your personal/student Google Drive.
- [ ] **Configure Sharing Permissions:**
  - Right-click the uploaded video $\rightarrow$ Click **Share**.
  - Under *General access*, change from *"Restricted"* to:
    **"Anyone with the link"** with role set to **"Viewer"**.
- [ ] **Test in Incognito Mode:** Open a new private/incognito browser window and paste the sharing link to ensure it streams without prompting for a Google login.
- [ ] **Record Link in Documentation:** Add the sharing link to `docs/SUBMISSION_CHECKLIST.md` and the final submission form.
