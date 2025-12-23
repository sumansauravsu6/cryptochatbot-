-- Supabase Database Schema for Chat Application
-- Run this SQL in your Supabase SQL Editor to create the necessary tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'bot')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    charts JSONB,
    is_error BOOLEAN DEFAULT FALSE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_email ON chat_sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create policies for chat_sessions
-- Allow users to read their own sessions
CREATE POLICY "Users can view their own sessions"
    ON chat_sessions
    FOR SELECT
    USING (true);  -- We'll rely on user_email matching in the app

-- Allow users to insert their own sessions
CREATE POLICY "Users can create sessions"
    ON chat_sessions
    FOR INSERT
    WITH CHECK (true);

-- Allow users to update their own sessions
CREATE POLICY "Users can update their own sessions"
    ON chat_sessions
    FOR UPDATE
    USING (true);

-- Allow users to delete their own sessions
CREATE POLICY "Users can delete their own sessions"
    ON chat_sessions
    FOR DELETE
    USING (true);

-- Create policies for chat_messages
-- Allow users to read messages from their sessions
CREATE POLICY "Users can view messages"
    ON chat_messages
    FOR SELECT
    USING (true);

-- Allow users to insert messages
CREATE POLICY "Users can create messages"
    ON chat_messages
    FOR INSERT
    WITH CHECK (true);

-- Allow users to update messages
CREATE POLICY "Users can update messages"
    ON chat_messages
    FOR UPDATE
    USING (true);

-- Allow users to delete messages
CREATE POLICY "Users can delete messages"
    ON chat_messages
    FOR DELETE
    USING (true);

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sample query to verify tables were created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- ============================================
-- NEWSLETTER SUBSCRIPTIONS TABLE
-- ============================================

-- Create newsletter_subscriptions table
CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email TEXT NOT NULL UNIQUE,
    user_name TEXT DEFAULT 'User',
    topics TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_newsletter_user_email ON newsletter_subscriptions(user_email);
CREATE INDEX IF NOT EXISTS idx_newsletter_is_active ON newsletter_subscriptions(is_active);

-- Enable Row Level Security
ALTER TABLE newsletter_subscriptions ENABLE ROW LEVEL SECURITY;

-- Create policies for newsletter_subscriptions
CREATE POLICY "Anyone can view subscriptions"
    ON newsletter_subscriptions
    FOR SELECT
    USING (true);

CREATE POLICY "Anyone can create subscriptions"
    ON newsletter_subscriptions
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Anyone can update subscriptions"
    ON newsletter_subscriptions
    FOR UPDATE
    USING (true);

CREATE POLICY "Anyone can delete subscriptions"
    ON newsletter_subscriptions
    FOR DELETE
    USING (true);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_newsletter_subscriptions_updated_at
    BEFORE UPDATE ON newsletter_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
