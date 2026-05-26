import { create } from 'zustand';

interface VoterData {
  id: string;
  epicId: string;
  name: string;
  age: number;
  gender: 'M' | 'F' | 'O';
  confidence: number;
  boundingBox: { x: number, y: number, w: number, h: number };
}

interface ExtractionState {
  currentJobId: string | null;
  voters: VoterData[];
  selectedVoterId: string | null;
  setVoters: (voters: VoterData[]) => void;
  setSelectedVoterId: (id: string | null) => void;
  updateVoter: (id: string, updates: Partial<VoterData>) => void;
}

export const useExtractionStore = create<ExtractionState>((set) => ({
  currentJobId: null,
  voters: [],
  selectedVoterId: null,
  setVoters: (voters) => set({ voters }),
  setSelectedVoterId: (id) => set({ selectedVoterId: id }),
  updateVoter: (id, updates) => set((state) => ({
    voters: state.voters.map((v) => v.id === id ? { ...v, ...updates } : v)
  })),
}));
