-- Migration: Add chat_messages table
-- Purpose: Store conversational AI chat history for context building

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    model TEXT DEFAULT 'deepseek-chat'
);

-- Index for fast retrieval by session
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id, timestamp);

-- Index for searching messages
CREATE INDEX IF NOT EXISTS idx_chat_content ON chat_messages(message);

-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_messages(timestamp DESC);
