from docplex.mp.model import Model
import math
from scipy.stats import gamma

# ------------------ Parameters ------------------
g = 9.807
rho = 1.204
METs = 4.9
psi_h = 4.429
psi_m = 1.369
B0 = 0.091
B1 = 0.009
C_D_A = 0.648
v = 5.6
C_RR = 0.006
p = 0.95

customers = [1, 2, 3]
vehicles = [1, 2]
shifts = [1, 2, 3]
nodes = [0] + customers + [len(customers) + 1]

demands = {1: 20, 2: 25, 3: 15}
bike_masses = {1: 50, 2: 60}
rider_masses = {1: 70, 2: 75}
bike_capacities = {1: 100, 2: 110}
battery_capacity = {1: 50, 2: 60}
alpha = {1: 2.0, 2: 2.5}
beta = {1: 1.5, 2: 1.8}
Rk = 0.25

time_windows = {
    0: (0, 0),
    1: (1, 4),
    2: (2, 6),
    3: (3, 8),
    4: (10, 10)
}
ST = {1: 0, 2: 4.5, 3: 9}
ET = {1: 4.5, 2: 9, 3: 13.5}
service_times = {0: 0, 1: 0.5, 2: 0.5, 3: 0.5, 4: 0}

travel_times = {(i, j): 1 for i in nodes for j in nodes if i != j}
grades = {(i, j): 0.01 for i in nodes for j in nodes if i != j}

W = max(travel_times[i, j] for i in nodes for j in nodes if i != j) + max(b for (a, b) in time_windows.values())
M_reload = max(travel_times[i, 0] + Rk for i in customers) + max(b for (a, b) in time_windows.values())
N = {k: bike_capacities[k] for k in vehicles}
Q = {(j, k): bike_capacities[k] - demands.get(j, 0) for j in nodes for k in vehicles}

# ------------------ Function to Build the Model ------------------

