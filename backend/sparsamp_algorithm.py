import random
from math import ceil
import torch

def get_lower_upper_bound(cumulative_probs, v):
    lower_bound = cumulative_probs[v-1] if v > 0 else torch.tensor(0.0)
    upper_bound = cumulative_probs[v]
    return [lower_bound.item(), upper_bound.item()]

def func_mrn(k_m, n_m, r):
    result = ((k_m / n_m) + r)
    if result >= 1:
        result = result - 1
    return result

def encode_step_paper(probs, n_m, k_m, r):
    cumulative_probs = torch.tensor(probs).cumsum(0)
    r_i_m = func_mrn(k_m, n_m, r)
    token_index = (cumulative_probs > r_i_m).nonzero()[0].item()

    SE = get_lower_upper_bound(cumulative_probs, token_index)
    # 严格对齐官方 ceil 逻辑
    temp0 = ceil((SE[0] - r) * n_m)
    temp1 = ceil((SE[1] - r) * n_m)

    if k_m + r * n_m >= n_m:
        k_m = k_m - n_m - temp0
    else:
        k_m = k_m - temp0
    n_m = temp1 - temp0
    return token_index, n_m, k_m

def decode_step_paper(probs, token_idx, n_m, r):
    cumulative_probs = torch.tensor(probs).cumsum(0)
    SE = get_lower_upper_bound(cumulative_probs, token_idx)

    temp0 = ceil((SE[0] - r) * n_m)
    temp1 = ceil((SE[1] - r) * n_m)
    
    n_m_new = temp1 - temp0
    return n_m_new, temp0