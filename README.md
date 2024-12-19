# Chance-Constrained Heterogeneous and Multi-trip Vehicle Routing Problem with Time Windows

A Python-based model for solving the **Chance-Constrained a Heterogeneous and Multi-trip Vehicle Routing Problem with Time Windows (CC-HMTVRPTW)** using **IBM CPLEX** and an **improved Adaptive Large Neighborhood Search (ALNS)**. 

---

## **Features**

- **Energy Consumption Optimization**:  
  Minimize the energy consumed by cargo bikes and the riders during deliveries.
  
- **Constraints**:  
  - **Vehicle Capacity Limits**: Ensure cargo bikes do not exceed their load capacity.
  - **Customer Time Windows**: Deliveries must be completed within specified time windows.
  - **Rider Fatigue**: Limit trip durations based on rider fatigue levels.
  - **Battery Constraints**: Ensure deliveries do not exceed the cargo bike's battery capacity.

- **Modified ALNS**
  - **Initial Solution Generation**: Based on fatigue-dependent travel times and shift overlaps.
  - **ALNS Heuristic**: Adaptive algorithm with multiple destroy and repair operators.
---

## **Requirements**

- **Python 3.12.4**
- **IBM CPLEX Optimization Studio**
- **`docplex` Library**

### **Install Dependencies**

Clone the repository:

```bash
git clone https://github.com/your-username/multi-shift-vrp-alns.git
cd multi-shift-vrp-alns
```
Install dependencies:

```bash
pip install -r requirements.txt
```

## 📊 **Usage**

### 1. **Prepare Data**

Update the `main.py` with your own:

- **Customers**: Latitude, longitude, demand, and time windows.
- **Depot**: Central starting location for vehicles.
- **Vehicles**: Specifications including mass, capacity, and battery range.
- **Shifts**: Time windows for different delivery shifts.

### 2. **Run the Program**

```bash
python main.py
```

### 3. **Output**

- **Console Output**: Initial solution, best solution, and final cost.
- **Visualization**: A plot displaying routes for each shift with distinct styles.

---

## **Project Structure**

```
CC-HMVRPTW/
│
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── initial_solution.py   # Initial solution generation
│   ├── cost_function.py      # Cost function calculation
│   ├── operators.py          # ALNS destroy and repair operators
│   ├── alns.py               # ALNS algorithm
│   └── visualize_routes.py   # Route visualization
```

---

## **Contributing**

Contributions are welcome! Feel free to:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

