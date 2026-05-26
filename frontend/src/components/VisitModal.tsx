import React, { useState } from 'react';
import '../styles/VisitModal.css';

interface Voter {
  id: number;
  voter_id: string;
  full_name: string;
  status: string;
  sentiment?: string;
  notes?: string;
  version: number;
}

interface VisitModalProps {
  voter: Voter;
  onClose: () => void;
  onSave: (data: { status: string; sentiment: string; notes: string }) => Promise<void>;
}

const VisitModal: React.FC<VisitModalProps> = ({ voter, onClose, onSave }) => {
  const [status, setStatus] = useState(voter.status || 'Visited');
  const [sentiment, setSentiment] = useState(voter.sentiment || 'Neutral');
  const [notes, setNotes] = useState(voter.notes || '');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSave({ status, sentiment, notes });
      onClose();
    } catch (error) {
      console.error('Failed to save visit data:', error);
      alert('Failed to save. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Mark Visit: {voter.full_name}</h3>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Status</label>
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="Visited">Visited</option>
                <option value="Not Home">Not Home</option>
                <option value="Refused">Refused</option>
                <option value="Shifted">Shifted</option>
                <option value="Deceased">Deceased</option>
              </select>
            </div>

            <div className="form-group">
              <label>Sentiment</label>
              <div className="sentiment-options">
                <button
                  type="button"
                  className={`sentiment-btn supportive ${sentiment === 'Supportive' ? 'active' : ''}`}
                  onClick={() => setSentiment('Supportive')}
                >
                  Supportive
                </button>
                <button
                  type="button"
                  className={`sentiment-btn neutral ${sentiment === 'Neutral' ? 'active' : ''}`}
                  onClick={() => setSentiment('Neutral')}
                >
                  Neutral
                </button>
                <button
                  type="button"
                  className={`sentiment-btn opposed ${sentiment === 'Opposed' ? 'active' : ''}`}
                  onClick={() => setSentiment('Opposed')}
                >
                  Opposed
                </button>
              </div>
            </div>

            <div className="form-group">
              <label>Notes / Feedback</label>
              <textarea
                placeholder="Record issues, feedback or specific requests..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="save-btn" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Visit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VisitModal;
