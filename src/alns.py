from src.operators import random_removal, worst_removal, overlap_removal, greedy_insertion, regret_insertion
from src.cost_function import augmented_cost_function

def alns(initial_solution, customers, vehicles, parameters, weights, max_iter=100):
    destroy_operators = [random_removal, worst_removal, overlap_removal]
    repair_operators = [greedy_insertion, regret_insertion]

    best_solution = initial_solution.copy()
    current_solution = initial_solution.copy()
    best_cost = augmented_cost_function(customers, vehicles, initial_solution, parameters, weights)
    
    for _ in range(max_iter):
        destroy_op = random.choice(destroy_operators)
        repair_op = random.choice(repair_operators)
        
        destroyed_solution, removed_customers = destroy_op(current_solution, n_remove=3)
        repaired_solution = repair_op(destroyed_solution, removed_customers, customers, vehicles)
        current_cost = augmented_cost_function(customers, vehicles, repaired_solution, parameters, weights)
        
        if current_cost < best_cost:
            best_solution = repaired_solution
            best_cost = current_cost
        
        current_solution = repaired_solution
    return best_solution
