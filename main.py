# -*- coding: utf-8 -*-
import itertools
import random
import os
import json
from collections import defaultdict
import argparse
import multiprocessing
import time
import math
import sys
import datetime

# ==============================================================================
# 核心函数区域 (基于用户提供的最新代码, 但替换了剪枝函数)
# ==============================================================================

def generate_combinations(pool, size):
    """生成组合列表"""
    if not pool or size > len(pool) or size < 0: return []
    try:
        unique_sorted_pool = sorted(list(set(pool)))
        if size > len(unique_sorted_pool): return []
        int_pool = [int(x) for x in unique_sorted_pool]
        return [list(combo) for combo in itertools.combinations(int_pool, size)]
    except (TypeError, ValueError) as e:
        print(f"错误: generate_combinations 输入 pool={pool} 包含非整数或不可排序类型? {e}", file=sys.stderr)
        return []

def validate_solution(j_combos, solution, s, min_s_covered):
    """验证解是否满足覆盖条件"""
    if not isinstance(solution, list): return False, j_combos
    if not solution: return len(j_combos) == 0 or min_s_covered <= 0, [] if len(j_combos) == 0 or min_s_covered <= 0 else j_combos
    covered_s_presence = set()
    for group in solution:
        try:
            group_set = set(int(x) for x in group)
            if len(group_set) >= s:
                 for s_sub in itertools.combinations(sorted(list(group_set)), s):
                     covered_s_presence.add(tuple(s_sub))
        except (TypeError, ValueError): continue
    failed_jc = []
    if not hasattr(j_combos, '__iter__'): return False, []
    for jc in j_combos:
        count = 0
        try:
            jc_set = set(int(x) for x in jc)
            if len(jc_set) >= s:
                 for s_sub in itertools.combinations(sorted(list(jc_set)), s):
                     if tuple(s_sub) in covered_s_presence: count += 1
            elif min_s_covered > 0: count = -1
            if count < min_s_covered: failed_jc.append(list(jc))
        except (TypeError, ValueError): failed_jc.append(list(jc)); continue
    return len(failed_jc) == 0, failed_jc


# ==============================================================================
#  *** 使用新的、更简单的剪枝函数 ***
# ==============================================================================
def prune_redundant_blocks_simple_shuffle(blocks, j_combos, s, min_s_covered):
    """更简单、可能更健壮的剪枝：随机顺序尝试移除，成功则重试。"""
    if not blocks: return []

    pruned = [list(b) for b in blocks] # 确保是列表的列表
    j_combos_list = [list(jc) for jc in j_combos] # 确保 jc 也是列表

    # 初始验证 (可选但推荐)
    initial_ok, _ = validate_solution(j_combos_list, pruned, s, min_s_covered)
    if not initial_ok:
        print("警告: 传入剪枝函数的初始解本身无效！将返回原始解。", file=sys.stderr)
        return blocks # 返回原始未剪枝解

    while True: # 持续循环直到没有块在一轮中被移除
        block_removed_in_pass = False
        if not pruned: break # 如果剪枝完了，退出

        indices = list(range(len(pruned)))
        random.shuffle(indices) # 随机化移除尝试顺序

        # 遍历随机打乱的索引
        for i in indices:
            # 获取要测试的块的当前索引 (因为列表长度可能变化)
            # 由于每次移除后都会 break 并重新开始 while 循环，
            # 所以 indices 里的索引 i 对应的是本轮开始时的 pruned 列表。
            # 直接使用索引 i 是安全的。
            if i >= len(pruned): continue # 理论上不应发生

            # 创建临时解（不包含当前索引 i 的块）
            temp_solution = pruned[:i] + pruned[i+1:]

            # 验证临时解
            ok, _ = validate_solution(j_combos_list, temp_solution, s, min_s_covered)

            if ok:
                # 移除成功
                pruned.pop(i)
                block_removed_in_pass = True
                # print(f"  (剪枝成功，剩余 {len(pruned)} 块)") # Debug
                # 因为列表已修改，必须重新开始 shuffle 和检查
                break # 跳出内层 for 循环，重新开始外层 while 循环

        # 如果完成了一轮完整的随机尝试而没有移除任何块，则剪枝结束
        if not block_removed_in_pass:
            break # 退出外层 while 循环

    return pruned
