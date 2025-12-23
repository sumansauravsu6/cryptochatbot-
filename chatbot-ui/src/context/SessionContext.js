import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import { supabaseService } from '../services/supabaseService';
import { isSupabaseConfigured } from '../lib/supabaseClient';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const { user, isLoaded } = useUser();
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isLoadingFromDB, setIsLoadingFromDB] = useState(true);
  const [useLocalStorage, setUseLocalStorage] = useState(!isSupabaseConfigured());
  const isCreatingSessionRef = useRef(false);

  // Load sessions from Supabase when user is authenticated
  useEffect(() => {
    const loadUserSessions = async () => {
      if (!isLoaded) return;

      if (!user || useLocalStorage) {
        // Fallback to localStorage if not authenticated or Supabase not configured
        const saved = localStorage.getItem('chatbot-sessions');
        const savedSessions = saved ? JSON.parse(saved) : [];
        setSessions(savedSessions);
        
        const savedCurrentSession = localStorage.getItem('chatbot-current-session');
        setCurrentSessionId(savedCurrentSession || null);
        setIsLoadingFromDB(false);
        return;
      }

      // Load from Supabase
      try {
        const userEmail = user.primaryEmailAddress?.emailAddress;
        if (!userEmail) {
          console.warn('⚠️ User email not available from Clerk');
          setIsLoadingFromDB(false);
          return;
        }

        console.log('📊 Loading sessions from Supabase for:', userEmail);
        const userSessions = await supabaseService.loadUserSessionsWithMessages(userEmail);
        console.log('✅ Loaded sessions from Supabase:', userSessions.length, 'sessions');
        setSessions(userSessions);
        
        // Set current session to the most recent one if available
        if (userSessions.length > 0) {
          setCurrentSessionId(userSessions[0].id);
          console.log('✅ Set current session to:', userSessions[0].id);
        }
      } catch (error) {
        console.error('❌ Error loading sessions from Supabase:', error);
        console.error('Error details:', error.message);
        
        // Check if it's a table not found error
        if (error.message && error.message.includes('relation') && error.message.includes('does not exist')) {
          console.error('\n⚠️  TABLES NOT CREATED IN SUPABASE!');
          console.log('\n📋 You need to create the database tables:');
          console.log('1. Go to https://supabase.com/dashboard');
          console.log('2. Select your project');
          console.log('3. Click "SQL Editor"');
          console.log('4. Click "New Query"');
          console.log('5. Copy content from supabase_schema.sql');
          console.log('6. Paste and click "Run"\n');
        }
        
        // Fallback to localStorage on error
        const saved = localStorage.getItem('chatbot-sessions');
        const savedSessions = saved ? JSON.parse(saved) : [];
        setSessions(savedSessions);
        console.log('⚠️ Falling back to localStorage:', savedSessions.length, 'sessions');
      } finally {
        setIsLoadingFromDB(false);
      }
    };

    loadUserSessions();
  }, [user, isLoaded, useLocalStorage]);

  // Save to localStorage as backup (only if using localStorage mode)
  useEffect(() => {
    if (useLocalStorage) {
      localStorage.setItem('chatbot-sessions', JSON.stringify(sessions));
    }
  }, [sessions, useLocalStorage]);

  useEffect(() => {
    if (useLocalStorage && currentSessionId) {
      localStorage.setItem('chatbot-current-session', currentSessionId);
    }
  }, [currentSessionId, useLocalStorage]);

  const createNewSession = async () => {
    // Prevent race conditions using ref (synchronous check)
    if (isCreatingSessionRef.current) {
      console.log('⏳ Already creating a session, skipping...');
      return null;
    }

    // Check the LAST (most recent) session - sessions[0] is the most recent
    const lastSession = sessions.length > 0 ? sessions[0] : null;
    
    if (lastSession && (lastSession.messages?.length || 0) === 0) {
      console.log('📝 Reusing last empty session:', lastSession.id);
      setCurrentSessionId(lastSession.id);
      return lastSession.id;
    }

    // Set flag IMMEDIATELY to prevent duplicate creation (synchronous)
    isCreatingSessionRef.current = true;
    console.log('➕ Creating new session...');
    
    try {
      const newSession = {
        id: Date.now().toString(),
        title: 'New Chat',
        messages: [],
        createdAt: new Date().toISOString()
      };

      // If user is authenticated and Supabase is configured, save to Supabase first
      if (user && !useLocalStorage) {
        try {
          const userEmail = user.primaryEmailAddress?.emailAddress;
          if (userEmail) {
            const savedSession = await supabaseService.createSession(userEmail, newSession.title);
            if (savedSession) {
              newSession.id = savedSession.id;
              newSession.createdAt = savedSession.created_at;
              console.log('✅ Session created in Supabase:', newSession.id);
            }
          }
        } catch (error) {
          console.error('Error creating session in Supabase:', error);
        }
      }

      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      return newSession.id;
    } finally {
      // Always reset flag when done
      isCreatingSessionRef.current = false;
    }
  };

  const deleteSession = async (sessionId) => {
    console.log('🗑️ Deleting session:', sessionId);
    
    // If user is authenticated and Supabase is configured, delete from Supabase
    if (user && !useLocalStorage) {
      try {
        const success = await supabaseService.deleteSession(sessionId);
        if (success) {
          console.log('✅ Session deleted from Supabase:', sessionId);
        } else {
          console.error('❌ Failed to delete session from Supabase');
          return; // Don't remove from UI if backend deletion failed
        }
      } catch (error) {
        console.error('Error deleting session from Supabase:', error);
        return; // Don't remove from UI if backend deletion failed
      }
    }

    // Remove from local state only after successful backend deletion
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      const remaining = sessions.filter(s => s.id !== sessionId);
      setCurrentSessionId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const updateSessionMessages = async (sessionId, messages) => {
    // Get the current session BEFORE updating state
    const currentSession = sessions.find(s => s.id === sessionId);
    const existingMessagesCount = currentSession?.messages?.length || 0;
    
    // Generate title from first user message (first message in array)
    const firstUserMessage = messages.find(m => m.sender === 'user');
    const sessionTitle = firstUserMessage 
      ? firstUserMessage.text.substring(0, 50) + (firstUserMessage.text.length > 50 ? '...' : '')
      : 'New Chat';
    
    // Update local state first for immediate UI feedback
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { 
            ...session, 
            messages,
            title: sessionTitle
          }
        : session
    ));

    // If user is authenticated and Supabase is configured, save to Supabase
    if (user && !useLocalStorage && messages.length > 0) {
      try {
        // Only save the new messages that were just added
        const newMessages = messages.slice(existingMessagesCount);
        
        console.log(`💾 Saving ${newMessages.length} new message(s) to Supabase (total: ${messages.length}, existing: ${existingMessagesCount})`);
        
        for (const message of newMessages) {
          await supabaseService.saveMessage(sessionId, message);
        }

        // Update session title in Supabase with first user message
        if (firstUserMessage && currentSession?.title !== sessionTitle) {
          await supabaseService.updateSessionTitle(sessionId, sessionTitle);
        }
      } catch (error) {
        console.error('Error saving messages to Supabase:', error);
      }
    }
  };

  const getCurrentSession = () => {
    return sessions.find(s => s.id === currentSessionId);
  };

  return (
    <SessionContext.Provider value={{
      sessions,
      currentSessionId,
      setCurrentSessionId,
      createNewSession,
      deleteSession,
      updateSessionMessages,
      getCurrentSession,
      isLoadingFromDB,
      useLocalStorage,
      setSessions
    }}>
      {children}
    </SessionContext.Provider>
  );
};
