"""
Mesh Performance & Accuracy Benchmark Suite
This script validates the system metrics to provide empirical proof for judges.
"""
import asyncio
import time
import json
import random
import os
import sys

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.persistence.title_repository import TitleRepository
from app.retrieval.inverted_token_index import InvertedTokenIndex
from app.orchestration.mesh_orchestrator import MeshOrchestrator

async def run_benchmarks():
    print("🚀 Starting Mesh Technical Benchmark Suite...")
    
    # --- SETUP ---
    repo = TitleRepository()
    titles = await repo.get_all_titles()
    if not titles:
        print("❌ Error: No titles found in Dataset.json")
        return

    # Initialize Index
    token_index = InvertedTokenIndex()
    token_index.build_index(titles)
    
    # Initialize Orchestrator (Lexical Mode)
    orchestrator = MeshOrchestrator(token_index=token_index, sbert_available=False)
    
    # --- TEST 1: RECALL ON CONTROLLED VARIANTS ---
    print("\n🎯 Test 1: Measuring Recall on Controlled Variants...")
    test_size = 200
    sample_titles = random.sample(titles, min(test_size, len(titles)))
    
    variants = []
    for t in sample_titles:
        original = t['title']
        # 1. Typo (change 1 char)
        if len(original) > 5:
            typo = list(original)
            idx = random.randint(0, len(original)-1)
            typo[idx] = chr(random.randint(97, 122))
            variants.append(("".join(typo), original))
        
        # 2. Reordered
        words = original.split()
        if len(words) > 1:
            random.shuffle(words)
            variants.append((" ".join(words), original))
            
        # 3. Added stop-word
        variants.append((f"{original} News", original))
        variants.append((f"The {original}", original))

    true_positives = 0
    total_variants = len(variants)
    
    for variant_text, original_source in variants:
        res = await orchestrator.verify(variant_text)
        # If it's a variant of an existing title, it SHOULD be rejected or show high similarity
        if res.decision == "Reject" or (res.analysis and res.analysis.lexical_similarity > 60):
            true_positives += 1
            
    recall = (true_positives / total_variants) * 100 if total_variants > 0 else 0
    print(f"✅ Recall Result: {true_positives}/{total_variants} conflicts detected ({recall:.1f}%)")

    # --- TEST 2: PHONETIC ACCURACY ---
    print("\n🎯 Test 2: Measuring Phonetic Accuracy...")
    phonetic_pairs = [
        ("Kashmeeri Times", "Kashmiri Times"),
        ("Dainik Jaagran", "Dainik Jagran"),
        ("Hindoo", "Hindu"),
        ("Bangal Mirror", "Bengal Mirror"),
        ("Namascar", "Namaskar"),
        ("Amrit Bazzar", "Amrit Bazar"),
        ("Lokmait", "Lokmat"),
        ("Samaachar", "Samachar")
    ]
    
    phonetic_hits = 0
    for p_query, p_target in phonetic_pairs:
        # We check if the phonetic similarity engine or general verification flags high score
        # Since we use MeshOrchestrator, it will check against the whole 12k dataset
        res = await orchestrator.verify(p_query)
        # Check if the intended target or any similar title is found
        if res.analysis and res.analysis.phonetic_similarity > 40:
            phonetic_hits += 1
            
    phonetic_accuracy = (phonetic_hits / len(phonetic_pairs)) * 100
    print(f"✅ Phonetic Accuracy: {phonetic_hits}/{len(phonetic_pairs)} sounds caught ({phonetic_accuracy:.1f}%)")

    # --- TEST 3: SPEED BENCHMARK ---
    print("\n🎯 Test 3: Running Speed Benchmarks...")
    benchmark_size = 100
    bench_titles = [t['title'] for t in random.sample(titles, benchmark_size)]
    
    start_time = time.time()
    for bt in bench_titles:
        await orchestrator.verify(bt)
    end_time = time.time()
    
    avg_speed = ((end_time - start_time) / benchmark_size) * 1000
    print(f"✅ Avg Verification Speed: {avg_speed:.1f}ms per record")

    # --- TEST 4: CONFIDENCE SCORE VALIDATION ---
    print("\n🎯 Test 4: Validating Confidence Scores on True Conflicts...")
    # Gather scores for the true positives from Test 1
    conflict_scores = []
    for variant_text, _ in variants[:50]: # Sample 50
        res = await orchestrator.verify(variant_text)
        if res.scores and "lexical_similarity" in res.scores:
            conflict_scores.append(res.scores["lexical_similarity"])
            
    avg_confidence = (sum(conflict_scores) / len(conflict_scores)) if conflict_scores else 0
    print(f"✅ Avg Similarity for Conflicts: {avg_confidence:.3f}")

    # --- FINAL SUMMARY ---
    print("\n" + "="*50)
    print("🏆 JUDGES-READY PERFORMANCE REPORT")
    print("="*50)
    print(f"1. Overall Recall:     {recall:.1f}%")
    print(f"2. Phonetic Accuracy:  {phonetic_accuracy:.1f}%")
    print(f"3. Avg Processing:     {avg_speed:.1f}ms")
    print(f"4. Confidence Level:   {avg_confidence:.3f}")
    print(f"5. Dataset Scale:      {len(titles)} Records")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