# ==============================================================================
# 结束新的剪枝函数
# ==============================================================================


def greedy_once(domain, k, j, s, min_s_covered, j_to_s_map, sample_per_round=200):
    """单次贪心算法 (移除了内部验证调用)"""
    try:
        all_potential_blocks = list(itertools.combinations(domain, k))
        if not all_potential_blocks and min_s_covered > 0 and j_to_s_map: return None
    except Exception as e: print(f"错误: 生成 k-块时出错: {e}", file=sys.stderr); return None

    random.shuffle(all_potential_blocks)

    j_coverage = [{'subset': jc, 'covered_s': set(), 'remaining': min_s_covered} for jc in j_to_s_map.keys()]
    selected_blocks = []; selected_blocks_tuples_set = set()
    available_blocks = all_potential_blocks

    iteration = 0; max_iterations = len(all_potential_blocks) + len(j_coverage) + 10

    while iteration < max_iterations:
        iteration += 1
        all_satisfied = all(js['remaining'] <= 0 for js in j_coverage)
        if all_satisfied: break
        if not available_blocks: break

        best_block_chosen_list = None; best_gain = -1.0
        sample_size = min(sample_per_round, len(available_blocks))
        if sample_size <= 0: break
        candidates_to_evaluate_list = random.sample(available_blocks, sample_size)
        if not candidates_to_evaluate_list: break

        for block_candidate_list in candidates_to_evaluate_list:
            try: block_candidate_tuple = tuple(sorted(block_candidate_list));
            except TypeError: continue
            if block_candidate_tuple in selected_blocks_tuples_set: continue
            current_gain = 0.0; block_set = set(block_candidate_tuple); s_subs_in_block = set()
            try:
                if len(block_set) >= s: s_subs_in_block = set(itertools.combinations(block_candidate_tuple, s))
            except TypeError: continue
            if not s_subs_in_block: continue
            for js in j_coverage:
                if js['remaining'] <= 0: continue
                jc_tuple = js['subset']; newly_covered_count = 0; jc_s_subs = j_to_s_map.get(jc_tuple, set())
                for s_sub_tuple in s_subs_in_block:
                    try: is_covered = s_sub_tuple in js['covered_s']
                    except TypeError: is_covered = False
                    if s_sub_tuple in jc_s_subs and not is_covered: newly_covered_count += 1
                if newly_covered_count > 0: gain_for_this_jc = min(newly_covered_count, js['remaining']) * float(js['remaining']); current_gain += gain_for_this_jc
            if current_gain > best_gain: best_gain = current_gain; best_block_chosen_list = block_candidate_list

        if best_block_chosen_list is None:
            best_fallback_list = None; max_reduction = 0
            for block_candidate_list in candidates_to_evaluate_list:
                 try: block_tuple = tuple(sorted(block_candidate_list));
                 except TypeError: continue
                 if block_tuple in selected_blocks_tuples_set: continue
                 block_set = set(block_tuple); reduction = 0
                 try: s_subs_in_block = set(itertools.combinations(block_tuple,s)) if len(block_set) >= s else set()
                 except TypeError: continue
                 if not s_subs_in_block: continue
                 for js in j_coverage:
                     if js['remaining'] > 0:
                          jc_tuple = js['subset']; jc_s_subs = j_to_s_map.get(jc_tuple, set())
                          for s_sub_tuple in s_subs_in_block:
                              try: is_covered = s_sub_tuple in js['covered_s']
                              except TypeError: is_covered = False
                              if s_sub_tuple in jc_s_subs and not is_covered: reduction += 1
                 if reduction > max_reduction: max_reduction = reduction; best_fallback_list = block_candidate_list
            if best_fallback_list: best_block_chosen_list = best_fallback_list
            else: break
        if best_block_chosen_list is None: break

        best_block_tuple = tuple(sorted(best_block_chosen_list))
        if best_block_tuple in selected_blocks_tuples_set: continue

        selected_blocks.append(best_block_chosen_list); selected_blocks_tuples_set.add(best_block_tuple)
        try: available_blocks.remove(best_block_chosen_list)
        except ValueError: pass

        try: s_subs_in_chosen_block = set(itertools.combinations(best_block_tuple, s)) if len(best_block_tuple) >= s else set()
        except TypeError: s_subs_in_chosen_block = set()

        if s_subs_in_chosen_block:
            for js in j_coverage:
                if js['remaining'] <= 0: continue
                jc_tuple = js['subset']; jc_s_subs = j_to_s_map.get(jc_tuple, set())
                for s_sub_tuple in s_subs_in_chosen_block:
                     if s_sub_tuple in jc_s_subs:
                          try:
                              if s_sub_tuple not in js['covered_s']: js['covered_s'].add(s_sub_tuple); js['remaining'] = max(0, js['remaining'] - 1)
                          except TypeError: continue

    # --- 循环结束 ---
    final_all_satisfied = all(js['remaining'] <= 0 for js in j_coverage)

    if final_all_satisfied:
        return selected_blocks
    else:
        print(f"警告: greedy_once 结束但未满足所有覆盖条件。", file=sys.stderr)
        return None

