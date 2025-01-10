import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point

def visualize_routes(customers, depot, solution, shifts):
    """
    Visualize the routes assigned to vehicles for different shifts.

    Args:
        customers (DataFrame): DataFrame with customer locations (latitude, longitude).
        depot (tuple): Latitude and longitude of the depot.
        solution (dict): Dictionary with vehicle IDs, their assigned customers, and shifts.
        shifts (list): List of shifts (e.g., [1, 2, 3]).
    """
    # Create GeoDataFrames for customers and depot
    customer_points = [Point(row['longitude'], row['latitude']) for _, row in customers.iterrows()]
    customer_gdf = gpd.GeoDataFrame(customers, geometry=customer_points)
    
    depot_point = Point(depot[1], depot[0])
    depot_gdf = gpd.GeoDataFrame({'geometry': [depot_point]}, geometry='geometry')

    # Line styles for each shift
    shift_styles = {
        1: 'o-',   # First shift: Solid line with circles
        2: 's--',  # Second shift: Dashed line with square
        3: '^:'   # Third shift: Dotted line with triangles
    }

    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 10))
    base = customer_gdf.plot(ax=ax, color='blue', markersize=50, label='Customers')
    depot_gdf.plot(ax=base, color='red', markersize=100, label='Depot')

    # Plot routes
    for vehicle, assignments in solution.items():
        for shift, assigned_customers in assignments.items():
            if len(assigned_customers) == 0:
                continue

            # Collect route points: depot -> assigned customers -> depot
            route_points = [depot_point]
            for customer_id in assigned_customers:
                customer = customers.loc[customers['id'] == customer_id].iloc[0]
                route_points.append(Point(customer['longitude'], customer['latitude']))
            route_points.append(depot_point)

            # Create a LineString for the route
            route_line = LineString(route_points)
            gpd.GeoSeries([route_line]).plot(ax=base, linewidth=2, linestyle=shift_styles.get(shift, '-'), label=f'Vehicle {vehicle}, Shift {shift}')

    # Add legend and labels
    plt.title("Vehicle Routes Visualization by Shift")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()
