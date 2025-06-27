import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fractions import Fraction
import math

# App title and description
st.title("Apollonius Circle Overlap Plotter")
st.write("Adjust the sliders to change the input point A and grid density. The plot shows the overlapping region of Apollonius circles created between point A and a grid of points (optionally visible). The ratio k for each circle is computed as lcm_G / lcm_A, where lcm_G is the LCM of the denominators of the grid point coordinates, and lcm_A is that of the input point A. Only grid points with lcm_G <= lcm_A are considered.")

# Sliders for coordinates of point A
x_a = st.slider("x_A (Input Point)", min_value=-10.0, max_value=10.0, value=0.0, step=0.001)
y_a = st.slider("y_A (Input Point)", min_value=-10.0, max_value=10.0, value=0.0, step=0.001)

# Grid density slider
grid_density = st.slider("Grid Density", min_value=3, max_value=20, value=7, step=1)

# Resolution for overlap detection
resolution = st.slider("Overlap Resolution", min_value=50, max_value=200, value=100, step=10)

# Checkbox to show grid points
show_grid = st.checkbox("Show grid points", value=False)

# Create grid of points
grid_range = 20  # Range of the grid
x_grid = np.linspace(-grid_range/2, grid_range/2, grid_density)
y_grid = np.linspace(-grid_range/2, grid_range/2, grid_density)

# Compute all grid points for plotting
X, Y = np.meshgrid(x_grid, y_grid)
x_all = X.flatten()
y_all = Y.flatten()

# Function to calculate LCM of two numbers
def lcm(a, b):
    return (a * b) // math.gcd(a, b) if a > 0 and b > 0 else 0

# Function to get denominator of a float
def get_denominator(x, max_den=10000):
    f = Fraction(x).limit_denominator(max_den)
    return f.denominator

# Compute lcm_a for input point A
den_x_a = get_denominator(x_a)
den_y_a = get_denominator(y_a)
lcm_a = lcm(den_x_a, den_y_a)

# Function to calculate Apollonius circle parameters
def apollonius_circle(x1, y1, x2, y2, k):
    """
    Calculate center and radius of Apollonius circle for points (x1,y1) and (x2,y2) with ratio k
    Returns (center_x, center_y, radius) or None if circle doesn't exist
    """
    g = (k**2 * x2 - x1)/(1 - k**2)
    f = (k**2 * y2 - y1)/(1 - k**2)
    c = (x1**2 + y1**2 - k**2 * x2**2 - k**2 * y2**2)/(1 - k**2)
    
    r = np.sqrt(g**2 + f**2 - c)
    return -g, -f, r

# Collect all valid Apollonius circles
apollonius_circles = []
for xi in x_grid:
    for yi in y_grid:
        # Skip if grid point is too close to input point
        if abs(xi - x_a) < 1e-6 and abs(yi - y_a) < 1e-6:
            continue
        # Compute lcm_g for the grid point
        den_x_g = get_denominator(xi)
        den_y_g = get_denominator(yi)
        lcm_g = lcm(den_x_g, den_y_g)
        # Discard circle if lcm_g > lcm_a or lcm_g is invalid
        if lcm_g > lcm_a or lcm_g == 0:
            continue
        # Calculate k as lcm_g / lcm_a
        k = lcm_g / lcm_a
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

# Add grid points if checkbox is checked
if show_grid:
    fig.add_trace(go.Scatter(
        x=x_all,
        y=y_all,
        mode='markers',
        marker=dict(size=3, color='gray', opacity=0.5),
        name='Grid Points'
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
    Z = np.ones_like(X, dtype=bool)  # Start with all True
    for cx, cy, r in apollonius_circles:
        inside = (X - cx)**2 + (Y - cy)**2 <= r**2
        Z &= inside  # Logical AND to find overlap
    
    # Convert to float for contour plotting
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
    
    # Optional: Show individual circles
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
st.write(f"**LCM of input point A denominators:** {lcm_a}")
st.write(f"**Number of Apollonius circles:** {len(apollonius_circles)}")
if len(apollonius_circles) > 0:
    overlap_count = np.sum(Z)
    total_points = Z.size
    overlap_percentage = (overlap_count / total_points) * 100
    st.write(f"**Overlap area (approximate):** {overlap_percentage:.4f}% of the checked region")