def build_model(relax=False):
    mdl = Model(name='energy_consumption_vrp_relaxed' if relax else 'energy_consumption_vrp')

    # Use continuous variables if relax=True, otherwise use binary variables
    if relax:
        x = mdl.continuous_var_dict(((i, j, k, l) for i in nodes for j in nodes if i != j for k in vehicles for l in shifts), name='x')
        y = mdl.continuous_var_dict(((i, k, l) for i in nodes for k in vehicles for l in shifts), name='y')
    else:
        x = mdl.binary_var_dict(((i, j, k, l) for i in nodes for j in nodes if i != j for k in vehicles for l in shifts), name='x')
        y = mdl.binary_var_dict(((i, k, l) for i in nodes for k in vehicles for l in shifts), name='y')

    m = mdl.continuous_var_dict(((i, k, l) for i in nodes for k in vehicles for l in shifts), lb=0, name='m')
    z = mdl.continuous_var_dict(((i, j, k, l) for i in nodes for j in nodes if i != j for k in vehicles for l in shifts), lb=0, name='z')
    s = mdl.continuous_var_dict(((i, k, l) for i in nodes for k in vehicles for l in shifts), lb=0, name='s')

    # Objective Function
    objective = mdl.sum(
        travel_times[i, j] * (
            psi_m * METs * x[i, j, k, l] * rider_masses[k] +
            psi_h * (
                (x[i, j, k, l] * bike_masses[k] + x[i, j, k, l] * rider_masses[k] + z[i, j, k, l]) * g * v * math.sin(math.atan(grades[i, j])) +
                x[i, j, k, l] * 0.5 * rho * C_D_A * v**3 +
                x[i, j, k, l] * (B0 + B1 * v) * v +
                C_RR * (x[i, j, k, l] * bike_masses[k] + x[i, j, k, l] * rider_masses[k] + z[i, j, k, l]) * g * math.cos(math.atan(grades[i, j])) * v
            )
        ) for i in nodes for j in nodes if i != j for k in vehicles for l in shifts
    )

    mdl.minimize(objective)

    # Constraints
    
        # (21) Each customer is visited exactly once
        for i in customers:
            mdl.add_constraint(mdl.sum(y[i, k, l] for k in vehicles for l in shifts) == 1)
    
        # (22) Flow conservation constraints
        for k in vehicles:
            for l in shifts:
                for i in nodes:
                    mdl.add_constraint(mdl.sum(x[i, j, k, l] for j in nodes if i != j) == y[i, k, l])
                    mdl.add_constraint(mdl.sum(x[j, i, k, l] for j in nodes if i != j) == y[i, k, l])


        # (23) Incoming arc consistency
        for j in customers:
            for k in vehicles:
                for l in shifts:
                    mdl.add_constraint(mdl.sum(x[i, j, k, l] for i in nodes if i != j) == y[j, k, l])
    
        # (24) Capacity constraint per shift
        for k in vehicles:
            for l in shifts:
                mdl.add_constraint(mdl.sum(demands.get(i, 0) * y[i, k, l] for i in customers) <= bike_capacities[k])


        # (25) Vehicle depot departure constraint
        for k in vehicles:
            mdl.add_constraint(
                mdl.sum(x[0, j, k, l] for j in customers for l in shifts) <= len(shifts)
            )

        # (26) Depot balance: departures from start depot = arrivals to end depot
        for k in vehicles:
            for l in shifts:
                mdl.add_constraint(
                    mdl.sum(x[0, j, k, l] for j in customers) ==
                    mdl.sum(x[i, nodes[-1], k, l] for i in customers)
                )
    
        # (27-29) Load propagation and limit
        for i in nodes:
            for j in nodes:
                if i != j:
                    for k in vehicles:
                        for l in shifts:
                            mdl.add_constraint(m[i, k, l] >= m[j, k, l] + demands.get(j, 0) - Q[j, k] * (1 - x[i, j, k, l]))
        for i in nodes:
            for k in vehicles:
                for l in shifts:
                    mdl.add_constraint(m[i, k, l] >= demands.get(i, 0))
                    mdl.add_constraint(m[i, k, l] <= bike_capacities[k])
    
        # (29-30) Time propagation and time windows
        for i in customers:
            for j in nodes:
                if i != j:
                    for k in vehicles:
                        for l in shifts:
                            mdl.add_constraint(s[i, k, l] + travel_times[i, j] + service_times[i] - W * (1 - x[i, j, k, l]) <= s[j, k, l])

    
        for i in customers:
            for k in vehicles:
                for l in shifts:
                    mdl.add_constraint(s[i, k, l] + travel_times[i, 0] + Rk - M_reload * (1 - x[i, nodes[-1], k, l]) <= s[nodes[-1], k, l])
    
        # (31) Shift start-end and continuity
        for k in vehicles:
            for l in shifts[:-1]:
                mdl.add_constraint(s[nodes[-1], k, l] <= s[0, k, l + 1])
    
        # (32) Time windows for customers
        for i in customers:
            for k in vehicles:
                for l in shifts:
                    a, b = time_windows[i]
                    mdl.add_constraint(s[i, k, l] >= a)
                    mdl.add_constraint(s[i, k, l] <= b)
    
        # (33) Fatigue constraint
        for k in vehicles:
            for l in shifts:
                fatigue_limit = gamma.ppf(p, alpha[k], scale=beta[k]) / 60
                mdl.add_constraint(mdl.sum(travel_times[i, j] * x[i, j, k, l] for i in nodes for j in nodes if i != j) <= fatigue_limit)
    
        # (34) Battery constraint
        for k in vehicles:
            mdl.add_constraint(mdl.sum(3.6 * v * travel_times[i, j] * x[i, j, k, l] for i in nodes for j in nodes if i != j for l in shifts) <= battery_capacity[k])
    
        # (39-42) McCormick linearization for z
        for i in nodes:
            for j in nodes:
                if i != j:
                    for k in vehicles:
                        for l in shifts:
                            mdl.add_constraint(z[i, j, k, l] <= N[k] * x[i, j, k, l])
                            mdl.add_constraint(z[i, j, k, l] <= m[i, k, l])
                            mdl.add_constraint(z[i, j, k, l] >= m[i, k, l] - N[k] * (1 - x[i, j, k, l]))
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
