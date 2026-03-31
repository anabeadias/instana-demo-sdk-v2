def calculate_total(items):
    total = 0
    for item in items:
        total += item.quantity * 100  # preço fixo mock
    return total
