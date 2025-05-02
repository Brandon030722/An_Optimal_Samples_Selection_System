import itertools
import random
import os
import json
from collections import defaultdict
import argparse
import multiprocessing
import time

# ================= 原本已有的工具函数（不动） ===================

def generate_combinations(pool, size):
    return list(itertools.combinations(sorted(pool), size))

def validate_solution(j_combos, solution, s, min_s_covered):
    covered_s = defaultdict(int)
    for group in solution:
        for s_sub in itertools.combinations(sorted(group), s):
            covered_s[s_sub] += 1

    failed_jc = []
    for jc in j_combos:
        s_subs = list(itertools.combinations(sorted(jc), s))
        count = 0
        for s_sub in s_subs:
            if covered_s.get(s_sub, 0) >= 1:
                count += 1
        if count < min_s_covered:
            failed_jc.append(jc)
    return len(failed_jc) == 0, failed_jc

def prune_redundant_blocks(blocks, j_combos, s, min_s_covered):
    pruned = blocks.copy()
    s_coverage = defaultdict(int)
    for block in pruned:
        for s_sub in itertools.combinations(block, s):
            s_coverage[s_sub] += 1

    sorted_blocks = sorted(pruned, key=lambda blk: sum(s_coverage[s] for s in itertools.combinations(blk, s)), reverse=True)

    for block in sorted_blocks:
        temp = pruned.copy()
        temp.remove(block)
        ok, _ = validate_solution(j_combos, temp, s, min_s_covered)
        if ok:
            for s_sub in itertools.combinations(block, s):
                s_coverage[s_sub] -= 1
            pruned.remove(block)
    return pruned

def greedy_once(domain, k, j, s, min_s_covered, j_to_s_map, sample_per_round=200):
    blocks = list(itertools.combinations(domain, k))
    random.shuffle(blocks)

    j_coverage = []
    for j_subset in j_to_s_map:
        j_coverage.append({
            'subset': j_subset,
            'covered_s': set(),
            'remaining': min_s_covered
        })

    selected_blocks = []

    while True:
        all_satisfied = all(js['remaining'] <= 0 for js in j_coverage)
        if all_satisfied:
            break

        best_block = None
        best_gain = 0

        for block in random.sample(blocks, min(sample_per_round, len(blocks))):
            if block in selected_blocks:
                continue
            current_gain = 0
            for js in j_coverage:
                if js['remaining'] <= 0:
                    continue
                intersection = set(block) & set(js['subset'])
                if len(intersection) < s:
                    continue
                s_subs = [s for s in j_to_s_map[js['subset']] if set(s).issubset(intersection)]
                new_covered = sum(1 for s_sub in s_subs if s_sub not in js['covered_s'])
                gain = min(new_covered, js['remaining'])
                current_gain += gain
            if current_gain > best_gain:
                best_gain = current_gain
                best_block = block

        if best_block is None:
            break

        selected_blocks.append(best_block)
        best_block_set = set(best_block)
        for js in j_coverage:
            if js['remaining'] <= 0:
                continue
            intersection = best_block_set & set(js['subset'])
            if len(intersection) < s:
                continue
            s_subs = [s for s in j_to_s_map[js['subset']] if set(s).issubset(intersection)]
            for s_sub in s_subs:
                if s_sub not in js['covered_s']:
                    js['covered_s'].add(s_sub)
                    js['remaining'] -= 1

    all_j_subsets = list(j_to_s_map.keys())
    ok, _ = validate_solution(all_j_subsets, selected_blocks, s, min_s_covered)
    return selected_blocks if ok else None

def worker_run(args):
    return greedy_once(*args)

def multi_round_greedy(selected, k, j, s, min_s_covered, max_trials=20, sample_per_round=200):
    domain = list(selected)
    all_j_subsets = list(itertools.combinations(domain, j))
    j_to_s_map = {jc: list(itertools.combinations(jc, s)) for jc in all_j_subsets}

    args_list = [(domain, k, j, s, min_s_covered, j_to_s_map, sample_per_round) for _ in range(max_trials)]

    with multiprocessing.Pool(processes=min(12, multiprocessing.cpu_count())) as pool:
        all_results = pool.map(worker_run, args_list)

    best_solution = min((r for r in all_results if r), key=len, default=None)

    if best_solution:
        best_solution = prune_redundant_blocks(best_solution, all_j_subsets, s, min_s_covered)

    return [list(block) for block in best_solution] if best_solution else None

# ==================== 下面是新加的功能接口 =======================

def get_trials_from_n(n: int) -> int:
    # 根据n大小简单设计一个trial数策略，比如：
    return max(50, min(500, n * 10))

def run_optimization(selected: list[int],
                     k: int, j: int, s: int,
                     n: int,
                     min_s_covered: int = 1) -> list[list[int]]:
    trials = get_trials_from_n(n)
    return multi_round_greedy(
        selected, k, j, s,
        min_s_covered,          # ← 关键：传进来
        max_trials=trials
    )

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

# ==================== 结束 =======================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_per_round", type=int, default=200) # cnk=c12 5
    parser.add_argument("--m", type=int, default=45)
    parser.add_argument("--n", type=int, default=13)
    parser.add_argument("--k", type=int, default=6)
    parser.add_argument("--j", type=int, default=4)
    parser.add_argument("--s", type=int, default=4)
    parser.add_argument("--min_s_covered", type=int, default=1)
    args = parser.parse_args()
    start_time = time.time()
    full_pool = list(range(1, args.m + 1))
    selected = sorted(random.sample(full_pool, args.n))

    result = multi_round_greedy(selected, args.k, args.j, args.s, args.min_s_covered, max_trials=10, sample_per_round=args.sample_per_round)
    j_combos = list(itertools.combinations(selected, args.j))
    ok, failed = validate_solution(j_combos, result, args.s, args.min_s_covered)

    print("选中样本:", selected)
    print("最优组合数:", len(result))
    for i, group in enumerate(result, 1):
        print(f"组{i}: {group}")
    print("验证结果:", "✅ 成功" if ok else "❌ 失败")
    end_time = time.time()
    print("time:",end_time - start_time)