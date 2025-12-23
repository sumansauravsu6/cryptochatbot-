import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import './AuthPage.css';

function SignUpPage() {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🤖 Crypto Chatbot</h1>
          <p>Create an account to get started</p>
        </div>
        <SignUp 
          appearance={{
            elements: {
              rootBox: "auth-clerk-root",
              card: "auth-clerk-card"
            }
          }}
          routing="path"
          path="/sign-up"
          signInUrl="/sign-in"
        />
      </div>
    </div>
  );
}

export default SignUpPage;
