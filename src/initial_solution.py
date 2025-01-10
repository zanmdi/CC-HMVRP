import numpy as np
import pandas as pd

def calculate_overlap(a_i, b_i, E_t, L_t):
    """Calculate overlap between customer time window and shift."""
    return max(0, min(b_i, L_t) - max(a_i, E_t))

def generate_initial_solution(customers, vehicles, shifts):
    """
    Generate the initial solution.
    Args:
        customers: DataFrame of customers with 'a_i', 'b_i' (time window) and demand.
        vehicles: DataFrame of vehicles with fatigue, distance, and capacity constraints.
        shifts: DataFrame with 'E_t' and 'L_t' (shift start and end).
    Returns:
        initial_solution: A dict containing vehicle assignments.
        set of multi-shift customers: A list containing customers that can be assigned to multiple shifts.
    """
    initial_solution = {}
    multi_shift_customers = set()
    
    # Sort vehicles by fatigue threshold (Gamma function)
    vehicles = vehicles.sort_values(by='fatigue_threshold', ascending=False)

    for _, shift in shifts.iterrows():
        E_t, L_t = shift['E_t'], shift['L_t']
        shift_customers = []

        for _, customer in customers.iterrows():
            overlap = calculate_overlap(customer['a_i'], customer['b_i'], E_t, L_t)
            if overlap > 0:
                shift_customers.append(customer['id'])
                if customers[customers['id'] == customer['id']].shape[0] > 1:
                    multi_shift_customers.add(customer['id'])
        
        # Assign customers to vehicles
        for _, vehicle in vehicles.iterrows():
            assigned = []
            total_demand = 0
            for c_id in shift_customers:
                demand = customers.loc[customers['id'] == c_id, 'demand'].values[0]
                if total_demand + demand <= vehicle['capacity']:
                    assigned.append(c_id)
                    total_demand += demand
            
            initial_solution[vehicle['id']] = assigned
    
    return initial_solution, list(multi_shift_customers)
