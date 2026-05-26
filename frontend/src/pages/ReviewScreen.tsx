import React, { useEffect } from 'react';
import { useExtractionStore } from '../store/useExtractionStore';
import '../styles/ReviewScreen.css';

const ReviewScreen: React.FC = () => {
  const { voters, selectedVoterId, setVoters, setSelectedVoterId, updateVoter } = useExtractionStore();

  const selectedVoter = voters.find(v => v.id === selectedVoterId) || null;

  useEffect(() => {
    // Initial mock data
    setVoters([
      { id: '1', epicId: 'ABC1234567', name: 'John Doe', age: 34, gender: 'M', confidence: 0.98, boundingBox: { x: 50, y: 100, w: 200, h: 50 } },
      { id: '2', epicId: 'XYZ9876543', name: 'Jane Smith', age: 29, gender: 'F', confidence: 0.82, boundingBox: { x: 50, y: 160, w: 200, h: 50 } },
    ]);
  }, [setVoters]);

  const handleVerify = (id: string) => {
    // Logic to verify voter
    console.log(`Verified voter ${id}`);
  };

  const handleSave = () => {
    if (selectedVoter) {
      console.log('Saving changes for', selectedVoter.id);
      // In a real app, this would call an API
    }
  };

  return (
    <div className="review-container">
      {/* Header */}
      <header className="review-header">
        <div className="header-title">
          <h1>OCR Data Command Center</h1>
          <span className="badge badge-processing">Batch #402 - Maharashtra North</span>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary">Previous Page</button>
          <button className="btn btn-secondary">Next Page</button>
          <button className="btn btn-primary">Finish Batch</button>
        </div>
      </header>

      <main className="review-main">
        {/* Document Viewer */}
        <div className="document-viewer">
          <div className="canvas-wrapper">
            <img 
              src="https://via.placeholder.com/800x1200?text=Electoral+Roll+Page+4" 
              alt="Electoral Roll" 
              className="page-image"
            />
            {voters.map(v => (
              <div 
                key={v.id}
                className={`bounding-box ${selectedVoterId === v.id ? 'active' : ''} ${v.confidence < 0.85 ? 'low-confidence' : ''}`}
                style={{
                  left: `${v.boundingBox.x}px`,
                  top: `${v.boundingBox.y}px`,
                  width: `${v.boundingBox.w}px`,
                  height: `${v.boundingBox.h}px`
                }}
                onClick={() => setSelectedVoterId(v.id)}
              />
            ))}
          </div>
        </div>

        {/* Data Panel */}
        <aside className="data-panel">
          <div className="panel-header">
            <h2>Extracted Records</h2>
            <span className="count">{voters.length} Voters Found</span>
          </div>
          <div className="voter-list">
            {voters.map(v => (
              <div 
                key={v.id} 
                className={`voter-card ${selectedVoterId === v.id ? 'active' : ''}`}
                onClick={() => setSelectedVoterId(v.id)}
              >
                <div className="voter-info">
                  <div className="epic-id">{v.epicId}</div>
                  <div className="voter-name">{v.name}</div>
                  <div className="voter-meta">
                    Age: {v.age} | Gender: {v.gender}
                  </div>
                </div>
                <div className="voter-status">
                  <div className={`confidence-score ${v.confidence < 0.85 ? 'warning' : 'good'}`}>
                    {(v.confidence * 100).toFixed(0)}%
                  </div>
                  <button 
                    className="btn-verify"
                    onClick={(e) => { e.stopPropagation(); handleVerify(v.id); }}
                  >
                    ✓
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          {selectedVoter && (
            <div className="edit-form">
              <h3>Edit Details</h3>
              <div className="form-group">
                <label>Full Name</label>
                <input 
                  type="text" 
                  value={selectedVoter.name} 
                  onChange={(e) => updateVoter(selectedVoter.id, { name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>EPIC ID</label>
                <input 
                  type="text" 
                  value={selectedVoter.epicId} 
                  onChange={(e) => updateVoter(selectedVoter.id, { epicId: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Age</label>
                  <input 
                    type="number" 
                    value={selectedVoter.age} 
                    onChange={(e) => updateVoter(selectedVoter.id, { age: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select 
                    value={selectedVoter.gender}
                    onChange={(e) => updateVoter(selectedVoter.id, { gender: e.target.value as 'M' | 'F' | 'O' })}
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                  </select>
                </div>
              </div>
              <button className="btn btn-save" onClick={handleSave}>Save Changes</button>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
};

export default ReviewScreen;
