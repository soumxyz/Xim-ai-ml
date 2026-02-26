const mockResults = {
    default_rejected: {
        submitted_title: "Morning Herald Daily",
        closest_match: "Morning Herald",
        similarity_score: 82,
        verification_probability: 18,
        status: "Rejected",
        analysis: {
            lexical_similarity: 75,
            phonetic_similarity: 80,
            semantic_similarity: 88,
            disallowed_word: false,
            periodicity_violation: true,
            combination_violation: false,
            prefix_suffix_violation: false,
        },
        explanation:
            "This title is rejected because it is highly similar to 'Morning Herald' and adds periodicity to an existing registered title. The semantic similarity score of 88% exceeds the acceptable threshold, and the addition of 'Daily' constitutes a periodicity violation under Section 4.2 of the Title Registration Act.",
    },
    default_approved: {
        submitted_title: "The Civic Observer",
        closest_match: "City Watch Report",
        similarity_score: 22,
        verification_probability: 91,
        status: "Approved",
        analysis: {
            lexical_similarity: 18,
            phonetic_similarity: 12,
            semantic_similarity: 30,
            disallowed_word: false,
            periodicity_violation: false,
            combination_violation: false,
            prefix_suffix_violation: false,
        },
        explanation:
            "This title has been approved. It demonstrates sufficient uniqueness across all similarity metrics. No rule violations were detected. The title does not conflict with any existing registered titles in the database.",
    },
};

export const recentChecks = [
    { title: "National Tribune Weekly", status: "Rejected", probability: 12, timestamp: "2 min ago" },
    { title: "The Civic Observer", status: "Approved", probability: 91, timestamp: "8 min ago" },
    { title: "Metro Daily Express", status: "Rejected", probability: 24, timestamp: "15 min ago" },
    { title: "Sentinel Post", status: "Approved", probability: 87, timestamp: "22 min ago" },
    { title: "Morning Herald Daily", status: "Rejected", probability: 18, timestamp: "31 min ago" },
];

export function getMockResult(title) {
    const lower = title.toLowerCase();
    if (lower.includes("observer") || lower.includes("sentinel") || lower.includes("unique")) {
        return { ...mockResults.default_approved, submitted_title: title };
    }
    return { ...mockResults.default_rejected, submitted_title: title };
}
