import { VerificationResult } from './types';

const mockTitles = [
  { name: 'Morning Herald', category: 'existing' },
  { name: 'Daily Tribune', category: 'existing' },
  { name: 'The Telegraph', category: 'existing' },
  { name: 'The Guardian News', category: 'existing' },
  { name: 'Evening Post', category: 'existing' },
  { name: 'Regional Times', category: 'existing' },
];

const explanations = {
  approved: [
    'This title passes all compliance checks. It is sufficiently distinct from existing titles and complies with all regulatory requirements.',
    'Title approved. No conflicts with existing registrations and all phonetic and semantic checks passed successfully.',
    'Verification successful. This title meets all compliance standards and regulatory requirements for registration.',
  ],
  rejected: [
    'This title is rejected because it is highly similar to an existing registered title and violates the uniqueness requirement.',
    'The title contains disallowed words or phrases that violate regulatory compliance standards.',
    'Rejected due to high semantic similarity with an existing title. The periodicity rule violation adds further non-compliance.',
    'This title exceeds the similarity threshold with existing registered titles and is not compliant with regulatory standards.',
    'Title rejected. The combination of semantic and phonetic similarity with existing titles violates compliance requirements.',
  ],
};

function calculateScores(
  submittedTitle: string,
  existingTitle: string
): { lexical: number; phonetic: number; semantic: number } {
  const submitted = submittedTitle.toLowerCase();
  const existing = existingTitle.toLowerCase();

  // Simple lexical similarity (character overlap)
  let lexicalScore = 0;
  const minLength = Math.min(submitted.length, existing.length);
  let matches = 0;
  for (let i = 0; i < minLength; i++) {
    if (submitted[i] === existing[i]) matches++;
  }
  lexicalScore = Math.round((matches / Math.max(submitted.length, existing.length)) * 100);

  // Phonetic similarity (simple word overlap)
  const submittedWords = submitted.split(' ');
  const existingWords = existing.split(' ');
  let phonetic = 0;
  submittedWords.forEach((word) => {
    if (existingWords.some((w) => w.includes(word) || word.includes(w))) {
      phonetic += 20;
    }
  });
  const phoneticScore = Math.min(Math.round(phonetic), 100);

  // Semantic similarity (word presence)
  const semanticScore = 50 + Math.floor(Math.random() * 40);

  return {
    lexical: Math.max(20, lexicalScore),
    phonetic: Math.max(30, phoneticScore),
    semantic: Math.max(40, semanticScore),
  };
}

export async function verifyTitle(title: string): Promise<VerificationResult> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 900 + Math.random() * 300));

  const cleanedTitle = title.trim();
  const randomExisting = mockTitles[Math.floor(Math.random() * mockTitles.length)];
  const scores = calculateScores(cleanedTitle, randomExisting.name);
  const avgSimilarity = Math.round((scores.lexical + scores.phonetic + scores.semantic) / 3);

  // Determine approval based on similarity
  const isApproved = avgSimilarity < 60;
  const probability = isApproved ? 85 + Math.floor(Math.random() * 15) : 15 + Math.floor(Math.random() * 30);

  const hasDisallowedWord = cleanedTitle.toLowerCase().includes('fake') || cleanedTitle.toLowerCase().includes('hoax');
  const isPeriodicity = cleanedTitle.toLowerCase().includes('daily') || cleanedTitle.toLowerCase().includes('morning');
  const isCombination = avgSimilarity > 70 && isPeriodicity;

  return {
    submitted_title: cleanedTitle,
    closest_match: randomExisting.name,
    similarity_score: avgSimilarity,
    verification_probability: probability,
    status: isApproved ? 'Approved' : 'Rejected',
    analysis: {
      lexical_similarity: scores.lexical,
      phonetic_similarity: scores.phonetic,
      semantic_similarity: scores.semantic,
      disallowed_word: hasDisallowedWord,
      periodicity_violation: isPeriodicity && avgSimilarity > 65,
      combination_violation: isCombination,
      prefix_suffix_violation: false,
    },
    explanation: isApproved
      ? explanations.approved[Math.floor(Math.random() * explanations.approved.length)]
      : explanations.rejected[Math.floor(Math.random() * explanations.rejected.length)],
  };
}
