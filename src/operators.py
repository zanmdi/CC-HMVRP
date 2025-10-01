import random
import numpy as np

# --- Destroy Operators ---

def random_removal(solution, n_remove):
    """
    Randomly removes n customers from the current solution.
    """
    destroyed_solution = solution.copy()
    removed_customers = []
    for vehicle, customers in destroyed_solution.items():
        to_remove = random.sample(customers, min(n_remove, len(customers)))
        for customer in to_remove:
            customers.remove(customer)
            removed_customers.append(customer)
    return destroyed_solution, removed_customers


def worst_removal(solution, cost_function, customers, vehicles, weights, n_remove):
    """
    Removes the customers with the worst insertion cost.
    """
    customer_costs = []
    for vehicle, assigned_customers in solution.items():
        for customer_id in assigned_customers:
            temp_solution = solution.copy()
            temp_solution[vehicle].remove(customer_id)
            cost = cost_function(temp_solution, customers, vehicles, weights)
            customer_costs.append((customer_id, cost))
    
    # Sort customers by their cost impact
    customer_costs.sort(key=lambda x: x[1], reverse=True)
    to_remove = [customer for customer, _ in customer_costs[:n_remove]]
    
    destroyed_solution = solution.copy()
    removed_customers = []
    for vehicle in destroyed_solution:
        destroyed_solution[vehicle] = [c for c in destroyed_solution[vehicle] if c not in to_remove]
        removed_customers.extend(to_remove)
    return destroyed_solution, removed_customers


def overlap_removal(solution, customers, overlap_costs, n_remove):
    """
    Removes customers with the highest overlap costs.
    """
    customer_overlap = [(c_id, overlap_costs[c_id]) for c_id in overlap_costs]
    customer_overlap.sort(key=lambda x: x[1], reverse=True)

    to_remove = [c_id for c_id, _ in customer_overlap[:n_remove]]
    destroyed_solution = solution.copy()
    removed_customers = []
    for vehicle in destroyed_solution:
        destroyed_solution[vehicle] = [c for c in destroyed_solution[vehicle] if c not in to_remove]
        removed_customers.extend(to_remove)
    return destroyed_solution, removed_customers


import random

def worst_route_removal(solution, n_remove, cost_function):
    """
    Removes up to n_remove routes with the highest cost.
    """
    destroyed_solution = solution.copy()
    
    # Compute cost of each route
    route_costs = []
    for vehicle, customers in destroyed_solution.items():
        if customers:  # skip empty routes
            c = cost_function(vehicle, customers)
            route_costs.append((vehicle, c))
    
    # Sort routes by descending cost (worst first)
    route_costs.sort(key=lambda x: x[1], reverse=True)
    
    # Select up to n_remove worst routes
    routes_to_remove = route_costs[:min(n_remove, len(route_costs))]
    
    removed_routes = []
    for vehicle, _ in routes_to_remove:
        removed_customers = destroyed_solution[vehicle]
        removed_routes.append((vehicle, removed_customers))
        destroyed_solution[vehicle] = []  # clear the route
    
    return destroyed_solution, removed_routes


# --- Repair Operators ---

def greedy_insertion(solution, removed_customers, customers, vehicles):
    """
    Greedy insertion: Inserts customers into the best possible position.
    """
    for customer_id in removed_customers:
        best_vehicle = None
        best_cost = float('inf')
        for vehicle_id in solution.keys():
            vehicle_capacity = vehicles.loc[vehicles['id'] == vehicle_id, 'capacity'].values[0]
            total_demand = sum(customers.loc[customers['id'] == c_id, 'demand'].values[0]
                               for c_id in solution[vehicle_id])
            if total_demand + customers.loc[customers['id'] == customer_id, 'demand'].values[0] <= vehicle_capacity:
                cost = total_demand
                if cost < best_cost:
                    best_vehicle = vehicle_id
                    best_cost = cost

        if best_vehicle:
            solution[best_vehicle].append(customer_id)
    return solution


def regret_insertion(solution, removed_customers, customers, vehicles, regret_k=3):
    """
    Regret insertion with a lookahead strategy.
    """
    for customer_id in removed_customers:
        insertion_costs = []
        for vehicle_id in solution.keys():
            vehicle_capacity = vehicles.loc[vehicles['id'] == vehicle_id, 'capacity'].values[0]
            total_demand = sum(customers.loc[customers['id'] == c_id, 'demand'].values[0]
                               for c_id in solution[vehicle_id])
            if total_demand + customers.loc[customers['id'] == customer_id, 'demand'].values[0] <= vehicle_capacity:
                insertion_costs.append((vehicle_id, total_demand))
        
        if len(insertion_costs) >= regret_k:
            regret_cost = sum(sorted([c[1] for c in insertion_costs])[:regret_k])
            best_vehicle = sorted(insertion_costs, key=lambda x: x[1])[0][0]
        elif insertion_costs:
            best_vehicle = sorted(insertion_costs, key=lambda x: x[1])[0][0]
        else:
            continue

        solution[best_vehicle].append(customer_id)
    return solution
