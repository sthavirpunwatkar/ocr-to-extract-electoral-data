import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LandingPage from './pages/LandingPage';
import VoterSearch from './pages/VoterSearch';
import ReviewScreen from './pages/ReviewScreen';
import './index.css';

const queryClient = new QueryClient();

type View = 'landing' | 'search' | 'admin';

function App() {
  const [currentView, setCurrentView] = useState<View>('landing');

  const handleLogin = () => {
    setCurrentView('search');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app-wrapper">
        {currentView === 'landing' && <LandingPage onLogin={handleLogin} />}
        
        {currentView !== 'landing' && (
          <>
            <nav className="admin-nav">
              <button 
                className={currentView === 'search' ? 'active' : ''} 
                onClick={() => setCurrentView('search')}
              >
                Voter Search
              </button>
              <button 
                className={currentView === 'admin' ? 'active' : ''} 
                onClick={() => setCurrentView('admin')}
              >
                Data Entry (Admin)
              </button>
              <button onClick={() => setCurrentView('landing')}>Logout</button>
            </nav>

            {currentView === 'search' && <VoterSearch />}
            {currentView === 'admin' && <ReviewScreen />}
          </>
        )}
      </div>
    </QueryClientProvider>
  );
}

export default App;
