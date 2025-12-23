import { supabase, isSupabaseConfigured } from '../lib/supabaseClient';

/**
 * Supabase Service for managing chat sessions and messages
 * 
 * Database Schema:
 * 
 * Table: chat_sessions
 * - id (uuid, primary key)
 * - user_email (text, indexed)
 * - title (text)
 * - created_at (timestamp)
 * - updated_at (timestamp)
 * 
 * Table: chat_messages
 * - id (uuid, primary key)
 * - session_id (uuid, foreign key -> chat_sessions.id)
 * - text (text)
 * - sender (text) - 'user' or 'bot'
 * - timestamp (timestamp)
 * - charts (jsonb) - nullable
 * - is_error (boolean)
 */

class SupabaseService {
  /**
   * Fetch all sessions for a user by email
   */
  async getUserSessions(userEmail) {
    if (!isSupabaseConfigured()) {
      console.warn('⚠️ Supabase not configured, returning empty array');
      return [];
    }

    console.log('🔍 Fetching sessions for user:', userEmail);

    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('user_email', userEmail)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('❌ Error fetching sessions:', error);
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        console.error('Error details:', error.details);
        return [];
      }

      console.log('✅ Found sessions:', data?.length || 0);
      return data || [];
    } catch (error) {
      console.error('❌ Unexpected error in getUserSessions:', error);
      return [];
    }
  }

  /**
   * Fetch all messages for a specific session
   */
  async getSessionMessages(sessionId) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    try {
      const { data, error } = await supabase
        .from('chat_messages')
        .select('*')
        .eq('session_id', sessionId)
        .order('timestamp', { ascending: true });

      if (error) {
        console.error('Error fetching messages:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error in getSessionMessages:', error);
      return [];
    }
  }

  /**
   * Create a new chat session
   */
  async createSession(userEmail, title = 'New Chat') {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured, returning null');
      return null;
    }

    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .insert([
          {
            user_email: userEmail,
            title: title,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('Error creating session:', error);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Error in createSession:', error);
      return null;
    }
  }

  /**
   * Update session title
   */
  async updateSessionTitle(sessionId, title) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured');
      return false;
    }

    try {
      const { error } = await supabase
        .from('chat_sessions')
        .update({ 
          title: title,
          updated_at: new Date().toISOString()
        })
        .eq('id', sessionId);

      if (error) {
        console.error('Error updating session title:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error in updateSessionTitle:', error);
      return false;
    }
  }

  /**
   * Delete a session and all its messages
   */
  async deleteSession(sessionId) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured');
      return false;
    }

    try {
      // First delete all messages (cascade should handle this, but being explicit)
      await supabase
        .from('chat_messages')
        .delete()
        .eq('session_id', sessionId);

      // Then delete the session
      const { error } = await supabase
        .from('chat_sessions')
        .delete()
        .eq('id', sessionId);

      if (error) {
        console.error('Error deleting session:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error in deleteSession:', error);
      return false;
    }
  }

  /**
   * Save a message to a session
   */
  async saveMessage(sessionId, message) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured');
      return null;
    }

    try {
      const { data, error } = await supabase
        .from('chat_messages')
        .insert([
          {
            session_id: sessionId,
            text: message.text,
            sender: message.sender,
            timestamp: message.timestamp || new Date().toISOString(),
            charts: message.charts || null,
            is_error: message.isError || false
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('Error saving message:', error);
        return null;
      }

      // Update session's updated_at timestamp
      await supabase
        .from('chat_sessions')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', sessionId);

      return data;
    } catch (error) {
      console.error('Error in saveMessage:', error);
      return null;
    }
  }

  /**
   * Load all sessions with their messages for a user
   */
  async loadUserSessionsWithMessages(userEmail) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    try {
      // Get all sessions for the user
      const sessions = await this.getUserSessions(userEmail);
      console.log(`📥 Loading messages for ${sessions.length} session(s)`);

      // Load messages for each session
      const sessionsWithMessages = await Promise.all(
        sessions.map(async (session) => {
          const dbMessages = await this.getSessionMessages(session.id);
          
          // Transform database messages to match app format
          const messages = dbMessages.map(msg => ({
            id: msg.id,
            text: msg.text,
            sender: msg.sender,
            timestamp: msg.timestamp,
            charts: msg.charts,
            isError: msg.is_error
          }));
          
          console.log(`  Session ${session.id}: ${messages.length} message(s)`);
          
          return {
            id: session.id,
            title: session.title,
            messages: messages,
            createdAt: session.created_at,
            updatedAt: session.updated_at
          };
        })
      );

      return sessionsWithMessages;
    } catch (error) {
      console.error('Error in loadUserSessionsWithMessages:', error);
      return [];
    }
  }

  /**
   * Clear all messages from a session (keep the session)
   */
  async clearSessionMessages(sessionId) {
    if (!isSupabaseConfigured()) {
      console.warn('Supabase not configured');
      return false;
    }

    try {
      const { error } = await supabase
        .from('chat_messages')
        .delete()
        .eq('session_id', sessionId);

      if (error) {
        console.error('Error clearing messages:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error in clearSessionMessages:', error);
      return false;
    }
  }
}

// Export a singleton instance
export const supabaseService = new SupabaseService();
