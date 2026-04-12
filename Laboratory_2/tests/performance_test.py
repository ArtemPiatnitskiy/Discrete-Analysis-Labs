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
                timeout=120
            )
            elapsed = time.time() - start
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None
            return elapsed
        except subprocess.TimeoutExpired:
            print("Timeout during test")
            return None
    
    def plot_individual(self, x_values, times, xlabel, ylabel, title, color, filename):
        """Plot a single graph."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(x_values, times, 'o-', linewidth=2.5, markersize=10, color=color)
        ax.set_xlabel(xlabel, fontsize=13)
        ax.set_ylabel(ylabel, fontsize=13)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        plt.tight_layout()
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Сохранено: {filepath}")
        plt.close()
    
    def test_complexity_by_n(self, key_length=20):
        """
        Test complexity by varying N (number of elements).
        Keeps key length fixed. Runs multiple times and averages.
        """
        print(f"\n[ТЕСТ 1] Зависимость O(N) с фиксированной длиной ключа={key_length}")
        print(f"Запуск {self.num_runs} итераций для каждой точки")
        print("-" * 70)
        
        n_values = [1000, 5000, 10000, 50000, 100000, 250000, 500000]
        insert_times = []
        search_times = []
        delete_times = []
        
        for n in n_values:
            print(f"Тестирование N={n:7d}...", end=" ", flush=True)
            
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
                
                print(f"Вст: {avg_insert:8.4f}s | Поиск: {avg_search:8.4f}s | Удал: {avg_delete:8.4f}s")
            else:
                print("ОШИБКА")
        
        return n_values, insert_times, search_times, delete_times
    
    def test_complexity_by_key_length(self, n=200000):
        """
        Test complexity by varying key length.
        Keeps N (number of elements) fixed. Runs multiple times and averages.
        """
        print(f"\n[ТЕСТ 2] Зависимость от длины ключа с фиксированным N={n}")
        print(f"Запуск {self.num_runs} итераций для каждой точки")
        print("-" * 70)
        
        key_lengths = [5, 10, 20, 50, 100, MAX_KEY_LENGTH]
        insert_times = []
        search_times = []
        delete_times = []
        
        for k_len in key_lengths:
            print(f"Тестирование длина_ключа={k_len:3d}...", end=" ", flush=True)
            
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
                
                print(f"Вст: {avg_insert:8.4f}s | Поиск: {avg_search:8.4f}s | Удал: {avg_delete:8.4f}s")
            else:
                print("ОШИБКА")
        
        return key_lengths, insert_times, search_times, delete_times
    
    def test_large_scale_varying_keylen(self):
        """
        Stress test: Very large N (1-5 million) with varying key lengths.
        Shows how the algorithm scales at massive sizes.
        """
        print(f"\n[ТЕСТ 3] Стресс-тест: N=1-5М элементов с переменной длиной ключа")
        print(f"Запуск {self.num_runs} итераций для каждой точки (может быть долгим!)")
        print("-" * 70)
        
        n_values = [1000000, 2000000, 3000000, 4000000, 5000000]
        key_lengths = [10, 20, 50, 100]
        
        results_by_keylen = {}
        
        for k_len in key_lengths:
            print(f"\nТестирование с длиной ключа = {k_len}:")
            insert_times = []
            search_times = []
            delete_times = []
            
            for n in n_values:
                print(f"  N={n//1000000}М...", end=" ", flush=True)
                
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
                    
                    # Test searches - sample 50k searches
                    search_sample = random.sample(words, min(50000, len(words)))
                    search_ops = [('search', w) for w in search_sample]
                    t_search = self.run_test(search_ops)
                    if t_search is not None:
                        t_search_runs.append(t_search)
                    
                    # Test deletions
                    delete_words = random.sample(words, min(50000, len(words)))
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
                    
                    print(f"Вст: {avg_insert:8.2f}s")
                else:
                    print("ОШИБКА")
            
            results_by_keylen[k_len] = (insert_times, search_times, delete_times)
        
        return n_values, key_lengths, results_by_keylen
    
    def plot_combined(self, x_values, insert_times, search_times, delete_times,
                      xlabel, title_suffix, filename_prefix):
        """Plot all operations as separate individual graphs."""
        
        # Insertion graph
        self.plot_individual(x_values, insert_times, xlabel, 'Время (секунды)', 
                            f'Время вставки {title_suffix}', '#2E86AB',
                            f'{filename_prefix}_01_вставка.png')
        
        # Search graph
        self.plot_individual(x_values, search_times, xlabel, 'Время (секунды)',
                            f'Время поиска {title_suffix}', '#A23B72',
                            f'{filename_prefix}_02_поиск.png')
        
        # Deletion graph
        self.plot_individual(x_values, delete_times, xlabel, 'Время (секунды)',
                            f'Время удаления {title_suffix}', '#F18F01',
                            f'{filename_prefix}_03_удаление.png')
    
    def plot_large_scale_results(self, n_values, key_lengths, results_by_keylen):
        """Plot results from large scale stress test with multiple key lengths."""
        
        operations = ['вставка', 'поиск', 'удаление']
        operation_index = {'вставка': 0, 'поиск': 1, 'удаление': 2}
        colors = {'вставка': '#2E86AB', 'поиск': '#A23B72', 'удаление': '#F18F01'}
        
        for op_name, op_idx in operation_index.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            
            for k_len in key_lengths:
                times = results_by_keylen[k_len][op_idx]
                ax.plot(n_values, times, 'o-', linewidth=2.5, markersize=10,
                       label=f'Длина ключа = {k_len}')
            
            ax.set_xlabel('Количество элементов (N)', fontsize=13)
            ax.set_ylabel('Время (секунды)', fontsize=13)
            title_op = f'Время {op_name.lower()} (N = 1-5 миллионов, разные длины ключа)'
            ax.set_title(title_op, fontsize=14, fontweight='bold')
            ax.legend(fontsize=11, loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_xscale('log')
            ax.set_yscale('log')
            
            plt.tight_layout()
            filepath = OUTPUT_DIR / f'тест3_стресс_{op_name.lower()}.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Сохранено: {filepath}")
            plt.close()

def main():
    print("=" * 70)
    print("Набор тестов производительности Patricia Tree")
    print("=" * 70)
    
    try:
        tester = PatriciaPerformanceTester(PATRICIA_BIN)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Пожалуйста, скомпилируйте программу сначала:")
        print("  cd /mnt/d/Discrete-analysis/Discrete-analysis-Labs/Laboratory_2")
        print("  mkdir -p build && cd build")
        print("  cmake .. && make")
        sys.exit(1)
    
    # Test 1: Complexity by N
    n_vals, t_ins, t_src, t_del = tester.test_complexity_by_n(key_length=20)
    if t_ins:
        tester.plot_combined(n_vals, t_ins, t_src, t_del, 'Количество элементов (N)', 
                             '(фиксированная длина ключа = 20)', 'тест1_зависимость_от_N')
    
    # Test 2: Complexity by key length
    k_vals, t_ins2, t_src2, t_del2 = tester.test_complexity_by_key_length(n=200000)
    if t_ins2:
        tester.plot_combined(k_vals, t_ins2, t_src2, t_del2, 'Длина ключа (символы)', 
                             '(фиксированное N = 200000)', 'тест2_зависимость_от_длины')
    
    # Test 3: Large scale stress test
    n_vals_large, k_lens, results = tester.test_large_scale_varying_keylen()
    if results:
        tester.plot_large_scale_results(n_vals_large, k_lens, results)
    
    print("\n" + "=" * 70)
    print("✓ Все тесты завершены!")
    print(f"✓ Результаты сохранены: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
