#!/usr/bin/env python3
"""
Performance tests for Patricia Tree implementation.
Tests demonstrate O(N) average case complexity and key length dependency.
"""

import subprocess
import time
import random
import string
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# Configuration
PATRICIA_BIN = Path(__file__).parent.parent / "build" / "patricia"
OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_KEY_LENGTH = 256
NUM_RUNS = 3

class PatriciaPerformanceTester:
    def __init__(self, binary_path, num_runs=NUM_RUNS):
        self.binary = str(binary_path)
        self.num_runs = num_runs
        if not os.path.exists(self.binary):
            raise FileNotFoundError(f"Patricia binary not found: {self.binary}")
    
    def generate_random_word(self, length):
        """Generate random English word of given length."""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def generate_test_data(self, count, key_length):
        """Generate test data: list of (word, value) tuples."""
        words = set()
        while len(words) < count:
            words.add(self.generate_random_word(key_length))
        values = [random.randint(0, 2**64 - 1) for _ in range(count)]
        return list(zip(sorted(words), values))
    
    def run_test(self, operations):
        """
        Run test with given operations and measure time.
        
        operations: list of tuples like:
            ('insert', 'word', value)
            ('search', 'word')
            ('delete', 'word')
        
        Returns: elapsed time in seconds
        """
        input_str = ""
        for op in operations:
            if op[0] == 'insert':
                input_str += f"+ {op[1]} {op[2]}\n"
            elif op[0] == 'search':
                input_str += f"{op[1]}\n"
            elif op[0] == 'delete':
                input_str += f"- {op[1]}\n"
        
        start = time.time()
        try:
            result = subprocess.run(
                self.binary,
                input=input_str,
                capture_output=True,
                text=True,
                timeout=60
            )
            elapsed = time.time() - start
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None
            return elapsed
        except subprocess.TimeoutExpired:
            print("Timeout during test")
            return None
    
    def test_complexity_by_n(self, key_length=20):
        """
        Test complexity by varying N (number of elements).
        Keeps key length fixed. Runs multiple times and averages.
        """
        print(f"\n[TEST 1] Testing complexity O(N) with fixed key length={key_length}")
        print(f"Running {self.num_runs} iterations per test point")
        print("-" * 70)
        
        n_values = [1000, 5000, 10000, 50000, 100000, 250000, 500000]
        insert_times = []
        search_times = []
        delete_times = []
        
        for n in n_values:
            print(f"Testing N={n:7d}...", end=" ", flush=True)
            
            t_insert_runs = []
            t_search_runs = []
            t_delete_runs = []
            
            for run in range(self.num_runs):
                data = self.generate_test_data(n, key_length)
                words = [w for w, v in data]
                
                # Test insertions
                insert_ops = [('insert', w, v) for w, v in data]
                t_insert = self.run_test(insert_ops)
                if t_insert is not None:
                    t_insert_runs.append(t_insert)
                
                # Test searches - search ALL words
                search_ops = [('search', w) for w in words]
                t_search = self.run_test(search_ops)
                if t_search is not None:
                    t_search_runs.append(t_search)
                
                # Test deletions
                delete_words = random.sample(words, min(int(0.5 * n), n))
                init_ops = [('insert', w, v) for w, v in data]
                delete_ops = [('delete', w) for w in delete_words]
                t_delete = self.run_test(init_ops + delete_ops)
                if t_delete is not None:
                    t_delete_runs.append(t_delete)
            
            # Average results
            if t_insert_runs and t_search_runs and t_delete_runs:
                avg_insert = np.mean(t_insert_runs)
                avg_search = np.mean(t_search_runs)
                avg_delete = np.mean(t_delete_runs)
                
                insert_times.append(avg_insert)
                search_times.append(avg_search)
                delete_times.append(avg_delete)
                
                print(f"Ins: {avg_insert:8.4f}s | Src: {avg_search:8.4f}s | Del: {avg_delete:8.4f}s")
            else:
                print("FAILED")
        
        return n_values, insert_times, search_times, delete_times
    
    def test_complexity_by_key_length(self, n=200000):
        """
        Test complexity by varying key length.
        Keeps N (number of elements) fixed. Runs multiple times and averages.
        """
        print(f"\n[TEST 2] Testing key length dependency with fixed N={n}")
        print(f"Running {self.num_runs} iterations per test point")
        print("-" * 70)
        
        key_lengths = [5, 10, 20, 50, 100, MAX_KEY_LENGTH]
        insert_times = []
        search_times = []
        delete_times = []
        
        for k_len in key_lengths:
            print(f"Testing key_length={k_len:3d}...", end=" ", flush=True)
            
            t_insert_runs = []
            t_search_runs = []
            t_delete_runs = []
            
            for run in range(self.num_runs):
                data = self.generate_test_data(n, k_len)
                words = [w for w, v in data]
                
                # Test insertions
                insert_ops = [('insert', w, v) for w, v in data]
                t_insert = self.run_test(insert_ops)
                if t_insert is not None:
                    t_insert_runs.append(t_insert)
                
                # Test searches - search ALL words
                search_ops = [('search', w) for w in words]
                t_search = self.run_test(search_ops)
                if t_search is not None:
                    t_search_runs.append(t_search)
                
                # Test deletions
                delete_words = random.sample(words, min(int(0.5 * n), n))
                init_ops = [('insert', w, v) for w, v in data]
                delete_ops = [('delete', w) for w in delete_words]
                t_delete = self.run_test(init_ops + delete_ops)
                if t_delete is not None:
                    t_delete_runs.append(t_delete)
            
            # Average results
            if t_insert_runs and t_search_runs and t_delete_runs:
                avg_insert = np.mean(t_insert_runs)
                avg_search = np.mean(t_search_runs)
                avg_delete = np.mean(t_delete_runs)
                
                insert_times.append(avg_insert)
                search_times.append(avg_search)
                delete_times.append(avg_delete)
                
                print(f"Ins: {avg_insert:8.4f}s | Src: {avg_search:8.4f}s | Del: {avg_delete:8.4f}s")
            else:
                print("FAILED")
        
        return key_lengths, insert_times, search_times, delete_times
    
    def plot_results(self, x_values, insert_times, search_times, delete_times, 
                     xlabel, title_suffix, filename):
        """Plot time complexity results."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 4))
        
        # Insert plot
        axes[0].plot(x_values, insert_times, 'o-', linewidth=2, markersize=8, color='#2E86AB')
        axes[0].set_xlabel(xlabel, fontsize=12)
        axes[0].set_ylabel('Time (seconds)', fontsize=12)
        axes[0].set_title(f'Insertion Time {title_suffix}', fontsize=13)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xscale('log')
        axes[0].set_yscale('log')
        
        # Search plot
        axes[1].plot(x_values, search_times, 'o-', linewidth=2, markersize=8, color='#A23B72')
        axes[1].set_xlabel(xlabel, fontsize=12)
        axes[1].set_ylabel('Time (seconds)', fontsize=12)
        axes[1].set_title(f'Search Time {title_suffix}', fontsize=13)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xscale('log')
        axes[1].set_yscale('log')
        
        # Delete plot
        axes[2].plot(x_values, delete_times, 'o-', linewidth=2, markersize=8, color='#F18F01')
        axes[2].set_xlabel(xlabel, fontsize=12)
        axes[2].set_ylabel('Time (seconds)', fontsize=12)
        axes[2].set_title(f'Deletion Time {title_suffix}', fontsize=13)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_xscale('log')
        axes[2].set_yscale('log')
        
        plt.tight_layout()
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {filepath}")
        plt.close()
    
    def plot_combined(self, x_values, insert_times, search_times, delete_times,
                      xlabel, title_suffix, filename):
        """Plot all operations on one graph."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(x_values, insert_times, 'o-', linewidth=2, markersize=8, 
                label='Insertion', color='#2E86AB')
        ax.plot(x_values, search_times, 's-', linewidth=2, markersize=8, 
                label='Search', color='#A23B72')
        ax.plot(x_values, delete_times, '^-', linewidth=2, markersize=8, 
                label='Deletion', color='#F18F01')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Time (seconds)', fontsize=12)
        ax.set_title(f'Patricia Tree Performance {title_suffix}', fontsize=14)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        plt.tight_layout()
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()

