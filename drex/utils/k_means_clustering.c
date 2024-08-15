#include <stdio.h>
#include <stdlib.h>

// Function to calculate the binomial coefficient C(n, k)
unsigned long long binomial_coefficient(int n, int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k;
    
    unsigned long long result = 1;
    for (int i = 0; i < k; ++i) {
        result *= (n - i);
        result /= (i + 1);
    }
    return result;
}

// Function to calculate the number of combinations with repetition
unsigned long long combinations_with_replacement(int N, int X) {
    return binomial_coefficient(N + X - 1, X);
}

// Function to find the maximum value of N such that the sum of combinations does not exceed A
int find_max_N_for_sum(int max_X, unsigned long long A) {
    int max_N = 10000; // Set a reasonable upper bound for N
    int optimal_N = 0;
    unsigned long long total_combinations = 0;

    for (int N = 0; N <= max_N; ++N) {
        total_combinations = 0;
        for (int X = 2; X <= max_X; ++X) {
            unsigned long long combinations = combinations_with_replacement(N, X);
            total_combinations += combinations;
            if (total_combinations > A) {
                break;
            }
        }
        if (total_combinations <= A) {
            optimal_N = N;
        } else {
            break;
        }
    }
    if (optimal_N == 0) {
        printf("Error provided max number of combinations is too high\n");
    }

    return optimal_N;
}
