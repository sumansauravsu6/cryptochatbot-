# Supabase Integration Setup Guide

This guide will help you set up Supabase to store and retrieve user chat sessions and history.

## 🚀 Quick Start

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Choose a name (e.g., "crypto-chatbot")
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project" and wait for it to initialize (~2 minutes)

### 2. Set Up Database Tables

1. In your Supabase dashboard, go to the **SQL Editor**
2. Click "New Query"
3. Copy and paste the contents of `supabase_schema.sql` file
4. Click **Run** to execute the SQL
5. You should see success messages for table creation

### 3. Get Your API Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
   - **Anon/Public Key** (looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

### 4. Configure Environment Variables

1. In the `chatbot-ui` folder, create a `.env` file (copy from `.env.example`)
2. Add your Supabase credentials:

```env
REACT_APP_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. **Important**: Add `.env` to your `.gitignore` file to keep credentials secret!

### 5. Restart Your Development Server

```bash
cd chatbot-ui
npm start
```

## 📊 Database Schema

### Tables Created

#### `chat_sessions`
Stores user chat sessions
- `id` (UUID): Unique session identifier
- `user_email` (TEXT): User's email from Clerk authentication
- `title` (TEXT): Session title (auto-generated from first message)
- `created_at` (TIMESTAMP): When session was created
- `updated_at` (TIMESTAMP): Last update time

#### `chat_messages`
Stores individual messages within sessions
- `id` (UUID): Unique message identifier
- `session_id` (UUID): Reference to chat_sessions
- `text` (TEXT): Message content
- `sender` (TEXT): 'user' or 'bot'
- `timestamp` (TIMESTAMP): When message was sent
- `charts` (JSONB): Chart data if message includes charts
- `is_error` (BOOLEAN): Whether message is an error

## 🔒 Security Features

- **Row Level Security (RLS)**: Enabled on all tables
- **User Isolation**: Each user can only access their own sessions
- **Email-based Authentication**: Uses Clerk email for user identification
- **Automatic Cleanup**: Messages are deleted when session is deleted (CASCADE)

## 🎯 How It Works

1. **User Signs In**: Clerk authenticates user and provides email
2. **Load Sessions**: App queries Supabase for all sessions matching user email
3. **Display History**: All previous chat sessions are loaded and displayed in sidebar
4. **Save Messages**: New messages are automatically saved to Supabase
5. **Real-time Sync**: Changes are immediately reflected in the database

## 🔄 Fallback to Local Storage

If Supabase is not configured:
- App automatically falls back to localStorage
- All functionality works offline
- No data is lost

## 📝 Testing the Integration

1. **Sign in** with your email
2. **Create a chat session** and send some messages
3. **Sign out** and **sign back in**
4. Your previous sessions should be restored!
5. Check the **Supabase Dashboard** → **Table Editor** to see your data

## 🛠️ Troubleshooting

### Sessions Not Loading?
- Check browser console for errors
- Verify `.env` file has correct credentials
- Ensure Supabase project is active (not paused)
- Check SQL Editor for any failed queries

### Cannot Save Messages?
- Verify RLS policies are set correctly
- Check network tab in browser DevTools
- Ensure tables were created successfully

### Connection Errors?
- Verify `REACT_APP_SUPABASE_URL` is correct
- Check `REACT_APP_SUPABASE_ANON_KEY` is valid
- Restart development server after changing `.env`

## 🎨 Features

✅ **Persistent Chat History**: Never lose your conversations  
✅ **Multi-Device Sync**: Access your chats from anywhere  
✅ **Email-based Identification**: Secure user isolation  
✅ **Automatic Backup**: All messages saved in real-time  
✅ **Offline Support**: Works without Supabase (localStorage fallback)  
✅ **Smart Session Management**: Auto-generates session titles  
✅ **Fast Performance**: Indexed queries for quick loading  

## 🚦 Next Steps

- Set up automated backups in Supabase
- Add user preferences storage
- Implement search across all sessions
- Add export functionality for chat history

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

---

**Note**: Make sure to keep your `.env` file secure and never commit it to version control!
