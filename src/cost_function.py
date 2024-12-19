import numpy as np

def calculate_energy_consumption(customers, vehicles, solution, parameters):
    """
    Calculate the energy consumption for the current solution based on the objective function Z(s).
    Args:
        customers: DataFrame with customer details (demand, time windows, etc.).
        vehicles: DataFrame with vehicle details (mass, capacity, etc.).
        solution: Dict with vehicle assignments.
        parameters: Dict of problem parameters.
    Returns:
        Total energy consumption Z(s).
    """
    g = parameters['g']  # Gravitational acceleration
    rho = parameters['rho']  # Air density
    C_DA = parameters['C_DA']  # Drag area
    v = parameters['v']  # Velocity
    B_0 = parameters['B_0']  # Bearing coefficient constant
    B_1 = parameters['B_1']  # Bearing coefficient linear
    C_RR = parameters['C_RR']  # Rolling resistance coefficient
    METS = parameters['METS']  # Metabolic equivalents (constant)

    total_cost = 0

    for vehicle_id, assigned_customers in solution.items():
        vehicle = vehicles.loc[vehicles['id'] == vehicle_id].iloc[0]
        mc_k = vehicle['mass']  # Vehicle mass
        mr_k = vehicle['rider_mass']  # Rider mass

        for idx in range(len(assigned_customers) - 1):
            i = assigned_customers[idx]
            j = assigned_customers[idx + 1]

            t_ij = customers.loc[customers['id'] == i, f'travel_time_to_{j}'].values[0]
            e_ij = customers.loc[customers['id'] == i, f'grade_to_{j}'].values[0]
            m_ijk_t = customers.loc[customers['id'] == j, 'demand'].values[0]

            # Objective function components
            metabolic_cost = 3.96 * ((69.8 * 3.5 * METS * mr_k) / 200)
            grade_cost = (1 / 0.7) * ((mc_k + mr_k + m_ijk_t) * g * v * np.sin(np.arctan(e_ij)))
            drag_cost = (1 / 0.7) * (0.5 * rho * C_DA * v**3)
            bearing_cost = (1 / 0.7) * ((B_0 + B_1 * v) * v)
            rolling_cost = (1 / 0.7) * (C_RR * (mc_k + mr_k + m_ijk_t) * g * np.cos(np.arctan(e_ij)) * v)

            total_cost += t_ij * (metabolic_cost + grade_cost + drag_cost + bearing_cost + rolling_cost)

    return total_cost

def augmented_cost_function(customers, vehicles, solution, parameters, weights):
    """
    Calculate the augmented cost function f(s) including penalties for infeasibilities.
    Args:
        customers: DataFrame with customer data.
        vehicles: DataFrame with vehicle details.
        solution: Current solution dict.
        parameters: Problem parameters.
        weights: Penalty weights for constraints.
    Returns:
        Total augmented cost f(s).
    """
    # Objective function Z(s)
    Z_s = calculate_energy_consumption(customers, vehicles, solution, parameters)
    
    # Penalty terms
    penalty_battery = 0
    penalty_fatigue = 0
    penalty_capacity = 0
    penalty_time_window = 0

    for vehicle_id, assigned_customers in solution.items():
        vehicle = vehicles.loc[vehicles['id'] == vehicle_id].iloc[0]
        total_demand = sum(customers.loc[customers['id'] == c_id, 'demand'].values[0] for c_id in assigned_customers)

        # Battery range violation
        if vehicle['battery_range'] < sum(customers.loc[customers['id'] == c_id, 'travel_time'].values[0] for c_id in assigned_customers):
            penalty_battery += weights['wG'] * (sum(customers['travel_time']) - vehicle['battery_range'])

        # Fatigue threshold violation
        if vehicle['fatigue_threshold'] < sum(customers['travel_time']):
            penalty_fatigue += weights['wF'] * (sum(customers['travel_time']) - vehicle['fatigue_threshold'])

        # Capacity violation
        if total_demand > vehicle['capacity']:
            penalty_capacity += weights['wQ'] * (total_demand - vehicle['capacity'])

    total_augmented_cost = Z_s + penalty_battery + penalty_fatigue + penalty_capacity + penalty_time_window
    return total_augmented_cost
