import streamlit as st
import heapq
import plotly.graph_objects as go

st.set_page_config(
    page_title="SmartRoute | Campus Navigator",
    page_icon="🗺️",
    layout="wide"
)

# ---------- CAMPUS DATA ----------
graph = {
    "LIBRARY": {"U-BLOCK": 1},
    "U-BLOCK": {
        "LIBRARY": 1, "A-BLOCK": 1, "H-BLOCK": 1
    },
    "A-BLOCK": {"U-BLOCK": 1, "CANTEEN": 1},
    "H-BLOCK": {"U-BLOCK": 1, "LABS": 1},
    "CANTEEN": {"A-BLOCK": 1, "MAIN GATE": 1},
    "LABS": {"H-BLOCK": 1, "MAIN GATE": 1},
    "MAIN GATE": {"CANTEEN": 1, "LABS": 1}
}

coordinates = {
    "LIBRARY": (0, 4),
    "U-BLOCK": (0, 3),
    "A-BLOCK": (-1, 2),
    "H-BLOCK": (1, 2),
    "CANTEEN": (-1, 1),
    "LABS": (1, 1),
    "MAIN GATE": (0, 0)
}

locations = list(graph.keys())

# ---------- STYLING ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef5ff, #f8fbff);
}
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #163b72;
}
.subtitle {
    color: #526783;
    font-size: 16px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce7f5;
    padding: 16px;
    border-radius: 14px;
}
.stButton button {
    border-radius: 10px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------- A* SEARCH ----------
def heuristic(node, goal):
    # Zero heuristic: guarantees shortest path
    return 0

def a_star(start, goal, blocked_roads=None):
    blocked_roads = blocked_roads or set()

    queue = [(heuristic(start, goal), 0, start, [start])]
    best_cost = {start: 0}
    explored = set()

    while queue:
        f_cost, cost, current, path = heapq.heappop(queue)

        if cost != best_cost.get(current):
            continue

        if current in explored:
            continue

        explored.add(current)

        if current == goal:
            return path, cost, len(explored)

        for neighbor, distance in graph[current].items():
            road = frozenset((current, neighbor))

            if road in blocked_roads:
                continue

            new_cost = cost + distance

            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                new_path = path + [neighbor]

                heapq.heappush(
                    queue,
                    (
                        new_cost + heuristic(neighbor, goal),
                        new_cost,
                        neighbor,
                        new_path
                    )
                )

    return None, None, len(explored)

def find_alternative(start, goal, main_path, blocked_roads):
    alternatives = []

    # Block each road in the main path one at a time
    for i in range(len(main_path) - 1):
        road = frozenset((main_path[i], main_path[i + 1]))
        all_blocked = set(blocked_roads) | {road}

        path, cost, explored = a_star(start, goal, all_blocked)

        if path and path != main_path:
            alternatives.append((cost, path, explored))

    if alternatives:
        alternatives.sort(key=lambda item: (item[0], item[1]))
        return alternatives[0]

    return None

# ---------- CAMPUS MAP ----------
def draw_map(main_path=None, alt_path=None, blocked=None,
             start=None, goal=None):
    main_path = main_path or []
    alt_path = alt_path or []
    blocked = blocked or set()

    fig = go.Figure()

    # Draw all roads
    drawn = set()

    for node, neighbors in graph.items():
        for neighbor in neighbors:
            road = frozenset((node, neighbor))

            if road in drawn:
                continue
            drawn.add(road)

            x1, y1 = coordinates[node]
            x2, y2 = coordinates[neighbor]

            is_blocked = road in blocked
            is_main = (
                len(main_path) > 1
                and any(
                    frozenset((main_path[i], main_path[i + 1])) == road
                    for i in range(len(main_path) - 1)
                )
            )
            is_alt = (
                len(alt_path) > 1
                and any(
                    frozenset((alt_path[i], alt_path[i + 1])) == road
                    for i in range(len(alt_path) - 1)
                )
            )

            color = "#b7c5d8"
            width = 3
            dash = "solid"

            if is_alt:
                color, width, dash = "#f59e0b", 4, "dash"
            if is_main:
                color, width, dash = "#16a34a", 6, "solid"
            if is_blocked:
                color, width, dash = "#dc2626", 4, "dot"

            fig.add_trace(go.Scatter(
                x=[x1, x2], y=[y1, y2],
                mode="lines",
                line=dict(color=color, width=width, dash=dash),
                hoverinfo="text",
                text=[
                    f"{node} ↔ {neighbor}",
                    f"{node} ↔ {neighbor}"
                ],
                showlegend=False
            ))

            if is_blocked:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                fig.add_annotation(
                    x=mx, y=my, text="✕",
                    showarrow=False,
                    font=dict(color="#dc2626", size=20)
                )

    # Draw campus locations
    xs, ys, labels, colors, symbols = [], [], [], [], []

    for node, (x, y) in coordinates.items():
        xs.append(x)
        ys.append(y)
        labels.append(node)

        if node == start:
            colors.append("#16a34a")
            symbols.append("star")
        elif node == goal:
            colors.append("#2563eb")
            symbols.append("diamond")
        else:
            colors.append("#163b72")
            symbols.append("circle")

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(
            size=20,
            color=colors,
            symbol=symbols,
            line=dict(color="white", width=2)
        ),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    ))

    fig.update_layout(
        height=510,
        margin=dict(l=15, r=15, t=25, b=15),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(visible=False, range=[-2, 2]),
        yaxis=dict(visible=False, range=[-0.5, 4.7],
                   scaleanchor="x", scaleratio=1),
        showlegend=False
    )

    return fig

