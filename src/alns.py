import numpy as np
from src.operators import random_removal, worst_removal, overlap_removal, worst_route_removal, greedy_insertion, regret_insertion
from src.cost_function import augmented_cost_function
import random

def roulette_wheel_selection(operators, weights):
    """Select an operator based on a roulette wheel mechanism."""
    cumulative_weights = np.cumsum(weights)
    r = random.uniform(0, cumulative_weights[-1])
    for i, cw in enumerate(cumulative_weights):
        if r <= cw:
            return operators[i]

def update_weights(weights, scores, smoothing_factor):
    """Update operator weights based on scores."""
    for i in range(len(weights)):
        weights[i] = smoothing_factor * weights[i] + (1 - smoothing_factor) * scores[i]
    # Normalize weights to sum to 1
    total_weight = sum(weights)
    return [w / total_weight for w in weights]

def alns(initial_solution, customers, vehicles, parameters, weights, max_iter=100, smoothing_factor=0.7):
    # Define destroy and repair operators
    destroy_operators = [random_removal, worst_removal, overlap_removal, worst_route_removal]
    repair_operators = [greedy_insertion, regret_insertion]
    
    # Initialize weights and scores for destroy and repair operators
    destroy_weights = [1.0 / len(destroy_operators)] * len(destroy_operators)
    repair_weights = [1.0 / len(repair_operators)] * len(repair_operators)
    destroy_scores = [0] * len(destroy_operators)
    repair_scores = [0] * len(repair_operators)
    
    # Reward parameters
    reward_best = 10  # Reward for finding a new best solution
    reward_improve = 5  # Reward for improving the current solution
    reward_accept = 2  # Reward for accepting a worse solution

    best_solution = initial_solution.copy()
    current_solution = initial_solution.copy()
    best_cost = augmented_cost_function(customers, vehicles, initial_solution, parameters, weights)
    
    for _ in range(max_iter):
        # Select destroy and repair operators using roulette wheel mechanism
        destroy_op = roulette_wheel_selection(destroy_operators, destroy_weights)
        repair_op = roulette_wheel_selection(repair_operators, repair_weights)
        
        # Apply destroy and repair operators
        destroyed_solution, removed_customers = destroy_op(current_solution, n_remove=3)
        repaired_solution = repair_op(destroyed_solution, removed_customers, customers, vehicles)
        current_cost = augmented_cost_function(customers, vehicles, repaired_solution, parameters, weights)
        
        # Update scores based on solution quality
        if current_cost < best_cost:
            best_solution = repaired_solution
            best_cost = current_cost
            destroy_scores[destroy_operators.index(destroy_op)] += reward_best
            repair_scores[repair_operators.index(repair_op)] += reward_best
        elif current_cost < augmented_cost_function(customers, vehicles, current_solution, parameters, weights):
            destroy_scores[destroy_operators.index(destroy_op)] += reward_improve
            repair_scores[repair_operators.index(repair_op)] += reward_improve
        else:
            destroy_scores[destroy_operators.index(destroy_op)] += reward_accept
            repair_scores[repair_operators.index(repair_op)] += reward_accept
        
        # Update weights using the scores
        destroy_weights = update_weights(destroy_weights, destroy_scores, smoothing_factor)
        repair_weights = update_weights(repair_weights, repair_scores, smoothing_factor)
        
        # Set the current solution to the repaired solution
        current_solution = repaired_solution
    
    return best_solution
