import itertools
import random
import time
import os
import json
from collections import defaultdict
from heapq import nlargest
import argparse

def generate_combinations(pool, size):
    return list(itertools.combinations(sorted(pool), size))

def validate_solution(j_combos, solution, s):
    covered_s = set()
    for group in solution:
        covered_s.update(itertools.combinations(sorted(group), s))
    for jc in j_combos:
        if any(s_sub in covered_s for s_sub in itertools.combinations(jc, s)):
            continue
        return False
    return True

class CoverageOptimizer:
    def __init__(self, selected, k, j, s):
        self.selected = sorted(selected)
        self.k = k
        self.j = j
        self.s = s
        self.j_combos = generate_combinations(self.selected, j)

        self.s_to_j = defaultdict(set)
        self.element_freq = defaultdict(int)
        for jc in self.j_combos:
            for s_sub in itertools.combinations(jc, s):
                sorted_s = tuple(sorted(s_sub))
                self.s_to_j[sorted_s].add(jc)
                for num in sorted_s:
                    self.element_freq[num] += 1

    def score(self, candidate, remaining_j, global_coverage):
        candidate = sorted(candidate)
        score = 0
        covered_jcs = set()

        element_bonus = sum(self.element_freq[num] for num in candidate) * 0.01

        for s_sub in itertools.combinations(candidate, self.s):
            sorted_s = tuple(sorted(s_sub))
            related_jcs = self.s_to_j.get(sorted_s, set()) & remaining_j
            for jc in related_jcs:
                if jc not in covered_jcs:
                    score += 2.0
                    covered_jcs.add(jc)
                    score += 1 / (0.5 + global_coverage.get(sorted_s, 0)) * 0.3
        return score + element_bonus

    def optimize(self, trials=100, initial_epsilon=0.4):
        best_solution = None
        best_size = float('inf')

        for trial in range(trials):
            epsilon = initial_epsilon * (1 - trial / trials)
            remaining_j = set(self.j_combos)
            global_coverage = defaultdict(int)
            solution = []
            element_freq = self.element_freq.copy()

            while remaining_j:
                candidates = set()
                while len(candidates) < 60:
                    candidates.add(tuple(sorted(random.sample(self.selected, self.k))))
                top_elements = [e for e, _ in nlargest(self.k * 2, element_freq.items(), key=lambda x: x[1])]
                for _ in range(20):
                    candidate = tuple(sorted(random.sample(top_elements, self.k)))
                    candidates.add(candidate)

                scored = [(c, self.score(c, remaining_j, global_coverage)) for c in candidates]
                top_candidates = nlargest(5, scored, key=lambda x: x[1])

                chosen = top_candidates[0][0]
                if random.random() < epsilon and len(top_candidates) > 1:
                    chosen = random.choice(top_candidates[1:3])[0]

                solution.append(chosen)
                covered_jcs = set()
                for s_sub in itertools.combinations(chosen, self.s):
                    sorted_s = tuple(sorted(s_sub))
                    for jc in self.s_to_j.get(sorted_s, set()):
                        if jc in remaining_j:
                            covered_jcs.add(jc)
                    global_coverage[sorted_s] += 1
                    for num in sorted_s:
                        element_freq[num] = max(0, element_freq[num] - 1)

                remaining_j -= covered_jcs

            essential = []
            for i in range(len(solution)):
                temp_sol = solution[:i] + solution[i + 1:]
                if validate_solution(self.j_combos, temp_sol, self.s):
                    continue
                essential.append(solution[i])
            if len(essential) < best_size:
                best_solution = essential
                best_size = len(essential)

        return best_solution

def select_random_samples(m: int, n: int) -> list[int]:
    return sorted(random.sample(range(1, m + 1), n))

def get_trials_from_n(n: int) -> int:
    if n <= 12:
        return 200
    elif n == 13:
        return 300
    elif n == 14:
        return 400
    else:
        return 500

def run_optimization(selected: list[int], k: int, j: int, s: int, n: int) -> list[list[int]]:
    trials = get_trials_from_n(n)
    optimizer = CoverageOptimizer(selected, k, j, s)
    return optimizer.optimize(trials=trials)

def save_results_to_file(m, n, k, j, s, run_id, result, db_dir="db") -> str:
    os.makedirs(db_dir, exist_ok=True)
    filename = f"{m}-{n}-{k}-{j}-{s}-{run_id}-{len(result)}.json"
    path = os.path.join(db_dir, filename)
    with open(path, "w") as f:
        json.dump(result, f)
    return filename

def load_results_from_file(filename: str, db_dir="db") -> list[list[int]]:
    path = os.path.join(db_dir, filename)
    with open(path, "r") as f:
        return json.load(f)

def delete_result_file(filename: str, db_dir="db") -> bool:
    path = os.path.join(db_dir, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def list_all_result_files(db_dir="db") -> list[str]:
    if not os.path.exists(db_dir):
        return []
    return [f for f in os.listdir(db_dir) if f.endswith(".json")]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, default=45, help="全集元素个数 (默认 45)")
    parser.add_argument("--n", type=int, default=14, help="从m中选取的元素数 (默认 14)")
    parser.add_argument("--k", type=int, default=6, help="每组组合大小 (默认 6)")
    parser.add_argument("--j", type=int, default=6, help="要求覆盖的组合大小 (默认 6)")
    parser.add_argument("--s", type=int, default=4, help="每个j组合中必须覆盖的s子组合 (默认 4)")
    parser.add_argument("--run_id", type=int, default=1, help="本次运行编号")
    args = parser.parse_args()

    start_time = time.time()

    selected = select_random_samples(args.m, args.n)
    print(f"选中的{args.n}个元素: {selected}")

    result = run_optimization(selected, args.k, args.j, args.s, args.n)

    print(f"\n最优解：{len(result)} 组")
    for i, group in enumerate(result, 1):
        print(f"组{i}: {', '.join(map(str, sorted(group)))}")

    is_valid = validate_solution(generate_combinations(selected, args.j), result, args.s)
    print(f"\n验证结果：{'成功' if is_valid else '失败'}")

    filename = save_results_to_file(args.m, args.n, args.k, args.j, args.s, args.run_id, result)
    print(f"结果已保存到: {filename}")

    end_time = time.time()
    print(f"\n总耗时：{end_time - start_time:.2f}秒")
