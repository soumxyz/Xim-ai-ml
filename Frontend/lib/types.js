/**
 * @typedef {Object} VerificationAnalysis
 * @property {number} lexical_similarity
 * @property {number} phonetic_similarity
 * @property {number} semantic_similarity
 * @property {boolean} disallowed_word
 * @property {boolean} periodicity_violation
 * @property {boolean} combination_violation
 * @property {boolean} prefix_suffix_violation
 */

/**
 * @typedef {Object} VerificationResult
 * @property {string} submitted_title
 * @property {string} closest_match
 * @property {number} similarity_score
 * @property {number} verification_probability
 * @property {'Approved' | 'Rejected'} status
 * @property {VerificationAnalysis} analysis
 * @property {string} explanation
 */

/**
 * @typedef {Object} RecentCheck
 * @property {string} id
 * @property {string} title
 * @property {'Approved' | 'Rejected'} status
 * @property {number} probability
 * @property {Date} timestamp
 */

export const types = {};
