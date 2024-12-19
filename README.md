# 🚴‍♂️ Chance-Constrained a Heterogeneous and Multi-trip Vehicle Routing Problem with Time Windows

A Python-based model for solving the **Chance-Constrained a Heterogeneous and Multi-trip Vehicle Routing Problem with Time Windows (CC-HMTVRPTW)** using **IBM CPLEX** and an **improved Adaptive Large Neighborhood Search (ALNS)**. 

---

## 🌟 **Features**

- **Energy Consumption Optimization**:  
  Minimize the energy consumed by cargo bikes and the riders during deliveries.
  
- **Constraints**:  
  - **Vehicle Capacity Limits**: Ensure cargo bikes do not exceed their load capacity.
  - **Customer Time Windows**: Deliveries must be completed within specified time windows.
  - **Rider Fatigue**: Limit trip durations based on rider fatigue levels.
  - **Battery Constraints**: Ensure deliveries do not exceed the cargo bike's battery capacity.

---

## 🛠️ **Requirements**

- **Python 3.12.4**
- **IBM CPLEX Optimization Studio**
- **`docplex` Library**

### **Install Dependencies**

```bash
pip install docplex