def worker_run(args):
    """多进程工作函数"""
    pid = os.getpid()
    try:
        return greedy_once(*args)
    except Exception as e:
        print(f"!!!! 工作进程 {pid} 发生严重错误: {e} !!!!", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

# ==============================================================================
#  *** 修改 multi_round_greedy_with_prune 函数 ***
#  现在调用新的剪枝函数 prune_redundant_blocks_simple_shuffle
# ==============================================================================
def multi_round_greedy_with_prune(selected, k, j, s, min_s_covered, max_trials=20, sample_per_round=200, prune_active=True):
    """执行多轮贪心，并根据 prune_active 决定是否进行一次 *新的* 剪枝"""
    domain = list(selected); n = len(domain)
    all_j_subsets = []; j_to_s_map = {}
    # --- 预计算 ---
    try:
        if not (n >= j >= s >= 0 and n >= k >= s): return None
        all_j_subsets = list(itertools.combinations(domain, j))
        if not all_j_subsets and min_s_covered > 0: return []
        if all_j_subsets:
             j_to_s_map = {jc: set(itertools.combinations(jc, s)) for jc in all_j_subsets}
    except Exception as e: print(f" 预计算时出错: {e}"); return None
    # --- 结束预计算 ---
    if not all_j_subsets and min_s_covered > 0: return []
    # --- 并行贪心 ---
    start_greedy = time.time()
    args_list = [(domain, k, j, s, min_s_covered, j_to_s_map, sample_per_round) for _ in range(max_trials)]
    best_initial_solution = None
    num_workers = min(max_trials, multiprocessing.cpu_count(), 16)
    if max_trials <= 0: valid_results = []
    else:
        try:
            with multiprocessing.Pool(processes=num_workers, maxtasksperchild=1) as pool:
                all_results = pool.map(worker_run, args_list)
            valid_results = [r for r in all_results if r is not None]
        except Exception as e: print(f" 多进程错误: {e}"); return None
    greedy_duration = time.time() - start_greedy
    if not valid_results:
        print(f"    所有贪心试验失败 ({greedy_duration:.2f}s)。")
        return None
    best_initial_solution = min(valid_results, key=len)
    print(f"    贪心完成 ({greedy_duration:.2f}s). 最佳初始解: {len(best_initial_solution)} 块.", end='')
    # --- 结束并行贪心 ---
    # --- 剪枝 ---
    final_solution = best_initial_solution
    if prune_active and best_initial_solution:
        start_prune = time.time()
        # *** 调用新的简单随机 shuffle 剪枝函数 ***
        pruned_solution = prune_redundant_blocks_simple_shuffle(best_initial_solution, all_j_subsets, s, min_s_covered)
        prune_duration = time.time() - start_prune
        # 检查剪枝后的有效性
        pruned_ok, _ = validate_solution(all_j_subsets, pruned_solution, s, min_s_covered)
        if not pruned_ok:
             print(f" 警告: (简单)剪枝后的解未能通过验证！将返回剪枝前的解 ({len(best_initial_solution)} 块)。", end='')
             final_solution = best_initial_solution # 回退
        else:
             print(f" 剪枝完成 ({prune_duration:.2f}s). 剪枝后: {len(pruned_solution)} 块.")
             final_solution = pruned_solution
    elif prune_active and not best_initial_solution:
         print(" (无初始解，无法剪枝)")
    else:
         print(" (跳过剪枝)")
    # --- 结束剪枝 ---
    return [list(block) for block in final_solution] if final_solution is not None else None


# ==============================================================================
# 文件操作接口函数 (保持不变)
# ==============================================================================
def save_results_to_file(m, n, k, j, s, run_id, result, selected_samples, db_dir="db") -> str:
    try:
        os.makedirs(db_dir, exist_ok=True)
        result_count = len(result) if result else 0
        filename = f"{m}-{n}-{k}-{j}-{s}-{run_id}-{result_count}.json"
        path = os.path.join(db_dir, filename)
        data_to_save = {
            "params": {"m": m, "n": n, "k": k, "j": j, "s": s}, "run_id": run_id,
            "selected_samples": selected_samples, "result_groups": result if result else [],
            "group_count": result_count, "save_time": datetime.datetime.now().isoformat()
        }
        with open(path, "w", encoding='utf-8') as f: json.dump(data_to_save, f, indent=4)
        print(f"结果已保存到: {path}")
        return filename
    except Exception as e: print(f"错误: 保存文件时发生错误: {e}", file=sys.stderr); return ""

def load_results_from_file(filename: str, db_dir="db") -> dict | None:
    path = os.path.join(db_dir, filename)
    if not os.path.exists(path): return None
    try:
        with open(path, "r", encoding='utf-8') as f: data = json.load(f)
        if isinstance(data, dict) and "result_groups" in data: return data
        else: print(f"错误: 文件 {filename} 格式不正确。", file=sys.stderr); return None
    except Exception as e: print(f"错误: 加载文件 {filename} 时发生错误: {e}", file=sys.stderr); return None

def delete_result_file(filename: str, db_dir="db") -> bool:
    path = os.path.join(db_dir, filename)
    try:
        if os.path.exists(path): os.remove(path); print(f"文件已删除: {filename}"); return True
        else: return False
    except Exception as e: print(f"错误: 删除文件 {filename} 时出错: {e}", file=sys.stderr); return False

def list_all_result_files(db_dir="db") -> list[str]:
    if not os.path.exists(db_dir) or not os.path.isdir(db_dir): return []
    files = []
    try:
        for f in os.listdir(db_dir):
            parts = f.split('-')
            if f.endswith(".json") and len(parts) == 7:
                try: int(parts[0]); int(parts[1]); int(parts[2]); int(parts[3]); int(parts[4]); int(parts[6].split('.')[0]); files.append(f)
                except (ValueError, IndexError): continue
    except OSError as e: print(f"错误: 读取目录 {db_dir} 时出错: {e}", file=sys.stderr); return []
    return sorted(files)

# ==============================================================================
# 动态生成努力级别的函数 (保持不变)
# ==============================================================================
def get_adaptive_effort_levels(n_val, k_val, time_limit):
    levels = []; nCk = 0
    try:
        if n_val >= k_val >= 0: nCk = math.comb(n_val, k_val)
        size_factor = math.log(nCk + 1.1) if nCk > 0 and nCk < 10**7 else n_val
    except (ValueError, OverflowError): size_factor = n_val
    if n_val <= 10:
        base_trials = 8; sampling = max(50, int(nCk * 0.9)) if nCk > 0 else 100
        num_levels = 3; trial_multiplier = 2.0; sampling_multiplier=1.0; prune_start_level = 1
        current_sampling = sampling
    elif n_val <= 15:
        base_trials = 8; sampling = max(100, int(nCk * 0.6)) if nCk > 0 else 200
        num_levels = 4; trial_multiplier = 2.0; sampling_multiplier = 1.5; prune_start_level = 2
        current_sampling = sampling
    else: # n >= 16
        base_trials = 4; sampling_cap = max(100, int(nCk * 0.15)) if nCk > 1000 else 250
        base_sampling_abs = min(250, sampling_cap)
        num_levels = 5; trial_multiplier = 1.8; sampling_multiplier = 1.8; prune_start_level = 3
        current_sampling = base_sampling_abs
    current_trials = base_trials
    for i in range(num_levels):
        actual_sampling = int(current_sampling)
        try:
            num_k_blocks_possible = math.comb(n_val, k_val) if n_val >= k_val else 0
            actual_sampling = min(int(current_sampling), num_k_blocks_possible) if num_k_blocks_possible > 0 else int(current_sampling)
        except (ValueError, OverflowError): pass
        level_params = {
            'label': f'级别 {i+1}', 'max_trials': int(current_trials),
            'sample_per_round': max(1, actual_sampling) if nCk > 0 else 1,
            'prune': (i + 1 >= prune_start_level)
        }
        levels.append(level_params)
        current_trials *= trial_multiplier
        next_sampling_raw = current_sampling * sampling_multiplier
        if n_val > 15 and nCk > 0: current_sampling = min(int(next_sampling_raw), int(nCk * 0.8), 4000)
        elif nCk > 0 : current_sampling = min(int(next_sampling_raw), nCk, 6000)
        else: current_sampling = int(next_sampling_raw)
        current_sampling = max(1, current_sampling)
    return levels

# ==============================================================================
# 主程序入口
# ==============================================================================
if __name__ == "__main__":
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(description="自适应最优样本选择系统")
    # 参数定义...
    parser.add_argument("--m", type=int, default=45, help="可用样本总数 M")
    parser.add_argument("--n", type=int, required=True, help="从中选择的样本数 N")
    parser.add_argument("--k", type=int, required=True, help="最终选择组的大小 K")
    parser.add_argument("--j", type=int, required=True, help="要检查的中间组的大小 J")
    parser.add_argument("--s", type=int, required=True, help="j组内需要覆盖的子组大小 S")
    parser.add_argument("--min_s_covered", type=int, default=1, help="每个j组必须覆盖的最小s子组数")
    parser.add_argument("--selected_samples", type=int, nargs='+', default=None, help="手动指定 n 个样本编号 (1 到 m)")
    parser.add_argument("--time_limit", type=float, default=55.0, help="求解过程的目标时间限制（秒）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，用于复现")
    parser.add_argument("--db_dir", type=str, default="db_results", help="存储结果文件的目录")
    parser.add_argument("--save", action='store_true', help="是否将最终结果保存到文件")
    parser.add_argument("--run_id", type=str, default=None, help="自定义本次运行的ID (用于文件名)")

    args = parser.parse_args()

    # --- 输入验证 ---
    print("开始参数验证...")
    valid = True; error_msg = []
    # ... (验证逻辑) ...
    if not (args.n >= 1 and args.k >= 1 and args.j >= 1 and args.s >= 0): error_msg.append("n,k,j>=1, s>=0"); valid = False
    if not (args.n >= args.k): error_msg.append(f"n({args.n})>=k({args.k})"); valid = False
    if not (args.n >= args.j): error_msg.append(f"n({args.n})>=j({args.j})"); valid = False
    if not (args.j >= args.s): error_msg.append(f"j({args.j})>=s({args.s})"); valid = False
    if not (args.k >= args.s): error_msg.append(f"k({args.k})>=s({args.s})"); valid = False
    if args.min_s_covered < 0: error_msg.append("min_s_covered>=0"); valid = False
    try:
        if args.j >= args.s >= 0: max_s_in_j = math.comb(args.j, args.s);
        elif args.min_s_covered > 0: error_msg.append(f"j<s 或 s<0 时无法满足 min_s_covered>0"); valid = False
        else: max_s_in_j = 0
        if args.j >= args.s >= 0 and args.min_s_covered > max_s_in_j: error_msg.append(f"min_s_covered({args.min_s_covered})>jCs({max_s_in_j})"); valid = False
    except (ValueError, OverflowError) as e: error_msg.append(f"计算 jCs 出错: {e}"); valid = False
    if args.selected_samples:
        if len(args.selected_samples) != args.n: error_msg.append(f"指定的样本数({len(args.selected_samples)})与n({args.n})不符"); valid = False
        if len(set(args.selected_samples)) != args.n: error_msg.append("指定的样本必须唯一"); valid = False
        if not all(1 <= sample <= args.m for sample in args.selected_samples): error_msg.append(f"指定的样本必须在[1, {args.m}]范围内"); valid = False
    if not valid: print("参数验证失败:"); [print(f"  - {msg}") for msg in error_msg]; sys.exit(1)
    print("参数验证通过。")
    # --- 结束验证 ---

    # --- 随机种子与样本选择 ---
    if args.seed is not None: random.seed(args.seed); print(f"使用随机种子: {args.seed}")
    start_time = time.time()
    if args.selected_samples:
        selected = sorted(list(set(args.selected_samples)))
        print(f"\n使用用户提供的样本 (n={args.n}): {selected}")
    else:
        full_pool = list(range(1, args.m + 1))
        if args.n > args.m: print(f"错误: n ({args.n}) > m ({args.m})。"); sys.exit(1)
        selected = sorted(random.sample(full_pool, args.n))
        print(f"\n从 1 到 {args.m} 中随机选择的样本 (n={args.n}): {selected}")
    # --- 结束样本选择 ---

    # --- 自适应求解过程 ---
    TIME_LIMIT = args.time_limit
    SAFETY_MARGIN = 5.0 # 秒

    EFFORT_LEVELS = get_adaptive_effort_levels(args.n, args.k, args.time_limit)

    overall_best_solution = None
    overall_best_len = float('inf')
    start_adaptive_time = time.time()
    last_level_duration = 3.0 # 初始估计

    print(f"\n开始自适应求解 (目标时间: {TIME_LIMIT:.1f}s)...")

    for i, level in enumerate(EFFORT_LEVELS):
        current_loop_start_time = time.time()
        elapsed_adaptive_time = current_loop_start_time - start_adaptive_time
        time_left = TIME_LIMIT - elapsed_adaptive_time

        print(f"\n-- 尝试 Effort Level {i+1} ({level['label']}) -- [已用时间: {elapsed_adaptive_time:.1f}s]")

        # 时间检查
        estimated_next_duration = last_level_duration * 1.1
        if i > 0 and time_left < estimated_next_duration + SAFETY_MARGIN :
             print(f"基于上一级别耗时 ({last_level_duration:.1f}s)，预估剩余时间不足，停止尝试更高级别。")
             break
        elif time_left < SAFETY_MARGIN:
            print("剩余时间不足，停止尝试更高级别。")
            break

        trials = level['max_trials']
        sampling = level['sample_per_round']
        prune_active = level['prune']

        print(f"    运行参数: max_trials={trials}, sample_per_round={sampling}, prune_active={prune_active}")
        level_start_run = time.time()

        # *** 调用包含并行和一次（新）剪枝的函数 ***
        # 注意 multi_round_greedy_with_prune 内部调用的是 prune_redundant_blocks_simple_shuffle
        current_solution = multi_round_greedy_with_prune(
            selected, args.k, args.j, args.s, args.min_s_covered,
            max_trials=trials,
            sample_per_round=sampling,
            prune_active=prune_active
        )
        level_duration = time.time() - level_start_run

        if current_solution is not None:
            current_len = len(current_solution)
            # print(f"    级别 {i+1} 求解总耗时: {level_duration:.2f}s") # 移除内部打印
            if current_len < overall_best_len:
                print(f"  >>> 新最佳解: {current_len} 组 (优于 {overall_best_len if overall_best_len != float('inf') else '无'})")
                overall_best_solution = current_solution
                overall_best_len = current_len
            # else: print(f"  找到解: {current_len} 组 (未优于当前最佳 {overall_best_len})") # 移除
        else:
            print(f"    当前级别未能找到有效解或出错 ({level_duration:.2f}s)。")

        last_level_duration = level_duration # 更新耗时

    # --- 结束自适应求解 ---

    end_time = time.time()
    total_duration = end_time - start_time

    # --- 最终结果报告 ---
    print("\n" + "="*20 + " 自适应求解最终结果 " + "="*20)
    run_id_str = args.run_id if args.run_id else datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    if overall_best_solution is not None:
        print(f"找到的最佳 k={args.k} 组数量: {overall_best_len}")
        final_solution_list_of_lists = overall_best_solution
        formatted_result = []
        for group in final_solution_list_of_lists:
             try:
                 sorted_group = sorted([int(sample) for sample in group])
                 formatted_group_str = [f"{sample:02d}" for sample in sorted_group]
                 formatted_result.append(formatted_group_str)
             except (ValueError, TypeError) as fmt_e: continue
        formatted_result.sort()
        limit_print = 30
        if len(formatted_result) > limit_print:
            print(f"结果组 (共 {len(formatted_result)} 组，显示前 {limit_print//2} 和后 {limit_print//2}):")
            for i, group_str_list in enumerate(formatted_result[:limit_print//2], 1): print(f"  组 {i:3d}: ({', '.join(group_str_list)})")
            print(f"  ... (省略 {len(formatted_result) - limit_print} 组) ...")
            for i, group_str_list in enumerate(formatted_result[-limit_print//2:], len(formatted_result) - limit_print//2 + 1): print(f"  组 {i:3d}: ({', '.join(group_str_list)})")
        else:
             print(f"结果组 (共 {len(formatted_result)} 组):")
             for i, group_str_list in enumerate(formatted_result, 1): print(f"  组 {i:3d}: ({', '.join(group_str_list)})")

        # 最终验证
        print("\n最终验证运行...")
        try:
             j_combos_final = list(itertools.combinations(selected, args.j))
             # 确保传递的是列表的列表
             is_valid_final, failed_list = validate_solution(j_combos_final, final_solution_list_of_lists, args.s, args.min_s_covered)
             print(f"验证检查: {'✅ 解是有效的' if is_valid_final else f'❌ 解是无效的 (失败 {len(failed_list)} 个 jc)'}")
        except Exception as val_e: print(f"验证过程中出错: {val_e}")

        # 保存结果
        if args.save:
             save_results_to_file(args.m, args.n, args.k, args.j, args.s, run_id_str, final_solution_list_of_lists, selected, args.db_dir)

    else:
        print(f"未能在给定时间内为参数找到有效解。")
        print("验证检查: ❌ 未找到解")

    print(f"\n总执行时间: {total_duration:.2f} 秒.")
    print(f"(目标时间限制: {args.time_limit:.1f} 秒)")
    print("="*54)