# ---------- HEADER ----------
st.markdown(
    '<div class="main-title">🗺️ SmartRoute</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Smart Campus Route Planner • A* Search Algorithm</div>',
    unsafe_allow_html=True
)
st.write("")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Route Settings")
    start = st.selectbox(
        "📍 Starting Location",
        locations,
        index=0
    )
    goal = st.selectbox(
        "🎯 Destination",
        locations,
        index=len(locations) - 1
    )

    st.divider()
    st.subheader("🚧 Blocked Roads")

    road_options = []
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if locations.index(node) < locations.index(neighbor):
                road_options.append(f"{node} ↔ {neighbor}")

    selected_roads = st.multiselect(
        "Select roads to close",
        road_options,
        help="Closed roads will not be used for routing."
    )

    blocked_roads = set()
    for item in selected_roads:
        a, b = item.split(" ↔ ")
        blocked_roads.add(frozenset((a, b)))

    find_route = st.button(
        "🔍 Find Best Route",
        type="primary",
        use_container_width=True
    )

# ---------- ROUTE RESULTS ----------
# Recalculate whenever the user changes the settings
# or presses the route button.
path, cost, explored = a_star(start, goal, blocked_roads)

alternative = None
if path and start != goal:
    alternative = find_alternative(
        start, goal, path, blocked_roads
    )

alt_path = alternative[1] if alternative else []

tab_map, tab_directions = st.tabs(
    ["🗺️ Campus Map", "🧭 Directions"]
)

with tab_map:
    st.subheader("Campus Route Map")
    st.caption(
        "🟢 Shortest route  |  🟠 Alternative route  |  "
        "🔴 Blocked road  |  ⭐ Start  |  🔷 Destination"
    )

    st.plotly_chart(
        draw_map(path, alt_path, blocked_roads, start, goal),
        use_container_width=True
    )

with tab_directions:
    st.subheader("Step-by-Step Directions")

    if start == goal:
        st.success(f"You are already at {start}. No travel needed.")

    elif path:
        for i, location in enumerate(path):
            if i == 0:
                st.write(f"🟢 **Step {i + 1}:** Start at {location}")
            elif i == len(path) - 1:
                st.write(f"🏁 **Step {i + 1}:** Arrive at {location}")
            else:
                st.write(f"🚶 **Step {i + 1}:** Walk to {location}")

    else:
        st.error("No route available. Try unblocking a road.")

st.divider()

if path:
    c1, c2, c3 = st.columns(3)

    c1.metric("🛣️ Route Cost", cost)
    c2.metric("📍 Number of Stops", len(path) - 1)
    c3.metric("🔎 Locations Explored", explored)

    st.subheader("✅ Shortest Route")
    st.success("  →  ".join(path))

    if alternative:
        alt_cost, alt_route, alt_explored = alternative

        st.subheader("🔁 Alternative Route")
        st.info("  →  ".join(alt_route))
        st.write(f"Alternative route cost: **{alt_cost}**")
    elif start != goal:
        st.warning("No alternative route is available.")

else:
    st.error(
        "No route found between these locations with the selected "
        "blocked roads. Please unblock a road and try again."
    )

st.divider()
st.caption(
    "SmartRoute | A* Search | Demo campus map with sample road distances"
)
