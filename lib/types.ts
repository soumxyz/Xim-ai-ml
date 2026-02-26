export interface VerificationAnalysis {
  lexical_similarity: number;
  phonetic_similarity: number;
  semantic_similarity: number;
  disallowed_word: boolean;
  periodicity_violation: boolean;
  combination_violation: boolean;
  prefix_suffix_violation: boolean;
}

export interface VerificationResult {
  submitted_title: string;
  closest_match: string;
  similarity_score: number;
  verification_probability: number;
  status: 'Approved' | 'Rejected';
  analysis: VerificationAnalysis;
  explanation: string;
}

export interface RecentCheck {
  id: string;
  title: string;
  status: 'Approved' | 'Rejected';
  probability: number;
  timestamp: Date;
}
