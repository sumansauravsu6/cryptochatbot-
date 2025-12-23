import React from 'react';
import { SignedIn, SignedOut, RedirectToSignIn, UserButton } from '@clerk/clerk-react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import { ThemeProvider } from './context/ThemeContext';
import { SessionProvider } from './context/SessionContext';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <SessionProvider>
        {/* Show content only when user is signed in */}
        <SignedIn>
          <div className="app">
            <Sidebar />
            <div className="main-content">
              <div className="user-profile-header">
                <UserButton 
                  afterSignOutUrl="/"
                  appearance={{
                    elements: {
                      avatarBox: "user-avatar"
                    }
                  }}
                />
              </div>
              <ChatInterface />
            </div>
          </div>
        </SignedIn>
        
        {/* Redirect to sign-in when user is not authenticated */}
        <SignedOut>
          <RedirectToSignIn />
        </SignedOut>
      </SessionProvider>
    </ThemeProvider>
  );
}

export default App;
