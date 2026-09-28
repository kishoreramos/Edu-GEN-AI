# EduGenie Session Manager
import os
import json
import uuid
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone

from .schemas import ContextState, QuizState, ConversationMessage

logger = logging.getLogger("EduGenie.SessionManager")

# Default database location inside EduGenie package
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "edugenie.db"
DB_PATH = os.getenv("EDUGENIE_DB_PATH", str(DEFAULT_DB_PATH))

class SessionManager:
    """
    Manages persistent conversational sessions, message history, and learning context
    using a lightweight local SQLite database.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a thread-safe connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes SQLite schema if tables do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Sessions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_topic TEXT,
                    context_json TEXT,
                    summary TEXT
                );
                """)
                # Messages table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intent TEXT,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );
                """)
                # Quiz sessions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    quiz_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    questions_json TEXT NOT NULL,
                    score INTEGER,
                    total_questions INTEGER,
                    weak_areas_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );
                """)
                conn.commit()
                logger.info(f"Initialized SQLite database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}", exc_info=True)

    def validate_session_id(self, session_id: Optional[str]) -> Optional[str]:
        """Validates or cleans a session ID to prevent SQL injection or malformed keys."""
        if not session_id or not isinstance(session_id, str):
            return None
        cleaned = session_id.strip()
        # Keep alphanumeric, hyphens, and underscores up to 64 chars
        if 1 <= len(cleaned) <= 64 and all(c.isalnum() or c in "-_" for c in cleaned):
            return cleaned
        return None

    def create_session(self, custom_id: Optional[str] = None) -> str:
        """Creates a new session and returns its session_id."""
        valid_id = self.validate_session_id(custom_id)
        session_id = valid_id or f"session_{uuid.uuid4().hex[:12]}"
        initial_context = ContextState()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, created_at, updated_at, current_topic, context_json)
            VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                None,
                initial_context.model_dump_json()
            ))
            conn.commit()
        return session_id

    def get_or_create_session(self, session_id: Optional[str] = None) -> Tuple[str, ContextState]:
        """
        Retrieves an existing session's context state, or creates a new session
        if missing or invalid.
        """
        valid_id = self.validate_session_id(session_id)
        if valid_id:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT session_id, context_json FROM sessions WHERE session_id = ?", (valid_id,))
                row = cursor.fetchone()
                if row:
                    try:
                        ctx_dict = json.loads(row["context_json"]) if row["context_json"] else {}
                        return valid_id, ContextState(**ctx_dict)
                    except Exception as e:
                        logger.warning(f"Corrupted context for session {valid_id} ({e}); resetting.")
                        reset_state = ContextState()
                        self.update_session_context(valid_id, reset_state)
                        return valid_id, reset_state

        # Create new session if not found or invalid
        new_id = self.create_session(custom_id=valid_id)
        return new_id, ContextState()

    def get_session_context(self, session_id: str) -> Optional[ContextState]:
        """Loads the active context state for a given session."""
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT context_json FROM sessions WHERE session_id = ?", (valid_id,))
            row = cursor.fetchone()
            if row and row["context_json"]:
                try:
                    return ContextState(**json.loads(row["context_json"]))
                except Exception:
                    return ContextState()
        return None

    def update_session_context(self, session_id: str, context: ContextState):
        """Updates the persistent context state for a session."""
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE sessions
            SET updated_at = ?, current_topic = ?, context_json = ?
            WHERE session_id = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                context.current_topic,
                context.model_dump_json(),
                valid_id
            ))
            conn.commit()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """Appends a message to the session's conversation history."""
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            raise ValueError("Invalid session ID.")

        now_str = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO messages (session_id, role, content, intent, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (valid_id, role, content, intent, meta_json, now_str))
            cursor.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now_str, valid_id))
            conn.commit()

        return ConversationMessage(
            role=role,
            content=content,
            intent=intent,
            created_at=now_str,
            metadata=metadata or {}
        )

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ConversationMessage]:
        """
        Retrieves the most recent bounded conversation history (default: last 10 messages)
        in chronological order.
        """
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT role, content, intent, metadata_json, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """, (valid_id, limit))
            rows = cursor.fetchall()

        # Reverse to return in chronological order
        messages = []
        for r in reversed(rows):
            try:
                meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            except Exception:
                meta = {}
            messages.append(ConversationMessage(
                role=r["role"],
                content=r["content"],
                intent=r["intent"],
                created_at=r["created_at"],
                metadata=meta
            ))
        return messages

    def save_quiz_session(self, session_id: str, quiz_state: QuizState):
        """Saves a quiz session record and updates active context."""
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO quiz_sessions (session_id, quiz_id, topic, questions_json, score, total_questions, weak_areas_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                valid_id,
                quiz_state.quiz_id,
                quiz_state.topic,
                json.dumps(quiz_state.questions),
                quiz_state.score,
                quiz_state.total,
                json.dumps(quiz_state.weak_areas)
            ))
            conn.commit()

        # Update context state's last_quiz
        ctx = self.get_session_context(valid_id) or ContextState()
        ctx.last_quiz = quiz_state
        self.update_session_context(valid_id, ctx)

    def clear_session(self, session_id: str):
        """Resets messages and context for a session."""
        valid_id = self.validate_session_id(session_id)
        if not valid_id:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (valid_id,))
            cursor.execute("DELETE FROM quiz_sessions WHERE session_id = ?", (valid_id,))
            cursor.execute("""
            UPDATE sessions
            SET current_topic = NULL, context_json = ?
            WHERE session_id = ?
            """, (ContextState().model_dump_json(), valid_id))
            conn.commit()

    def get_all_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves a list of recent sessions with preview title and message count."""
        sessions = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.session_id, s.created_at, s.updated_at, s.current_topic,
                   (SELECT content FROM messages WHERE session_id = s.session_id AND role = 'user' ORDER BY id ASC LIMIT 1) as first_message,
                   (SELECT COUNT(*) FROM messages WHERE session_id = s.session_id) as message_count
            FROM sessions s
            ORDER BY s.updated_at DESC
            LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            for r in rows:
                first_msg = r["first_message"]
                topic = r["current_topic"]
                if topic:
                    title = topic
                elif first_msg:
                    title = (first_msg[:32] + "...") if len(first_msg) > 32 else first_msg
                else:
                    title = "New Conversation"
                sessions.append({
                    "session_id": r["session_id"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "current_topic": topic,
                    "title": title,
                    "message_count": r["message_count"]
                })
        return sessions

# Default singleton instance
default_session_manager = SessionManager()
