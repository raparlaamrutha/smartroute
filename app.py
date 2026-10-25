import heapq

# SMART CAMPUS ROUTE PLANNER USING A*

# 1. Campus Map (Graph)
graph = {
    "LIBRARY": {"U-BLOCK": 1},

    "U-BLOCK": {
        "LIBRARY": 1,
        "A-BLOCK": 1,
        "H-BLOCK": 1
    },

    "A-BLOCK": {
        "U-BLOCK": 1,
        "CANTEEN": 1
    },

    "H-BLOCK": {
        "U-BLOCK": 1,
        "LABS": 1
    },

    "CANTEEN": {
        "A-BLOCK": 1,
        "MAIN GATE": 1
    },

    "LABS": {
        "H-BLOCK": 1,
        "MAIN GATE": 1
    },

    "MAIN GATE": {
        "CANTEEN": 1,
        "LABS": 1
    }
}

# 2. Coordinates of Locations
coordinates = {
    "LIBRARY": (0, 4),
    "U-BLOCK": (0, 3),
    "A-BLOCK": (-1, 2),
    "H-BLOCK": (1, 2),
    "CANTEEN": (-1, 1),
    "LABS": (1, 1),
    "MAIN GATE": (0, 0)
}

# 3. Heuristic Function
def heuristic(node, goal):
    # Zero heuristic guarantees a shortest path
    return 0

# 4. A* Search Algorithm
def a_star(start, goal, blocked_roads=None):

    if blocked_roads is None:
        blocked_roads = set()

    priority_queue = [
        (heuristic(start, goal), 0, start, [start])
    ]

    best_cost = {start: 0}
    explored = set()

    while priority_queue:

        f_cost, g_cost, current, path = heapq.heappop(
            priority_queue
        )

        if g_cost != best_cost.get(current):
            continue

        if current in explored:
            continue

        explored.add(current)

        if current == goal:
            return path, g_cost, len(explored)

        for neighbor, distance in graph[current].items():

            road = frozenset((current, neighbor))

            if road in blocked_roads:
                continue

            new_cost = g_cost + distance

            if new_cost < best_cost.get(
                neighbor, float("inf")
            ):
                best_cost[neighbor] = new_cost

                new_path = path + [neighbor]

                new_f = new_cost + heuristic(
                    neighbor, goal
                )

                heapq.heappush(
                    priority_queue,
                    (
                        new_f,
                        new_cost,
                        neighbor,
                        new_path
                    )
                )

    return None, None, len(explored)

# 5. Display Available Locations
def show_locations():

    print("\nAVAILABLE LOCATIONS")

    for number, location in enumerate(
        graph, start=1
    ):
        print(f"{number}. {location}")

# 6. Normalize User Input
def normalize_location(name):

    return " ".join(
        name.strip().upper().split()
    )

# 7. Display Route and Directions
def show_route(path, cost, explored):

    print("\nSHORTEST ROUTE")
    print(" -> ".join(path))

    print("\nSTEP-BY-STEP DIRECTIONS")

    for step, location in enumerate(
        path, start=1
    ):

        if step == 1:
            print(f"{step}. Start at {location}")

        elif step == len(path):
            print(f"{step}. Arrive at {location}")

        else:
            print(f"{step}. Walk to {location}")

    print("\nTotal Path Cost:", cost)
    print("Locations Explored:", explored)
    print("Number of Stops:", len(path) - 1)

# 8. Find an Alternative Route
def find_alternative_route(start, goal, main_path):

    alternatives = []

    for i in range(len(main_path) - 1):

        road = frozenset(
            (main_path[i], main_path[i + 1])
        )

        path, cost, explored = a_star(
            start, goal, {road}
        )

        if path and path != main_path:
            alternatives.append(
                (cost, path, explored)
            )

    if alternatives:
        alternatives.sort(
            key=lambda item: (item[0], item[1])
        )
        return alternatives[0]

    return None

# 9. Main Program
def main():

    print("=" * 45)
    print(" SMART CAMPUS ROUTE PLANNER USING A*")
    print("=" * 45)

    while True:

        show_locations()

        start = normalize_location(
            input("\nEnter starting location: ")
        )

        goal = normalize_location(
            input("Enter destination: ")
        )

        if start not in graph or goal not in graph:

            print(
                "\nInvalid location! "
                "Please enter a location from the list."
            )
            continue

        if start == goal:

            print(
                f"\nYou are already at {start}. "
                "No travel is needed."
            )

        else:

            path, cost, explored = a_star(
                start, goal
            )

            if path:

                show_route(path, cost, explored)

                alternative = find_alternative_route(
                    start, goal, path
                )

                if alternative:

                    alt_cost, alt_path, _ = alternative

                    print("\nALTERNATIVE ROUTE")
                    print(" -> ".join(alt_path))
                    print(
                        "Alternative Path Cost:",
                        alt_cost
                    )

                else:

                    print(
                        "\nNo alternative route is available."
                    )

            else:

                print("\nNo route found.")

        again = input(
            "\nPlan another route? (yes/no): "
        ).strip().lower()

        if again not in ("yes", "y"):

            print(
                "\nThank you for using "
                "Smart Campus Route Planner!"
            )
            break

# 10. Program Execution
if __name__ == "__main__":
    main()
