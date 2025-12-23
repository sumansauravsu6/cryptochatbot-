# 🔧 Supabase Setup Instructions - FOLLOW THESE STEPS

## ⚠️ IMPORTANT: You MUST Create Database Tables First!

Your app is configured but the **database tables don't exist yet**. Follow these steps:

---

## 📋 Step-by-Step Instructions

### Step 1: Open Supabase Dashboard
1. Go to: **https://supabase.com/dashboard**
2. Sign in to your account
3. Click on your project: **crypto-chatbot** (or whatever you named it)

---

### Step 2: Open SQL Editor
1. In the left sidebar, click **"SQL Editor"** (database icon)
2. Click the **"New query"** button (or the + icon)

---

### Step 3: Copy the SQL Schema
1. Open the file: `supabase_schema.sql` in your project folder
2. **Select ALL the content** (Ctrl+A)
3. **Copy it** (Ctrl+C)

---

### Step 4: Run the SQL Schema
1. Go back to Supabase SQL Editor
2. **Paste** the SQL code (Ctrl+V)
3. Click the **"Run"** button (or press Ctrl+Enter)
4. Wait for execution to complete

---

### Step 5: Verify Tables Created
1. In the left sidebar, click **"Table Editor"**
2. You should see TWO new tables:
   - ✅ `chat_sessions`
   - ✅ `chat_messages`

If you see these tables, **SUCCESS!** 🎉

---

### Step 6: Refresh Your App
1. Go back to your browser with the app
2. **Refresh the page** (F5 or Ctrl+R)
3. Sign in again
4. Start chatting!

---

## 🧪 How to Test It's Working

1. **Send a message** in the chat
2. Go to Supabase Dashboard → **Table Editor**
3. Click on `chat_sessions` - you should see your session
4. Click on `chat_messages` - you should see your messages

---

## 🔍 Check Browser Console

Open browser Developer Tools (F12) and look for these messages:

**✅ Good signs:**
```
✅ Supabase client initialized
📊 Loading sessions from Supabase for: your@email.com
✅ Loaded sessions from Supabase: X sessions
```

**❌ Bad signs (Tables not created):**
```
❌ Error fetching sessions: relation "public.chat_sessions" does not exist
⚠️ TABLES NOT CREATED IN SUPABASE!
```

If you see the bad signs, go back to Step 2 and create the tables!

---

## 📄 SQL Schema Location

The SQL schema file is located at:
```
chatbot-ui/supabase_schema.sql
```

You can also find it in your project root folder.

---

## 🆘 Troubleshooting

### Problem: "relation does not exist" error
**Solution:** You haven't run the SQL schema yet. Go to Step 2.

### Problem: Can't see tables in Table Editor
**Solution:** 
1. Make sure you ran the SQL in the correct project
2. Check for SQL errors in the query results
3. Try running the schema again

### Problem: Messages not saving
**Solution:**
1. Check browser console for errors
2. Verify Row Level Security policies are created
3. Make sure you're signed in with a valid email

---

## ✨ After Setup

Once tables are created, your app will:
- ✅ Save all chat sessions to Supabase
- ✅ Load previous chats when you sign in
- ✅ Sync across all your devices
- ✅ Never lose your conversations

---

## 🎯 Quick Checklist

- [ ] Opened Supabase Dashboard
- [ ] Went to SQL Editor
- [ ] Copied `supabase_schema.sql` content
- [ ] Pasted and ran the SQL
- [ ] Verified tables exist in Table Editor
- [ ] Refreshed the app
- [ ] Tested by sending a message
- [ ] Checked message appears in Supabase

---

**Need more help?** Check `SUPABASE_SETUP.md` for detailed instructions.
