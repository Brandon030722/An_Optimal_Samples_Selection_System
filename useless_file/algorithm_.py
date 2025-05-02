# algorithm_.py  – 适配 ws.py
from main import run_optimization
from typing import List

def generate_SA(n: List[int], k: int, j: int, s: int,
                min_s_covered: int = 1) -> List[List[int]]:
    selected = sorted(n)
    result = run_optimization(
               selected, k, j, s,
               len(selected),
               min_s_covered
        )
    return [list(group) for group in result]   # tuple → list