import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import './AuthPage.css';

function SignInPage() {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🤖 Crypto Chatbot</h1>
          <p>Sign in to access your AI-powered cryptocurrency assistant</p>
        </div>
        <SignIn 
          appearance={{
            elements: {
              rootBox: "auth-clerk-root",
              card: "auth-clerk-card"
            }
          }}
          routing="path"
          path="/sign-in"
          signUpUrl="/sign-up"
        />
      </div>
    </div>
  );
}

export default SignInPage;
