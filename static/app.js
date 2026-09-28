/**
 * EduGenie — Premium AI-Native Educational Learning Interface Client
 * Provides smooth transitions, immediate response rendering, markdown parsing,
 * interactive quiz evaluations, and dynamic contextual suggestions.
 */
document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // Application State
    // -------------------------------------------------------------
    const state = {
        sessionId: (typeof window !== "undefined" && new URLSearchParams(window.location.search).get("session")) || localStorage.getItem("edugenie_session_id") || null,
        isProcessing: false,
        currentTopic: "General Learning",
        selectedTask: "auto",
        hasMessages: false
    };

    // DOM Elements
    const appContainer = document.getElementById("appContainer");
    const messagesContainer = document.getElementById("messagesContainer");
    const welcomeHero = document.getElementById("welcomeHero");
    const typingIndicator = document.getElementById("typingIndicator");
    const chatForm = document.getElementById("chatForm");
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const activeTopicBadge = document.getElementById("activeTopicBadge");
    const newChatBtn = document.getElementById("newChatBtn");
    const latencyIndicator = document.getElementById("latencyIndicator");
    const taskButtons = document.querySelectorAll(".task-btn");

    // -------------------------------------------------------------
    // Initialize Application
    // -------------------------------------------------------------
    function init() {
        setupEventListeners();

        if (state.sessionId) {
            loadSessionHistory(state.sessionId);
        } else {
            setAppState("home");
        }
    }

    function setAppState(mode) {
        if (mode === "chat") {
            appContainer.classList.remove("state-home");
            appContainer.classList.add("state-chat");
            state.hasMessages = true;
        } else {
            appContainer.classList.remove("state-chat");
            appContainer.classList.add("state-home");
            state.hasMessages = false;
        }
    }

    // -------------------------------------------------------------
    // Event Listeners
    // -------------------------------------------------------------
    function setupEventListeners() {
        // Form submission
        chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            handleSend();
        });

        // Textarea auto-resize & keyboard handling
        messageInput.addEventListener("input", autoResizeTextarea);
        messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                chatForm.requestSubmit();
            }
        });

        // Task selection pills
        taskButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                taskButtons.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                state.selectedTask = btn.getAttribute("data-task") || "auto";

                const placeholders = {
                    "auto": "Ask EduGenie anything...",
                    "Explain": "e.g. Explain recursion in simple terms...",
                    "QnA": "e.g. What is polymorphism in Java?",
                    "Quiz": "e.g. Quiz me on Python data structures...",
                    "Summary": "Paste the educational text you want summarized...",
                    "Recommend Path": "e.g. Give me a learning roadmap for SQL..."
                };
                messageInput.placeholder = placeholders[state.selectedTask] || "Ask EduGenie anything...";
                messageInput.focus();
            });
        });

        // New Chat Button
        newChatBtn.addEventListener("click", () => {
            startNewChat();
        });
    }

    function autoResizeTextarea() {
        messageInput.style.height = "auto";
        const newHeight = Math.min(messageInput.scrollHeight, 180);
        messageInput.style.height = `${newHeight}px`;
    }

    function startNewChat() {
        state.sessionId = null;
        state.currentTopic = "General Learning";
        localStorage.removeItem("edugenie_session_id");
        if (activeTopicBadge) {
            activeTopicBadge.textContent = state.currentTopic;
            activeTopicBadge.classList.add("hidden");
        }
        messagesContainer.innerHTML = "";
        if (latencyIndicator) latencyIndicator.textContent = "";
        setAppState("home");
        messageInput.value = "";
        messageInput.style.height = "auto";
        messageInput.focus();
    }

    // -------------------------------------------------------------
    // Session Management & History Recovery
    // -------------------------------------------------------------
    async function loadSessionHistory(sessionId) {
        try {
            const res = await fetch(`/api/session/${sessionId}/history?limit=20`);
            if (!res.ok) {
                setAppState("home");
                return;
            }
            const data = await res.json();
            const messages = data.messages || [];

            if (messages.length > 0) {
                setAppState("chat");
                messagesContainer.innerHTML = "";
                messages.forEach(msg => {
                    if (msg.role === "user") {
                        appendUserBubble(msg.content, false);
                    } else if (msg.role === "assistant") {
                        appendAssistantBubble({
                            reply: msg.content,
                            intent: msg.intent,
                            data: msg.metadata || {}
                        }, false);
                    }
                });
                scrollToBottom();
            } else {
                setAppState("home");
            }
        } catch (err) {
            console.warn("Could not load session history:", err);
            setAppState("home");
        }
    }

    // -------------------------------------------------------------
    // Core Message Sending & Fast Response Delivery
    // -------------------------------------------------------------
    async function handleSend(customText = null) {
        let text = (customText !== null ? customText : messageInput.value).trim();
        if (!text || state.isProcessing) return;

        // Apply manual task prefix if explicit task mode is chosen and not already prefixed
        if (customText === null && state.selectedTask !== "auto") {
            const task = state.selectedTask;
            const lower = text.toLowerCase();
            if (task === "Explain" && !lower.startsWith("explain ") && !lower.startsWith("teach me ")) {
                text = `Explain ${text}`;
            } else if (task === "Quiz" && !lower.startsWith("quiz ") && !lower.startsWith("test me ")) {
                text = `Quiz me on ${text}`;
            } else if (task === "Summary" && !lower.startsWith("summarize")) {
                text = `Summarize: ${text}`;
            } else if (task === "Recommend Path" && !lower.includes("roadmap") && !lower.includes("learning path")) {
                text = `Give me a learning path for ${text}`;
            }
        }

        // Reset input box immediately
        messageInput.value = "";
        messageInput.style.height = "auto";

        // Transition from centered home to active chat state immediately
        setAppState("chat");

        // 1. Render User Message
        appendUserBubble(text, true);

        // 2. Set Processing & Show Typing Indicator Immediately
        setProcessing(true);
        showTypingIndicator();
        scrollToBottom();

        const t0 = performance.now();

        try {
            const payload = {
                message: text,
                session_id: state.sessionId
            };

            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const roundtripMs = Math.round(performance.now() - t0);

            // Hide typing indicator immediately upon server response
            hideTypingIndicator();

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                appendErrorBubble(errData.error || `Server returned error (${res.status})`);
                return;
            }

            const data = await res.json();

            // Display measured latency
            if (latencyIndicator) {
                const s = (roundtripMs / 1000).toFixed(1);
                latencyIndicator.textContent = `⚡ ${s}s`;
            }

            // Update session state
            if (data.session_id) {
                state.sessionId = data.session_id;
                localStorage.setItem("edugenie_session_id", data.session_id);
            }

            // Update topic badge
            if (data.context_state && data.context_state.current_topic) {
                state.currentTopic = data.context_state.current_topic;
                if (activeTopicBadge) {
                    activeTopicBadge.textContent = state.currentTopic;
                    activeTopicBadge.classList.remove("hidden");
                }
            }

            // 3. Render Assistant Response Immediately
            appendAssistantBubble(data, true);

        } catch (err) {
            console.error("Chat request failed:", err);
            hideTypingIndicator();
            appendErrorBubble("Network connection error. Please verify the backend server is running.");
        } finally {
            setProcessing(false);
            messageInput.focus();
            scrollToBottom();
        }
    }

    function setProcessing(isProcessing) {
        state.isProcessing = isProcessing;
        sendBtn.disabled = isProcessing;
        sendBtn.style.opacity = isProcessing ? "0.4" : "1";
    }

    function showTypingIndicator() {
        typingIndicator.classList.remove("hidden");
        messagesContainer.appendChild(typingIndicator);
    }

    function hideTypingIndicator() {
        typingIndicator.classList.add("hidden");
    }

    function scrollToBottom() {
        setTimeout(() => {
            const mainViewport = document.querySelector(".main-viewport");
            if (mainViewport) {
                mainViewport.scrollTop = mainViewport.scrollHeight;
            }
        }, 20);
    }

    // -------------------------------------------------------------
    // Bubble Rendering
    // -------------------------------------------------------------
    function appendUserBubble(text, shouldScroll = true) {
        const row = document.createElement("div");
        row.className = "message-row-user";

        const bubble = document.createElement("div");
        bubble.className = "user-bubble";
        bubble.textContent = text;

        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        if (shouldScroll) scrollToBottom();
    }

    function appendAssistantBubble(data, shouldScroll = true) {
        const row = document.createElement("div");
        row.className = "message-row-assistant";

        // Header
        const header = document.createElement("div");
        header.className = "assistant-header";
        
        const avatar = document.createElement("div");
        avatar.className = "assistant-avatar";
        avatar.textContent = "✨";

        const name = document.createElement("span");
        name.className = "assistant-name";
        name.textContent = "EduGenie";

        header.appendChild(avatar);
        header.appendChild(name);

        if (data.intent && data.intent !== "UNKNOWN") {
            const tag = document.createElement("span");
            tag.className = "assistant-intent-tag";
            tag.textContent = formatIntentLabel(data.intent);
            header.appendChild(tag);
        }

        row.appendChild(header);

        // Body
        const body = document.createElement("div");
        body.className = "assistant-body";
        body.innerHTML = renderMarkdown(data.reply || "");
        row.appendChild(body);

        // Quiz Widget if structured quiz data exists
        const quizData = data.data && data.data.quiz;
        if (Array.isArray(quizData) && quizData.length > 0) {
            const topic = (data.data && data.data.topic) || state.currentTopic;
            const widget = buildQuizWidget(quizData, topic);
            row.appendChild(widget);
        }

        // Contextual Suggestions (clean, non-repetitive chips)
        const suggestions = getContextualSuggestions(data);
        if (suggestions.length > 0) {
            const wrapper = document.createElement("div");
            wrapper.className = "suggestions-wrapper";
            suggestions.forEach(s => {
                const chip = document.createElement("button");
                chip.type = "button";
                chip.className = "suggestion-chip";
                chip.innerHTML = `${s.icon} <span>${escapeHtml(s.label)}</span>`;
                chip.addEventListener("click", () => {
                    handleSend(s.prompt);
                });
                wrapper.appendChild(chip);
            });
            row.appendChild(wrapper);
        }

        messagesContainer.appendChild(row);
        if (shouldScroll) scrollToBottom();
    }

    function appendErrorBubble(message) {
        const row = document.createElement("div");
        row.className = "message-row-assistant";

        const errDiv = document.createElement("div");
        errDiv.className = "error-bubble";
        errDiv.textContent = `⚠️ ${message}`;

        row.appendChild(errDiv);
        messagesContainer.appendChild(row);
        scrollToBottom();
    }

    function formatIntentLabel(intent) {
        const map = {
            "QA": "Q&A",
            "EXPLAIN": "Explanation",
            "QUIZ": "Quiz",
            "SUMMARIZE": "Summary",
            "LEARNING_PATH": "Learning Path",
            "MULTI_ACTION": "Workflow",
            "CLARIFICATION": "Clarification"
        };
        return map[intent] || intent;
    }

    // -------------------------------------------------------------
    // Contextual Suggestions Logic (Subtle, max 2-3, non-repetitive)
    // -------------------------------------------------------------
    function getContextualSuggestions(data) {
        const intent = data.intent || "";
        const topic = (data.data && data.data.topic) || state.currentTopic || "this";

        if (intent === "EXPLAIN" || intent === "QA") {
            return [
                { icon: "✦", label: "Quiz me", prompt: `Quiz me on ${topic}` },
                { icon: "💡", label: "Give an example", prompt: `Can you give me a practical real-world example of that?` },
                { icon: "🐣", label: "Explain simpler", prompt: "Can you explain that more simply?" }
            ];
        } else if (intent === "QUIZ") {
            return [
                { icon: "🔍", label: "Explain mistakes", prompt: "Teach me the concepts I might have missed in this quiz." },
                { icon: "🔄", label: "Try another quiz", prompt: `Give me another 3-question quiz on ${topic}` }
            ];
        } else if (intent === "LEARNING_PATH") {
            return [
                { icon: "🚀", label: "Begin first topic", prompt: `Explain the first beginner topic for ${topic}` },
                { icon: "🎯", label: "Prerequisites quiz", prompt: `Quiz me on foundational knowledge for ${topic}` }
            ];
        } else if (intent === "SUMMARIZE") {
            return [
                { icon: "✦", label: "Quiz on summary", prompt: "Quiz me on the key points in this summary." },
                { icon: "🗺️", label: "Learning roadmap", prompt: "Create a learning path based on this topic." }
            ];
        }
        return [];
    }

    // -------------------------------------------------------------
    // Interactive Quiz Widget Builder
    // -------------------------------------------------------------
    function buildQuizWidget(quizQuestions, topic) {
        const widget = document.createElement("div");
        widget.className = "quiz-widget";

        const quizId = "quiz_" + Math.random().toString(36).substring(2, 9);

        // Header
        const header = document.createElement("div");
        header.className = "quiz-widget-header";
        header.innerHTML = `
            <span class="quiz-title">Practice Assessment: ${escapeHtml(topic || "Self-Check")}</span>
            <span style="font-size: 0.78rem; color: var(--text-muted);">${quizQuestions.length} Questions</span>
        `;
        widget.appendChild(header);

        // Render each question
        quizQuestions.forEach((q, qIndex) => {
            const qCard = document.createElement("div");
            qCard.className = "quiz-question-card";

            const prompt = document.createElement("div");
            prompt.className = "quiz-q-prompt";
            prompt.textContent = `${qIndex + 1}. ${q.question}`;
            qCard.appendChild(prompt);

            const optGroup = document.createElement("div");
            optGroup.className = "quiz-options-group";

            const options = q.options || [];
            options.forEach((opt, optIndex) => {
                const label = document.createElement("label");
                label.className = "quiz-option-label";
                label.dataset.qIndex = qIndex;
                label.dataset.optionText = opt;

                const input = document.createElement("input");
                input.type = "radio";
                input.name = `${quizId}_q${qIndex}`;
                input.value = opt;

                const span = document.createElement("span");
                span.textContent = opt;

                label.appendChild(input);
                label.appendChild(span);
                optGroup.appendChild(label);
            });

            qCard.appendChild(optGroup);

            // Explanation box placeholder (shown after submission)
            const explanationBox = document.createElement("div");
            explanationBox.className = "quiz-explanation-box hidden";
            explanationBox.dataset.qIndex = qIndex;
            qCard.appendChild(explanationBox);

            widget.appendChild(qCard);
        });

        // Submit Button
        const submitBtn = document.createElement("button");
        submitBtn.type = "button";
        submitBtn.className = "quiz-submit-btn";
        submitBtn.textContent = "Check Answers";

        submitBtn.addEventListener("click", () => {
            evaluateQuiz(widget, quizQuestions, submitBtn, topic);
        });

        widget.appendChild(submitBtn);
        return widget;
    }

    function evaluateQuiz(widget, questions, submitBtn, topic) {
        let score = 0;
        const total = questions.length;
        const weakAreas = [];

        questions.forEach((q, qIndex) => {
            const labels = widget.querySelectorAll(`.quiz-option-label[data-q-index="${qIndex}"]`);
            const checkedInput = widget.querySelector(`input[name$="_q${qIndex}"]:checked`);
            const selectedVal = checkedInput ? checkedInput.value.trim() : null;
            const correctVal = (q.correct_answer || q.answer || "").trim();

            const isCorrect = selectedVal && selectedVal.toLowerCase() === correctVal.toLowerCase();
            if (isCorrect) {
                score++;
            } else {
                weakAreas.push({
                    question: q.question,
                    selected: selectedVal,
                    correct: correctVal
                });
            }

            // Highlight options
            labels.forEach(label => {
                const optVal = label.dataset.optionText.trim();
                const isThisCorrect = optVal.toLowerCase() === correctVal.toLowerCase();
                const isThisSelected = selectedVal && optVal.toLowerCase() === selectedVal.toLowerCase();

                if (isThisCorrect) {
                    label.classList.add("is-correct");
                    label.innerHTML += ` <span style="margin-left: auto;">✓</span>`;
                } else if (isThisSelected && !isThisCorrect) {
                    label.classList.add("is-incorrect");
                    label.innerHTML += ` <span style="margin-left: auto;">✗</span>`;
                }
                const rInput = label.querySelector("input");
                if (rInput) rInput.disabled = true;
            });

            // Display explanation
            const explanationBox = widget.querySelector(`.quiz-explanation-box[data-q-index="${qIndex}"]`);
            if (explanationBox) {
                const explText = q.explanation || `Correct answer is: ${correctVal}`;
                explanationBox.innerHTML = `<strong>Explanation:</strong> ${escapeHtml(explText)}`;
                explanationBox.classList.remove("hidden");
            }
        });

        // Hide submit button and show score banner
        submitBtn.classList.add("hidden");

        const banner = document.createElement("div");
        banner.className = "quiz-score-banner";

        const percent = Math.round((score / total) * 100);
        let feedback = "Excellent mastery! 🎉";
        if (percent < 50) feedback = "Good effort! Practice makes progress. 💪";
        else if (percent < 100) feedback = "Great job! A few concepts need a quick review. 👍";

        banner.innerHTML = `
            <div class="quiz-score-header">
                <span>Quiz Complete</span>
                <span>Score: ${score} / ${total} (${percent}%)</span>
            </div>
            <p class="quiz-score-text">${feedback}</p>
        `;

        widget.appendChild(banner);
    }

    // -------------------------------------------------------------
    // Lightweight Fast Markdown Renderer
    // -------------------------------------------------------------
    function renderMarkdown(raw) {
        if (!raw) return "";

        let html = raw.replace(/\r\n/g, "\n");

        // Fenced code blocks
        html = html.replace(/```([a-zA-Z0-9_\-]+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
        });

        // Inline code
        html = html.replace(/`([^`\n]+)`/g, "<code>$1</code>");

        // Bold & Italic
        html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");

        // Blockquotes
        html = html.replace(/^>\s+(.+)$/gm, "<blockquote>$1</blockquote>");

        // Headings
        html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
        html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
        html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

        // Unordered lists
        html = html.replace(/^\s*[-*]\s+(.*)$/gim, "<ul><li>$1</li></ul>");
        html = html.replace(/<\/ul>\s*<ul>/g, "");

        // Numbered lists
        html = html.replace(/^\s*(\d+)\.\s+(.*)$/gim, "<ol><li>$2</li></ol>");
        html = html.replace(/<\/ol>\s*<ol>/g, "");

        // Paragraphs
        const paragraphs = html.split(/\n\n+/);
        html = paragraphs.map(p => {
            p = p.trim();
            if (!p) return "";
            if (p.startsWith("<pre>") || p.startsWith("<h1>") || p.startsWith("<h2>") ||
                p.startsWith("<h3>") || p.startsWith("<ul>") || p.startsWith("<ol>") ||
                p.startsWith("<blockquote>")) {
                return p;
            }
            return `<p>${p.replace(/\n/g, "<br>")}</p>`;
        }).filter(Boolean).join("\n");

        return html;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Run Initialization
    init();
});
