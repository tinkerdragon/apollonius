from fractions import Fraction

def find_simplified_fractions():
    fractions = set()
    denominators = [1, 2, 3, 4]
    
    # Iterate over each denominator
    for d in denominators:
        # Range of numerators ensuring -10 <= n/d <= 10
        min_n = -10 * d
        max_n = 10 * d
        
        # Generate fractions for all numerators in range
        for n in range(min_n, max_n + 1):
            if n == 0:
                continue  # Skip zero to match original behavior
            fractions.add(Fraction(n, d))
    
    # Sort fractions and convert to floats
    sorted_fractions = sorted(fractions)
    return [float(f) for f in sorted_fractions]
