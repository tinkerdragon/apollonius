from math import gcd
from fractions import Fraction

def find_simplified_fractions():
    fractions = set()
    denominators = [1, 2, 3, 4]
    
    # For each denominator, find numerators that keep the fraction in [-10, 10]
    for d in denominators:
        # Calculate the range of numerators
        # Since fraction = n/d, we need -10 <= n/d <= 10
        # Thus, -10*d <= n <= 10*d
        min_n = int(-10 * d)
        max_n = int(10 * d)
        
        for n in range(min_n, max_n + 1):
            # Skip zero numerator to avoid 0/0 or equivalent
            if n == 0:
                continue
            # Simplify the fraction
            common = gcd(n, d)
            simplified_n = n // common
            simplified_d = d // common
            # Create the fraction and check if it's within range
            frac = Fraction(simplified_n, simplified_d)
            if -10 <= frac <= 10:
                fractions.add(frac)
    
    # Convert to list and sort
    sorted_fractions = sorted(fractions)
    return [(f.numerator, f.denominator) for f in sorted_fractions]
