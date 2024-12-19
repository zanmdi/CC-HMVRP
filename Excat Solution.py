from docplex.mp.model import Model
import math
from scipy.stats import gamma

# ------------------ Parameters ------------------
g = 9.81  # Gravitational acceleration (m/s^2)
rho = 1.204  # Air density (kg/m^3)
B0 = 0.091  # Bearing coefficient of cargo bike (N)
B1 = 0.0087  # Bearing coefficient of cargo bike (Ns/m)
C_D_A = 0.648  # Drag area (m^2)
v = 5.6  # Velocity (m/s)
C_RR = 0.006  # Rolling resistance coefficient
p = 0.95


customers = [1, 2, 3]
vehicles = [1, 2]
shifts = [1, 2, 3]
nodes = [0] + customers + [len(customers) + 1]

demands = {1: 20, 2: 25, 3: 15}
bike_masses = {1: 50, 2: 60}
rider_masses = {1: 70, 2: 75}
bike_capacities = {1: 100, 2: 110}
travel_times = {(i, j): 1 for i in nodes for j in nodes if i != j}
grades = {(i, j): 0.01 for i in nodes for j in nodes if i != j}

time_windows = {
    0: (0, 0),
    1: (1, 4),
    2: (2, 6),
    3: (3, 8),
    4: (10, 10)
}

# Gamma distribution parameters and battery capacity
alpha = {1: 2.0, 2: 2.5}
beta = {1: 1.5, 2: 1.8}
battery_capacity = {1: 50, 2: 60}  # Battery capacity in km

# Dynamically set M based on maximum possible load (bike capacity + rider mass)
M = max(bike_capacities[k] + rider_masses[k] for k in vehicles)

# ------------------ Function to Build the Model ------------------

def build_model(relax=False):
    mdl = Model(name='energy_consumption_vrp_relaxed' if relax else 'energy_consumption_vrp')

    # Use continuous variables if relax=True, otherwise use binary variables
    if relax:
        x = mdl.continuous_var_dict(((i, j, k, t) for i in nodes for j in nodes for k in vehicles for t in shifts if i != j), name='x')
        y = mdl.continuous_var_dict(((i, k, t) for i in nodes for k in vehicles for t in shifts), name='y')
    else:
        x = mdl.binary_var_dict(((i, j, k, t) for i in nodes for j in nodes for k in vehicles for t in shifts if i != j), name='x')
        y = mdl.binary_var_dict(((i, k, t) for i in nodes for k in vehicles for t in shifts), name='y')

    m = mdl.continuous_var_dict(((i, j, k, t) for i in nodes for j in nodes for k in vehicles for t in shifts if i != j), lb=0, name='m')
    z = mdl.continuous_var_dict(((i, j, k, t) for i in nodes for j in nodes for k in vehicles for t in shifts if i != j), lb=0, name='z')
    s = mdl.continuous_var_dict(((i, k) for i in nodes for k in vehicles), lb=0, name='s')

    # Objective Function
    objective = mdl.sum(travel_times[i, j] * (
        3.96 * (x[i, j, k, t] * (69.8 * 3.5 * rider_masses[k] / 200)) +
        (1 / 0.7) * ((bike_masses[k] + rider_masses[k] + z[i, j, k, t]) * g * v * math.sin(math.atan(grades[i, j]))) +
        (1 / 0.7) * (0.5 * rho * C_D_A * v**3) +
        (1 / 0.7) * ((B0 + B1 * v) * v) +
        (1 / 0.7) * (C_RR * (bike_masses[k] + rider_masses[k] + z[i, j, k, t]) * g * math.cos(math.atan(grades[i, j])) * v)
    ) for i in nodes for j in nodes for k in vehicles for t in shifts if i != j)

    mdl.minimize(objective)

    # Constraints
    for i in customers:
        mdl.add_constraint(mdl.sum(y[i, k, t] for k in vehicles for t in shifts) == 1)

    for k in vehicles:
        for t in shifts:
            for i in nodes:
                mdl.add_constraint(mdl.sum(x[i, j, k, t] for j in nodes if i != j) == y[i, k, t])
                mdl.add_constraint(mdl.sum(x[j, i, k, t] for j in nodes if i != j) == y[i, k, t])

    for k in vehicles:
        for t in shifts:
            mdl.add_constraint(mdl.sum(demands[i] * y[i, k, t] for i in customers) <= bike_capacities[k])

    for i in nodes:
        for j in nodes:
            for k in vehicles:
                for t in shifts:
                    if i != j:
                        mdl.add_constraint(z[i, j, k, t] <= M * x[i, j, k, t])
                        mdl.add_constraint(z[i, j, k, t] <= m[i, j, k, t])
                        mdl.add_constraint(z[i, j, k, t] >= m[i, j, k, t] - M * (1 - x[i, j, k, t]))

    for i in customers:
        for k in vehicles:
            mdl.add_constraint(s[i, k] >= time_windows[i][0])
            mdl.add_constraint(s[i, k] <= time_windows[i][1])

    # Fatigue constraint
    for k in vehicles:
        for t in shifts:
            # Calculate the inverse Gamma CDF for the given parameters
            fatigue_limit = gamma.ppf(p, alpha[k], scale=beta[k])
            mdl.add_constraint(
                mdl.sum(travel_times[i, j] * x[i, j, k, t] for i in nodes for j in nodes if i != j) <= fatigue_limit
            )
        
    # Battery capacity constraint
    for k in vehicles:
        mdl.add_constraint(mdl.sum(v * travel_times[i, j] * x[i, j, k, t] for i in nodes for j in nodes for t in shifts if i != j) <= battery_capacity[k])

    return mdl

# ------------------ Solve for Lower Bound ------------------

print("\nSolving for Lower Bound (Original Integer Constraints):")
mdl = build_model(relax=False)
mdl.parameters.timelimit = 3600  # Set time limit to 1 hour
solution = mdl.solve(log_output=True)

if solution:
    print("Lower Bound Objective Value:", mdl.objective_value)
else:
    print("No solution found for lower bound.")

# ------------------ Solve for Upper Bound ------------------

print("\nSolving for Upper Bound (Relaxed Constraints):")
mdl_relaxed = build_model(relax=True)
mdl_relaxed.parameters.timelimit = 3600  # Set time limit to 1 hour
solution_relaxed = mdl_relaxed.solve(log_output=True)

if solution_relaxed:
    print("Upper Bound Objective Value:", mdl_relaxed.objective_value)
else:
    print("No solution found for upper bound.")