def main():
    print("=" * 70)
    print("Patricia Tree Performance Testing Suite")
    print("=" * 70)
    
    try:
        tester = PatriciaPerformanceTester(PATRICIA_BIN)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please compile the patricia binary first:")
        print("  cd /mnt/d/Discrete-analysis/Discrete-analysis-Labs/Laboratory_2")
        print("  mkdir -p build && cd build")
        print("  cmake .. && make")
        sys.exit(1)
    
    # Test 1: Complexity by N
    n_vals, t_ins, t_src, t_del = tester.test_complexity_by_n(key_length=20)
    if t_ins:
        tester.plot_results(n_vals, t_ins, t_src, t_del, 'Number of Elements (N)', 
                            '(fixed key_length=20)', 'test1_by_n_separate.png')
        tester.plot_combined(n_vals, t_ins, t_src, t_del, 'Number of Elements (N)', 
                             '(fixed key_length=20)', 'test1_by_n_combined.png')
    
    # Test 2: Complexity by key length
    k_vals, t_ins2, t_src2, t_del2 = tester.test_complexity_by_key_length(n=200000)
    if t_ins2:
        tester.plot_results(k_vals, t_ins2, t_src2, t_del2, 'Key Length (characters)', 
                            '(fixed N=200000)', 'test2_by_keylength_separate.png')
        tester.plot_combined(k_vals, t_ins2, t_src2, t_del2, 'Key Length (characters)', 
                             '(fixed N=200000)', 'test2_by_keylength_combined.png')
    
    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print(f"✓ Results saved to: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
