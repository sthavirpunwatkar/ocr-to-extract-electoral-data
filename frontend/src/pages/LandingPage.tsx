import React, { useState } from 'react';
import './LandingPage.css';

interface LandingPageProps {
  onLogin: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate login
    if (username && password) {
      onLogin();
    }
  };

  return (
    <div className="landing-page">
      <div className="campaign-hero">
        <div className="party-symbol">
          {/* Placeholder for party symbol */}
          <div className="symbol-placeholder">
            <span>PARTY SYMBOL</span>
          </div>
        </div>
        <div className="candidate-profile">
          <div className="candidate-image-placeholder">
            <span>CANDIDATE IMAGE</span>
          </div>
          <h1>Vijay Rathore</h1>
          <p>Your Voice, Your Progress</p>
          <span className="constituency-tag">Maharashtra North Constituency</span>
        </div>
      </div>

      <div className="login-section">
        <div className="login-card">
          <h2>Campaign Worker Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Worker ID</label>
              <input 
                type="text" 
                placeholder="Enter Worker ID" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Access Pin</label>
              <input 
                type="password" 
                placeholder="••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="login-btn">
              Enter Campaign Dashboard
            </button>
          </form>
          <p className="login-footer">
            Contact your local coordinator for access issues.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
