import React, { useState } from 'react';
import apiClient from '../services/api';
import VisitModal from '../components/VisitModal';
import './VoterSearch.css';

interface Voter {
  id: number;
  voter_id: string;
  full_name: string;
  status: string;
  sentiment?: string;
  notes?: string;
  version: number;
  structured_data: {
    address?: string;
    booth_no?: string;
    [key: string]: any;
  };
}

const VoterSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [constituency, setConstituency] = useState('Maharashtra North');
  const [results, setResults] = useState<Voter[]>([]);
  const [transliterated, setTransliterated] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVoter, setSelectedVoter] = useState<Voter | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/search', {
        params: { q: searchQuery, limit: 20 }
      });
      setResults(response.data.results || []);
      setTransliterated(response.data.transliterated);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveVisit = async (data: { status: string; sentiment: string; notes: string }) => {
    if (!selectedVoter) return;

    const update = {
      id: selectedVoter.id,
      status: data.status,
      sentiment: data.sentiment,
      notes: data.notes,
      version: selectedVoter.version,
      device_id: 'worker-mobile-402',
      updated_at: new Date().toISOString()
    };

    try {
      await apiClient.post('/sync', [update]);
      // Update local state immediately
      setResults(prev => prev.map(v => 
        v.id === selectedVoter.id 
          ? { ...v, status: data.status, sentiment: data.sentiment, notes: data.notes } 
          : v
      ));
    } catch (err) {
      console.error('Sync failed:', err);
      throw err; // Let the modal handle the error alert
    }
  };

  const getStatusClass = (status: string) => {
    return status?.toLowerCase().replace(' ', '_') || 'pending';
  };

  return (
    <div className="voter-search-container">
      <header className="app-header">
        <div className="app-brand">
          <span className="logo">C</span>
          <h1>Campaign Connect</h1>
        </div>
        <div className="constituency-info">
          <label>Constituency:</label>
          <select value={constituency} onChange={(e) => setConstituency(e.target.value)}>
            <option value="Maharashtra North">Maharashtra North</option>
            <option value="Maharashtra South">Maharashtra South</option>
            <option value="Pune Central">Pune Central</option>
          </select>
        </div>
        <div className="user-profile">
          <span>Worker: #402</span>
        </div>
      </header>

      <main className="search-main">
        <section className="search-section">
          <h2>Voter Search</h2>
          <p>Search by Name or EPIC ID to find voter details and booth information.</p>
          
          <form className="search-bar" onSubmit={handleSearch}>
            <input 
              type="text" 
              placeholder="Search voters (e.g. 'Rajesh' or 'राजेश')..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </form>

          {transliterated && (
            <div className="transliteration-hint">
              Searching for: <strong>{transliterated}</strong>
            </div>
          )}

          {error && <div className="search-error">{error}</div>}
        </section>

        <section className="results-section">
          <div className="results-header">
            <h3>Search Results</h3>
            <span>{results.length} records found</span>
          </div>

          {results.length === 0 && !isLoading && searchQuery && (
            <div className="no-results">No voters found matching your query.</div>
          )}

          <div className="results-grid">
            {results.map(voter => (
              <div key={voter.id} className="voter-search-card">
                <div className="voter-header">
                  <h4>{voter.full_name}</h4>
                  <span className={`status-pill ${getStatusClass(voter.status)}`}>
                    {voter.status || 'Pending'}
                  </span>
                </div>
                <div className="voter-details">
                  <div className="detail-row">
                    <span className="label">EPIC ID:</span>
                    <span className="value">{voter.voter_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Address:</span>
                    <span className="value">{voter.structured_data?.address || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Booth:</span>
                    <span className="value">{voter.structured_data?.booth_no || 'N/A'}</span>
                  </div>
                  {voter.sentiment && (
                    <div className="detail-row">
                      <span className="label">Sentiment:</span>
                      <span className={`value sentiment-${voter.sentiment.toLowerCase()}`}>
                        {voter.sentiment}
                      </span>
                    </div>
                  )}
                </div>
                <div className="card-actions">
                  <button className="btn-secondary">View History</button>
                  <button 
                    className="btn-primary"
                    onClick={() => setSelectedVoter(voter)}
                  >
                    Mark Visited
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {selectedVoter && (
        <VisitModal
          voter={selectedVoter}
          onClose={() => setSelectedVoter(null)}
          onSave={handleSaveVisit}
        />
      )}
    </div>
  );
};

export default VoterSearch;
