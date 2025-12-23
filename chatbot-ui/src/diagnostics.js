import { supabase, isSupabaseConfigured } from './lib/supabaseClient';

/**
 * Diagnostic tool to test Supabase connection and table setup
 * Run this in browser console after importing
 */

export const testSupabaseConnection = async () => {
  console.log('🔍 Testing Supabase Connection...\n');
  
  // Check 1: Environment variables
  console.log('1️⃣ Checking environment variables:');
  console.log('   REACT_APP_SUPABASE_URL:', process.env.REACT_APP_SUPABASE_URL ? '✅ Set' : '❌ Not set');
  console.log('   REACT_APP_SUPABASE_ANON_KEY:', process.env.REACT_APP_SUPABASE_ANON_KEY ? '✅ Set' : '❌ Not set');
  console.log('   Is Configured:', isSupabaseConfigured() ? '✅ Yes' : '❌ No');
  console.log('');
  
  if (!isSupabaseConfigured()) {
    console.error('❌ Supabase not configured! Please check your .env file.');
    return;
  }
  
  // Check 2: Test basic connection
  console.log('2️⃣ Testing basic connection:');
  try {
    const { data, error } = await supabase.from('chat_sessions').select('count');
    if (error) {
      console.error('   ❌ Connection error:', error.message);
      if (error.message.includes('relation') && error.message.includes('does not exist')) {
        console.error('\n   ⚠️  TABLES NOT CREATED! You need to run the SQL schema in Supabase.');
        console.log('\n   📋 Follow these steps:');
        console.log('   1. Go to your Supabase dashboard');
        console.log('   2. Click "SQL Editor" in the left menu');
        console.log('   3. Click "New Query"');
        console.log('   4. Copy the content from supabase_schema.sql');
        console.log('   5. Paste it and click "Run"');
      }
    } else {
      console.log('   ✅ Connection successful!');
      console.log('   📊 Tables found');
    }
  } catch (err) {
    console.error('   ❌ Unexpected error:', err);
  }
  console.log('');
  
  // Check 3: Test table existence
  console.log('3️⃣ Checking table structure:');
  try {
    // Check chat_sessions table
    const { data: sessionsData, error: sessionsError } = await supabase
      .from('chat_sessions')
      .select('*')
      .limit(1);
    
    if (sessionsError) {
      console.log('   ❌ chat_sessions table:', sessionsError.message);
    } else {
      console.log('   ✅ chat_sessions table exists');
    }
    
    // Check chat_messages table
    const { data: messagesData, error: messagesError } = await supabase
      .from('chat_messages')
      .select('*')
      .limit(1);
    
    if (messagesError) {
      console.log('   ❌ chat_messages table:', messagesError.message);
    } else {
      console.log('   ✅ chat_messages table exists');
    }
  } catch (err) {
    console.error('   ❌ Error checking tables:', err);
  }
  console.log('');
  
  // Check 4: Test insert permission
  console.log('4️⃣ Testing insert permissions:');
  try {
    const testEmail = 'test@example.com';
    const { data, error } = await supabase
      .from('chat_sessions')
      .insert([
        {
          user_email: testEmail,
          title: 'Test Session',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ])
      .select();
    
    if (error) {
      console.log('   ❌ Insert test failed:', error.message);
    } else {
      console.log('   ✅ Insert test successful!');
      // Clean up test data
      if (data && data[0]) {
        await supabase.from('chat_sessions').delete().eq('id', data[0].id);
        console.log('   ✅ Test data cleaned up');
      }
    }
  } catch (err) {
    console.error('   ❌ Error testing insert:', err);
  }
  console.log('');
  
  console.log('✅ Diagnostic complete!');
};

// Auto-run on import in development
if (process.env.NODE_ENV === 'development') {
  console.log('💡 Run testSupabaseConnection() in console to diagnose issues');
}

export default testSupabaseConnection;
