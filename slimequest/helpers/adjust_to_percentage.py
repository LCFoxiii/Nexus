def SQAdjustToPercentage(a, b, divider):
    return round(max(a - b, 0) / divider * 100)