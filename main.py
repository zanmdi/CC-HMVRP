import pandas as pd
import numpy as np
from src.initial_solution import generate_initial_solution
from src.alns import alns
from src.cost_function import augmented_cost_function
from src.visualize_routes import visualize_routes

def main():
    # Define parameters
    parameters = {
        'g': 9.81,       # Gravitational acceleration (m/s^2)
        'rho': 1.204,    # Air density (kg/m^3)
        'C_DA': 0.648,   # Drag area (m^2)
        'v': 5.6,        # Velocity (m/s)
        'B_0': 0.091,    # Bearing coefficient (N)
        'B_1': 0.0087,   # Bearing coefficient (Ns/m)
        'C_RR': 0.006,   # Rolling resistance coefficient
        'METS': 4.9      # Metabolic equivalents (kcal/kg/hour)
    }

    # Define penalty weights
    weights = {
        'wG': 10,   # Penalty weight for battery constraint violations
        'wF': 5,    # Penalty weight for fatigue constraint violations
        'wQ': 3,    # Penalty weight for capacity constraint violations
        'wT': 2     # Penalty weight for time window constraint violations
    }

    # Customers and Depot Data (0 is the depot)
    customers = pd.DataFrame([
        {'id': 0, 'a_i': 0, 'b_i': 24, 'longitude': 41.8827, 'latitude':  -87.6233,'demand': 0},  # Depot
        {'id': 1, 'a_i': 8, 'b_i': 12, 'longitude': 41.8917, 'latitude': -87.6055,'demand': 10},
        {'id': 2, 'a_i': 9, 'b_i': 11, 'longitude': 41.8789, 'latitude': -87.6359,'demand': 15},
        {'id': 3, 'a_i': 10, 'b_i': 14, 'longitude': 41.9211, 'latitude': -87.6338,'demand': 8}
    ])

    # Full Travel Time Matrix (hours)
    travel_time_matrix = np.array([
        [0.0, 1.0, 1.5, 2.0],  # From Depot
        [1.0, 0.0, 1.2, 1.8],  # From Customer 1
        [1.5, 1.2, 0.0, 1.0],  # From Customer 2
        [2.0, 1.8, 1.0, 0.0]   # From Customer 3
    ])

    # Grade Matrix (slopes between points)
    grade_matrix = np.array([
        [0.0, 0.01, 0.02, 0.03],  # From Depot
        [0.01, 0.0, 0.015, 0.025],  # From Customer 1
        [0.02, 0.015, 0.0, 0.01],  # From Customer 2
        [0.03, 0.025, 0.01, 0.0]   # From Customer 3
    ])

    # Vehicles Data
    # The fatigue threshold is calculated for each rider based on p=0.95 and aplha_k and beta_k described in the paper
    vehicles = pd.DataFrame([
        {'id': 1, 'mass': 40, 'rider_mass': 70, 'capacity': 50, 'fatigue_threshold': 4, 'battery_range': 10},
        {'id': 2, 'mass': 42, 'rider_mass': 65, 'capacity': 45, 'fatigue_threshold': 3.5, 'battery_range': 9}
    ])

    # Shifts Data
    shifts = pd.DataFrame([
        {'E_t': 8, 'L_t': 12},
        {'E_t': 12, 'L_t': 16}
    ])

    # Generate the initial solution
    print("\n--- Generating Initial Solution ---")
    initial_solution, multi_shift_customers = generate_initial_solution(customers, vehicles, shifts)
    print("Initial Solution:", initial_solution)
    print("Multi-Shift Customers:", multi_shift_customers)

    # Integrate travel time and grade matrix into customer DataFrame
    customers['travel_time_matrix'] = [travel_time_matrix] * len(customers)
    customers['grade_matrix'] = [grade_matrix] * len(customers)

    # Run the ALNS algorithm
    print("\n--- Running ALNS Algorithm ---")
    best_solution = alns(initial_solution, customers, vehicles, parameters, weights, max_iter=100)

    print("\n--- Best Solution Found ---")
    for vehicle, assigned_customers in best_solution.items():
        print(f"Vehicle {vehicle}: Customers {assigned_customers}")

    # Calculate the final cost of the best solution
    print("\n--- Final Cost ---")
    final_cost = augmented_cost_function(customers, vehicles, best_solution, parameters, weights)
    print(f"Total Cost: {final_cost:.2f}")


    # Visualize routes
    print("\n--- Route Visualization ---")
    
    visualize_routes(customers.iloc[1:, :].reset_index(drop = True), customers.iloc[:1, :], best_solution)


if __name__ == "__main__":
    main()
