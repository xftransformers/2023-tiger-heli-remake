def clamp(val: float, min_: float, max_: float) -> float:
    lower_clamp = max(val, min_)
    return min(lower_clamp, max_)

