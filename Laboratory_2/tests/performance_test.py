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

class PatriciaPerformanceTester:
    def __init__(self, binary_path):
        self.binary = str(binary_path)
        if not os.path.exists(self.binary):
            raise FileNotFoundError(f"Patricia binary not found: {self.binary}")
    
    def generate_random_word(self, length):
        """Generate random English word of given length."""
        if length > MAX_KEY_LENGTH:
            raise ValueError(f"Key length must be <= {MAX_KEY_LENGTH}, got {length}")
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
        
        Returns: (total_time, operation_times)
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
                timeout=30
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
        Keeps key length fixed.
        """
        print(f"\n[TEST 1] Testing complexity O(N) with fixed key length={key_length}")
        print("-" * 60)
        
        n_values = [1000, 5000, 10000, 50000, 100000, 250000, 500000]
        insert_times = []
        search_times = []
        delete_times = []
        
        for n in n_values:
            print(f"Testing N={n}...", end=" ", flush=True)
            
            data = self.generate_test_data(n, key_length)
            words = [w for w, v in data]
            
            # Test insertions
            insert_ops = [('insert', w, v) for w, v in data]
            t_insert = self.run_test(insert_ops)
            insert_times.append(t_insert)
            
            # Test searches
            search_words = random.sample(words, min(1000, n))
            search_ops = [('search', w) for w in search_words]
            t_search = self.run_test(search_ops)
            search_times.append(t_search)
            
            # Test deletions
            delete_words = random.sample(words, min(1000, n))
            # First insert, then delete
            init_ops = [('insert', w, v) for w, v in data]
            delete_ops = [('delete', w) for w in delete_words]
            t_delete = self.run_test(init_ops + delete_ops)
            # Approximate delete time
            delete_times.append(t_delete)
            
            print(f"Insert: {t_insert:.4f}s, Search: {t_search:.4f}s, Delete: {t_delete:.4f}s")
        
        return n_values, insert_times, search_times, delete_times
    
    def test_complexity_by_key_length(self, n=200000):
        """
        Test complexity by varying key length.
        Keeps N (number of elements) fixed.
        """
        print(f"\n[TEST 2] Testing key length dependency with fixed N={n}")
        print("-" * 60)
        
        key_lengths = [5, 10, 20, 50, 100, MAX_KEY_LENGTH]
        insert_times = []
        search_times = []
        delete_times = []
        
        for k_len in key_lengths:
            print(f"Testing key_length={k_len}...", end=" ", flush=True)
            
            data = self.generate_test_data(n, k_len)
            words = [w for w, v in data]
            
            # Test insertions
            insert_ops = [('insert', w, v) for w, v in data]
            t_insert = self.run_test(insert_ops)
            insert_times.append(t_insert)
            
            # Test searches
            search_words = random.sample(words, min(1000, n))
            search_ops = [('search', w) for w in search_words]
            t_search = self.run_test(search_ops)
            search_times.append(t_search)
            
            # Test deletions
            delete_words = random.sample(words, min(100, n))
            init_ops = [('insert', w, v) for w, v in data]
            delete_ops = [('delete', w) for w in delete_words]
            t_delete = self.run_test(init_ops + delete_ops)
            delete_times.append(t_delete)
            
            print(f"Insert: {t_insert:.4f}s, Search: {t_search:.4f}s, Delete: {t_delete:.4f}s")
        
        return key_lengths, insert_times, search_times, delete_times
    
    def plot_results(self, x_values, insert_times, search_times, delete_times, 
                     xlabel, title_suffix, filename):
        """Plot time complexity results."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 4))
        
        # Insert plot
        axes[0].plot(x_values, insert_times, 'o-', linewidth=2, markersize=8, color='#2E86AB')
        axes[0].set_xlabel(xlabel, fontsize=12)
        axes[0].set_ylabel('Время (секунды)', fontsize=12)
        axes[0].set_title(f'Время вставки {title_suffix}', fontsize=13)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xscale('log')
        axes[0].set_yscale('log')
        
        # Search plot
        axes[1].plot(x_values, search_times, 'o-', linewidth=2, markersize=8, color='#A23B72')
        axes[1].set_xlabel(xlabel, fontsize=12)
        axes[1].set_ylabel('Время (секунды)', fontsize=12)
        axes[1].set_title(f'Время поиска {title_suffix}', fontsize=13)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xscale('log')
        axes[1].set_yscale('log')
        
        # Delete plot
        axes[2].plot(x_values, delete_times, 'o-', linewidth=2, markersize=8, color='#F18F01')
        axes[2].set_xlabel(xlabel, fontsize=12)
        axes[2].set_ylabel('Время (секунды)', fontsize=12)
        axes[2].set_title(f'Время удаления {title_suffix}', fontsize=13)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_xscale('log')
        axes[2].set_yscale('log')
        
        plt.tight_layout()
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_combined(self, x_values, insert_times, search_times, delete_times,
                      xlabel, title_suffix, filename):
        """Plot all operations on one graph."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(x_values, insert_times, 'o-', linewidth=2, markersize=8, 
                label='Вставка', color='#2E86AB')
        ax.plot(x_values, search_times, 's-', linewidth=2, markersize=8, 
                label='Поиск', color='#A23B72')
        ax.plot(x_values, delete_times, '^-', linewidth=2, markersize=8, 
                label='Удаление', color='#F18F01')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Время (секунды)', fontsize=12)
        ax.set_title(f'Производительность Patricia Tree {title_suffix}', fontsize=14)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        plt.tight_layout()
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()

    def plot_results_split(self, x_values, insert_times, search_times, delete_times,
                           xlabel, title_suffix, filename_base):
        """Plot separate chart for each operation."""
        plots = [
            ('insert', insert_times, '#2E86AB', 'Время вставки'),
            ('search', search_times, '#A23B72', 'Время поиска'),
            ('delete', delete_times, '#F18F01', 'Время удаления'),
        ]

        for suffix, y_values, color, title in plots:
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.plot(x_values, y_values, 'o-', linewidth=2, markersize=8, color=color)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel('Время (секунды)', fontsize=12)
            ax.set_title(f'{title} {title_suffix}', fontsize=13)
            ax.grid(True, alpha=0.3)
            ax.set_xscale('log')
            ax.set_yscale('log')

            plt.tight_layout()
            filepath = OUTPUT_DIR / f"{filename_base}_{suffix}.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {filepath}")
            plt.close()

def main():
    print("=" * 60)
    print("Patricia Tree Performance Testing Suite")
    print("=" * 60)
    
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
    tester.plot_results_split(n_vals, t_ins, t_src, t_del, 'Количество элементов (N)',
                              '(фиксированная длина ключа = 20)', 'test1_by_n_separate')
    tester.plot_combined(n_vals, t_ins, t_src, t_del, 'Количество элементов (N)', 
                         '(фиксированная длина ключа = 20)', 'test1_by_n_combined.png')
    
    # Test 2: Complexity by key length
    k_vals, t_ins2, t_src2, t_del2 = tester.test_complexity_by_key_length(n=200000)
    tester.plot_results(k_vals, t_ins2, t_src2, t_del2, 'Длина ключа (символы)', 
                        '(фиксированное N = 200000)', 'test2_by_keylength_separate.png')
    tester.plot_combined(k_vals, t_ins2, t_src2, t_del2, 'Длина ключа (символы)', 
                         '(фиксированное N = 200000)', 'test2_by_keylength_combined.png')
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print(f"✓ Results saved to: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
