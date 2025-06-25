
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# App title and description
st.title("Apollonius Circle Overlap Plotter")
st.write("Adjust the sliders to change the input point A and ratio k. The plot shows the overlapping region of Apollonius circles created between point A and a grid of invisible points.")

# Sliders for coordinates of point A and ratio k
x_a = st.slider("x_A (Input Point)", min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
y_a = st.slider("y_A (Input Point)", min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
k = st.slider("k (Ratio)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)

# Grid density slider
grid_density = st.slider("Grid Density", min_value=3, max_value=100, value=7, step=1)

# Resolution for overlap detection
resolution = st.slider("Overlap Resolution", min_value=50, max_value=200, value=100, step=10)

# Create grid of points
grid_range = 10  # Range of the grid
x_grid = np.linspace(-grid_range/2, grid_range/2, grid_density)
y_grid = np.linspace(-grid_range/2, grid_range/2, grid_density)

# Function to calculate Apollonius circle parameters
def apollonius_circle(x1, y1, x2, y2, k):
    """
    Calculate center and radius of Apollonius circle for points (x1,y1) and (x2,y2) with ratio k
    Returns (center_x, center_y, radius) or None if circle doesn't exist
    """
    d = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Special cases
    if d < 1e-6 or abs(k - 1) < 1e-6:
        return None
    
    # Calculate center
    denominator = 1 - k**2
    if abs(denominator) < 1e-6:
        return None
        
    ox = (x1 - k**2 * x2) / denominator
    oy = (y1 - k**2 * y2) / denominator
    
    # Calculate radius
    r = abs(k * d / denominator)
    
    return ox, oy, r

# Function to check if a point is inside a circle
def point_in_circle(px, py, cx, cy, r):
    """Check if point (px, py) is inside circle centered at (cx, cy) with radius r"""
    return (px - cx)**2 + (py - cy)**2 <= r**2

# Collect all valid Apollonius circles
apollonius_circles = []
for xi in x_grid:
    for yi in y_grid:
        # Skip if grid point is too close to input point
        if abs(xi - x_a) < 1e-6 and abs(yi - y_a) < 1e-6:
            continue
            
        circle_params = apollonius_circle(x_a, y_a, xi, yi, k)
        if circle_params is not None:
            apollonius_circles.append(circle_params)

# Create figure
fig = go.Figure()

# Add input point A
fig.add_trace(go.Scatter(
    x=[x_a],
    y=[y_a],
    mode="markers+text",
    text=["A"],
    textposition="top right",
    marker=dict(size=10, color="red"),
    name="Input Point A"
))

# Find overlapping region using discretization
if len(apollonius_circles) > 0:
    # Determine plotting range
    all_x_min = []
    all_x_max = []
    all_y_min = []
    all_y_max = []
    
    for cx, cy, r in apollonius_circles:
        all_x_min.append(cx - r)
        all_x_max.append(cx + r)
        all_y_min.append(cy - r)
        all_y_max.append(cy + r)
    
    plot_x_min = min(all_x_min + [x_a - 1])
    plot_x_max = max(all_x_max + [x_a + 1])
    plot_y_min = min(all_y_min + [y_a - 1])
    plot_y_max = max(all_y_max + [y_a + 1])
    
    # Create mesh for overlap detection
    x_mesh = np.linspace(plot_x_min, plot_x_max, resolution)
    y_mesh = np.linspace(plot_y_min, plot_y_max, resolution)
    X, Y = np.meshgrid(x_mesh, y_mesh)
    
    # Check which mesh points are inside all circles
    Z = np.ones_like(X, dtype=bool)     # all True to start
    for cx, cy, r in apollonius_circles:
        inside = (X - cx)**2 + (Y - cy)**2 <= r**2
        Z &= inside                     # logical AND on bool arrays

    # For the contour we want numeric values (0/1)
    Z_float = Z.astype(float)
    fig.add_trace(
        go.Contour(
            x=x_mesh,
            y=y_mesh,
            z=Z_float,
            showscale=False,
            contours=dict(start=0.5, end=1.5, size=1, coloring="fill"),
            colorscale=[[0, "white"], [1, "lightblue"]],
            name="Overlap Region",
        )
    )
    
    # Add contour for the overlap region
    fig.add_trace(go.Contour(
        x=x_mesh,
        y=y_mesh,
        z=Z.astype(float),
        showscale=False,
        contours=dict(
            start=0.5,
            end=1.5,
            size=1,
            coloring='fill'
        ),
        colorscale=[[0, 'white'], [1, 'lightblue']],
        name="Overlap Region"
    ))
    
    # Optionally add individual circle outlines (lighter)
    if st.checkbox("Show individual Apollonius circles", value=False):
        for i, (cx, cy, r) in enumerate(apollonius_circles):
            theta = np.linspace(0, 2*np.pi, 100)
            x_circle = cx + r * np.cos(theta)
            y_circle = cy + r * np.sin(theta)
            fig.add_trace(go.Scatter(
                x=x_circle,
                y=y_circle,
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Calculate center and range for equal axes
    center_x = (plot_x_min + plot_x_max) / 2
    center_y = (plot_y_min + plot_y_max) / 2
    half_range = max(plot_x_max - plot_x_min, plot_y_max - plot_y_min) / 2 * 1.1
    
else:
    st.warning("No valid Apollonius circles could be created with the current parameters.")
    center_x = x_a
    center_y = y_a
    half_range = 5

# Update layout
fig.update_layout(
    xaxis_title="x",
    yaxis_title="y",
    xaxis=dict(
        range=[center_x - half_range, center_x + half_range],
        scaleanchor="y",
        scaleratio=1,
    ),
    yaxis_range=[center_y - half_range, center_y + half_range],
    width=700,
    height=700,
    showlegend=True
)

# Display the plot
st.plotly_chart(fig)

# Information about the overlap
st.write(f"**Number of Apollonius circles:** {len(apollonius_circles)}")
if len(apollonius_circles) > 0:
    overlap_count = np.sum(Z)
    total_points = Z.size
    overlap_percentage = (overlap_count / total_points) * 100
    st.write(f"**Overlap area (approximate):** {overlap_percentage:.1f}% of the checked region")
