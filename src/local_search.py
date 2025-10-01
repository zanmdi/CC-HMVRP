from copy import deepcopy
import random
from src.cost_function import augmented_cost_function

def local_search(solution, customers, vehicles, parameters, weights):
    """
    Local search procedure with relocate, exchange, and 2-opt moves.
    Applies intra-route and inter-route relocate, inter-route exchange,
    and inter-route 2-opt. Accepts only improving moves.
    """
    best_solution = deepcopy(solution)
    best_cost = augmented_cost_function(customers, vehicles, best_solution, parameters, weights)
    improved = True

    while improved:
        improved = False

        # === 1. Relocate (intra & inter) ===
        for v1, route1 in best_solution.items():
            for i in range(len(route1)):
                customer = route1[i]
                # Try intra-route reinsertion
                for j in range(len(route1)):
                    if i != j:
                        new_solution = deepcopy(best_solution)
                        new_solution[v1].remove(customer)
                        new_solution[v1].insert(j, customer)
                        new_cost = augmented_cost_function(customers, vehicles, new_solution, parameters, weights)
                        if new_cost < best_cost:
                            best_solution, best_cost = new_solution, new_cost
                            improved = True
                # Try inter-route reinsertion
                for v2, route2 in best_solution.items():
                    if v1 != v2:
                        for j in range(len(route2) + 1):
                            new_solution = deepcopy(best_solution)
                            new_solution[v1].remove(customer)
                            new_solution[v2].insert(j, customer)
                            new_cost = augmented_cost_function(customers, vehicles, new_solution, parameters, weights)
                            if new_cost < best_cost:
                                best_solution, best_cost = new_solution, new_cost
                                improved = True

        # === 2. Exchange (inter-route) ===
        for v1, route1 in best_solution.items():
            for v2, route2 in best_solution.items():
                if v1 < v2 and route1 and route2:
                    for i in range(len(route1)):
                        for j in range(len(route2)):
                            new_solution = deepcopy(best_solution)
                            new_solution[v1][i], new_solution[v2][j] = new_solution[v2][j], new_solution[v1][i]
                            new_cost = augmented_cost_function(customers, vehicles, new_solution, parameters, weights)
                            if new_cost < best_cost:
                                best_solution, best_cost = new_solution, new_cost
                                improved = True

        # === 3. 2-opt (inter-route) ===
        for v1, route1 in best_solution.items():
            for v2, route2 in best_solution.items():
                if v1 < v2 and len(route1) > 1 and len(route2) > 1:
                    for i in range(1, len(route1)):
                        for j in range(1, len(route2)):
                            new_solution = deepcopy(best_solution)
                            new_route1 = route1[:i] + route2[j:]
                            new_route2 = route2[:j] + route1[i:]
                            new_solution[v1] = new_route1
                            new_solution[v2] = new_route2
                            new_cost = augmented_cost_function(customers, vehicles, new_solution, parameters, weights)
                            if new_cost < best_cost:
                                best_solution, best_cost = new_solution, new_cost
                                improved = True

    return best_solution, best_cost
