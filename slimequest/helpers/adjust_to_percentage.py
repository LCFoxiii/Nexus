def SQAdjustToPercentage(a, b, divider) -> float:
    diff = a - b
    
    if diff <= 0:
        return 0.0

    return diff / divider