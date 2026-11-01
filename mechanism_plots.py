"""Plotly figures and small illustrative calculations for the Mechanism page.

Schematics are drawn with Plotly shapes on hidden axes, so their positions are
plain drawing coordinates, not engineering units. The charts use real units.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

from modules.isotherms import batch_operating_line

# One colour per material, used in all three tabs. Both pass the colour-blind
# and contrast checks on light and dark backgrounds.
FLUID_COLOR = "#2a78d6"
ADSORBENT_COLOR = "#d95926"
EQUIPMENT_COLOR = "#898781"
GRID_COLOR = "rgba(137, 135, 129, 0.25)"

# Fixed bed colour scale: pale means fresh, full adsorbent colour means saturated.
COLUMN_COLORSCALE = [[0.0, "#fbe4d8"], [1.0, ADSORBENT_COLOR]]

# Marker for "you are here" points. A white centre reads on either background.
CURRENT_POINT = dict(size=14, color="#ffffff", line=dict(color="#52514e", width=3))

# Illustrative countercurrent example.
COUNTERCURRENT_FEED = 100.0  # c_F, mg/L
ADSORPTION_FACTOR = 1.5  # A = K_lin * M / S, dimensionless
MAX_STAGES = 5

# Illustrative fixed bed example.
BED_HEIGHT = 100.0  # H_T, cm
MID_TIME = 100.0  # t_50, min (time when the outlet reaches c/c_0 = 0.5)
STEEPNESS = 0.15  # k, 1/min (larger values give a sharper curve and shorter MTZ)
BREAK_RATIO = 0.05  # c/c_0 taken as the breakthrough point
END_TIME = 200.0  # last time shown, min


# ---------------------------------------------------------------------------
# Small illustrative calculations
# ---------------------------------------------------------------------------


def stage_concentrations(c_F, A, n_stages):
    """Fluid concentration leaving each ideal countercurrent stage, in mg/L.

    Assumes a linear isotherm q = K_lin * c and fresh adsorbent (q_in = 0). Fluid
    enters stage 1 and adsorbent enters stage N. The solute balance around stage
    i then gives c_(i-1) + A * c_(i+1) = (1 + A) * c_i, which solves to

        c_i / c_F = (A^(N + 1 - i) - 1) / (A^(N + 1) - 1)

    Args:
        c_F: Feed concentration in mg/L.
        A: Adsorption factor K_lin * M / S (dimensionless).
        n_stages: Number of stages N.

    Returns:
        Array of c_1 to c_N in mg/L. The last value is the outlet concentration.
    """
    i = np.arange(1, n_stages + 1)
    if np.isclose(A, 1.0):
        # The formula above becomes 0/0 at A = 1, and this is its limit.
        return c_F * (n_stages + 1 - i) / (n_stages + 1)
    return c_F * (A ** (n_stages + 1 - i) - 1) / (A ** (n_stages + 1) - 1)


def single_stage_adsorbent_ratio(c_F, c_out, A):
    """How many times more adsorbent one stage needs to reach the same c_out.

    A single ideal stage gives c_out = c_F / (1 + A_single), so it needs
    A_single = c_F / c_out - 1. Dividing by A compares the adsorbent amounts.
    """
    return (c_F / c_out - 1.0) / A


def breakthrough_ratio(t, depth_fraction=1.0):
    """Illustrative c/c_0 from a logistic function, at any depth in the bed.

    Args:
        t: Time in min. A single number or a NumPy array.
        depth_fraction: Position z / H_T, where 0 is the inlet and 1 the outlet.

    Returns:
        c/c_0 (dimensionless). The same function drives both the column colours
        and the breakthrough curve, so the two views always agree.
    """
    return 1.0 / (1.0 + np.exp(-STEEPNESS * (t - MID_TIME * depth_fraction)))


def breakthrough_time():
    """Time in min when the outlet reaches BREAK_RATIO, from the logistic."""
    return MID_TIME - _mtz_half_time()


def _mtz_half_time():
    """Time in min between the middle of the MTZ and either edge of it."""
    return np.log((1.0 - BREAK_RATIO) / BREAK_RATIO) / STEEPNESS


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------


def _schematic_canvas(x_range, y_range, height):
    """Create an empty figure with hidden axes for drawing a diagram on."""
    fig = go.Figure()
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        dragmode=False,
    )
    fig.update_xaxes(visible=False, range=x_range, fixedrange=True)
    fig.update_yaxes(visible=False, range=y_range, fixedrange=True)
    return fig


def _arrow(fig, start, end, color, width=3):
    """Draw a flow arrow from start (x, y) to end (x, y)."""
    fig.add_annotation(
        x=end[0],
        y=end[1],
        ax=start[0],
        ay=start[1],
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        text="",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.1,
        arrowwidth=width,
        arrowcolor=color,
    )


def _bed_color(loading):
    """Colour on the fixed bed scale, for a loading from 0 (fresh) to 1 (saturated)."""
    return sample_colorscale(COLUMN_COLORSCALE, [loading])[0]


def _label(fig, x, y, text, size=13, **kwargs):
    """Place plain text on a diagram. Colour follows the page theme."""
    fig.add_annotation(
        x=x, y=y, text=text, showarrow=False, font=dict(size=size), **kwargs
    )


def _style_chart(fig, x_title, y_title, height, title=None):
    """Apply the same axes, grid and spacing to every chart."""
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(size=15)) if title else None,
        margin=dict(l=60, r=24, t=70 if title else 40, b=56),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        hovermode="closest",
    )
    fig.update_xaxes(title_text=x_title, gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(title_text=y_title, gridcolor=GRID_COLOR, zeroline=False)


# ---------------------------------------------------------------------------
# Tab 1: stirred tank
# ---------------------------------------------------------------------------


def stirred_tank_schematic():
    """Diagram of a stirred tank followed by a filter."""
    fig = _schematic_canvas([0, 13], [-0.2, 6.4], 400)

    # Tank walls and the solution inside. The top is left open.
    fig.add_shape(
        type="rect",
        x0=3.2,
        x1=6.8,
        y0=0.8,
        y1=3.9,
        fillcolor=FLUID_COLOR,
        opacity=0.15,
        line_width=0,
    )
    fig.add_shape(
        type="path",
        path="M 3.2 4.6 L 3.2 0.8 L 6.8 0.8 L 6.8 4.6",
        line=dict(color=EQUIPMENT_COLOR, width=3),
    )

    # Stirrer: motor, shaft and two paddle blades.
    fig.add_shape(
        type="rect",
        x0=4.6,
        x1=5.4,
        y0=5.2,
        y1=5.8,
        fillcolor=EQUIPMENT_COLOR,
        line_width=0,
    )
    fig.add_shape(
        type="line",
        x0=5,
        x1=5,
        y0=1.7,
        y1=5.2,
        line=dict(color=EQUIPMENT_COLOR, width=3),
    )
    for x0, x1 in [(4.1, 4.95), (5.05, 5.9)]:
        fig.add_shape(
            type="circle",
            x0=x0,
            x1=x1,
            y0=1.55,
            y1=1.85,
            fillcolor=EQUIPMENT_COLOR,
            line_width=0,
        )

    # Adsorbent particles suspended in the solution. The fixed seed keeps them
    # in the same place every time the page redraws.
    rng = np.random.default_rng(7)
    fig.add_trace(
        go.Scatter(
            x=rng.uniform(3.5, 6.5, 26),
            y=rng.uniform(1.05, 3.65, 26),
            mode="markers",
            marker=dict(size=9, color=ADSORBENT_COLOR),
            hoverinfo="skip",
        )
    )

    # Streams in and out of the tank.
    _arrow(fig, (0.4, 3.3), (3.1, 3.3), FLUID_COLOR)
    _label(fig, 1.7, 4.0, "Solution in<br>S (L), c<sub>F</sub> (mg/L)")
    _arrow(fig, (6.2, 6.0), (6.2, 4.0), ADSORBENT_COLOR)
    _label(fig, 6.5, 5.5, "Adsorbent added<br>M (g), q<sub>F</sub> (mg/g)", xanchor="left")

    # After equilibrium the slurry goes to a filter, which splits the two phases.
    _arrow(fig, (6.8, 1.4), (8.9, 1.4), EQUIPMENT_COLOR)
    _label(fig, 7.85, 2.0, "Slurry at<br>equilibrium", size=12)
    fig.add_shape(
        type="rect",
        x0=8.9,
        x1=10.7,
        y0=0.7,
        y1=2.1,
        fillcolor="rgba(137, 135, 129, 0.15)",
        line=dict(color=EQUIPMENT_COLOR, width=2),
    )
    _label(fig, 9.8, 1.4, "Filter")
    _arrow(fig, (10.7, 1.8), (12.9, 1.8), FLUID_COLOR)
    _label(fig, 11.8, 2.5, "Treated solution<br>c (mg/L)")
    _arrow(fig, (10.7, 1.0), (12.9, 1.0), ADSORBENT_COLOR)
    _label(fig, 11.8, 0.3, "Spent adsorbent<br>q (mg/g)")
    return fig


def batch_equilibrium_plot(c_F, S, M, isotherm, c_eq, q_eq, q_F=0.0):
    """Isotherm and operating line on a q vs c graph, with their crossing marked.

    Args:
        c_F: Feed concentration in mg/L.
        S: Volume of solution in L.
        M: Mass of adsorbent in g.
        isotherm: Function that takes c in mg/L and returns q in mg/g.
        c_eq: Equilibrium concentration in mg/L.
        q_eq: Equilibrium loading in mg/g.
        q_F: Initial loading on the adsorbent in mg/g.
    """
    c = np.linspace(0.0, c_F * 1.1, 300)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=c,
            y=isotherm(c),
            mode="lines",
            name="Isotherm (equilibrium)",
            line=dict(color=ADSORBENT_COLOR, width=2.5),
            hovertemplate="c = %{x:.1f} mg/L<br>q = %{y:.1f} mg/g<extra>Isotherm</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=c,
            y=batch_operating_line(c, c_F, S, M, q_F),
            mode="lines",
            name="Operating line (slope −S/M)",
            line=dict(color=FLUID_COLOR, width=2.5),
            hovertemplate="c = %{x:.1f} mg/L<br>q = %{y:.1f} mg/g<extra>Operating line</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[c_eq],
            y=[q_eq],
            mode="markers",
            name="Equilibrium point",
            marker=CURRENT_POINT,
            hovertemplate="c = %{x:.1f} mg/L<br>q = %{y:.1f} mg/g<extra>Equilibrium</extra>",
        )
    )
    # The label sits to the right, in the gap that opens between the two lines.
    fig.add_annotation(
        x=c_eq,
        y=q_eq,
        text=f"Equilibrium<br>c = {c_eq:.1f} mg/L<br>q = {q_eq:.1f} mg/g",
        align="left",
        ax=75,
        ay=0,
        xanchor="left",
        arrowcolor=EQUIPMENT_COLOR,
        arrowwidth=1,
        arrowhead=0,
    )

    # A very steep operating line would stretch the axis and flatten the
    # isotherm, so the q axis follows the isotherm and the equilibrium point.
    q_top = 1.25 * max(float(isotherm(c_F)), q_eq)
    _style_chart(fig, "Fluid concentration c (mg/L)", "Loading q (mg/g)", 460)
    fig.update_xaxes(range=[0, c_F * 1.1])
    fig.update_yaxes(range=[0, q_top])
    return fig


# ---------------------------------------------------------------------------
# Tab 2: continuous countercurrent
# ---------------------------------------------------------------------------


def countercurrent_schematic(n_stages, animate=False):
    """Row of stages with fluid flowing right and adsorbent flowing left.

    Args:
        n_stages: Number of stages to draw.
        animate: If True, add moving dots and Play and Pause buttons, and show
            the illustrative concentration leaving each stage.
    """
    stage_width, stage_gap = 1.6, 0.9
    row_width = n_stages * stage_width + (n_stages - 1) * stage_gap
    lefts = 5.8 - row_width / 2 + np.arange(n_stages) * (stage_width + stage_gap)
    rights = lefts + stage_width
    centers = lefts + stage_width / 2

    x_in, x_out = -2.6, 14.2  # where the pipes start and end
    fluid_y, adsorbent_y = 0.45, -0.45
    fig = _schematic_canvas([-3.0, 14.6], [-2.1, 2.1], 300)

    c_stages = stage_concentrations(COUNTERCURRENT_FEED, ADSORPTION_FACTOR, n_stages)
    for i in range(n_stages):
        fig.add_shape(
            type="rect",
            x0=lefts[i],
            x1=rights[i],
            y0=-1,
            y1=1,
            fillcolor="rgba(137, 135, 129, 0.15)",
            line=dict(color=EQUIPMENT_COLOR, width=2),
        )
        _label(fig, centers[i], 1.3, f"Stage {i + 1}")
        if animate:
            _label(fig, centers[i], 0, f"{c_stages[i]:.1f} mg/L", size=12)

    # Pipe sections: before the first stage, between stages, after the last.
    # Thinner pipes in the animation keep the moving dots easy to see.
    starts = np.concatenate(([x_in], rights))
    ends = np.concatenate((lefts, [x_out]))
    pipe_width = 1 if animate else 3
    for start, end in zip(starts, ends):
        _arrow(fig, (start, fluid_y), (end, fluid_y), FLUID_COLOR, pipe_width)
        _arrow(fig, (end, adsorbent_y), (start, adsorbent_y), ADSORBENT_COLOR, pipe_width)

    _label(fig, -1.5, 1.15, "Feed<br>c<sub>F</sub> (mg/L)", size=12)
    _label(fig, 13.1, 1.15, "Treated fluid<br>c<sub>out</sub> (mg/L)", size=12)
    _label(fig, 13.1, -1.15, "Fresh adsorbent<br>q<sub>in</sub> (mg/g)", size=12)
    _label(fig, -1.5, -1.15, "Spent adsorbent<br>q<sub>out</sub> (mg/g)", size=12)

    if animate:
        _add_flow_animation(
            fig, x_in, x_out, fluid_y, adsorbent_y, centers, c_stages
        )
    return fig


def _add_flow_animation(fig, x_in, x_out, fluid_y, adsorbent_y, centers, c_stages):
    """Add dots that travel along both streams, plus Play and Pause buttons.

    Fluid dots fade as solute is removed. Adsorbent dots start faint and grow
    stronger as they load up.
    """
    spacing, frames_per_spacing, n_frames = 1.2, 10, 200
    path_length = x_out - x_in
    base = np.arange(0.0, path_length, spacing)

    # Strength along each path, from 0 (no solute) to 1 (strongest).
    path_x = np.concatenate(([x_in], centers, [x_out]))
    fluid_strength = np.concatenate(
        ([1.0], c_stages / COUNTERCURRENT_FEED, [c_stages[-1] / COUNTERCURRENT_FEED])
    )
    # q is proportional to c for a linear isotherm. Fresh adsorbent has q = 0.
    adsorbent_strength = np.concatenate(([1.0], c_stages / c_stages[0], [0.0]))

    def dot_traces(frame):
        travelled = (base + frame * spacing / frames_per_spacing) % path_length
        fluid_x = x_in + travelled
        adsorbent_x = x_out - travelled
        fluid_opacity = 0.2 + 0.8 * np.interp(fluid_x, path_x, fluid_strength)
        adsorbent_opacity = 0.2 + 0.8 * np.interp(
            adsorbent_x, path_x, adsorbent_strength
        )
        return [
            go.Scatter(
                x=fluid_x,
                y=np.full(base.size, fluid_y),
                mode="markers",
                marker=dict(size=11, color=FLUID_COLOR, opacity=fluid_opacity),
                hoverinfo="skip",
            ),
            go.Scatter(
                x=adsorbent_x,
                y=np.full(base.size, adsorbent_y),
                mode="markers",
                marker=dict(size=11, color=ADSORBENT_COLOR, opacity=adsorbent_opacity),
                hoverinfo="skip",
            ),
        ]

    fig.add_traces(dot_traces(0))
    fig.frames = [go.Frame(data=dot_traces(i), name=str(i)) for i in range(n_frames)]

    play = dict(
        frame=dict(duration=70, redraw=False),
        transition=dict(duration=0),
        mode="immediate",
    )
    pause = dict(
        frame=dict(duration=0, redraw=False),
        transition=dict(duration=0),
        mode="immediate",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=44, b=0),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0,
                y=1.0,
                xanchor="left",
                yanchor="bottom",
                showactive=False,
                bgcolor="#ffffff",
                bordercolor=EQUIPMENT_COLOR,
                font=dict(color="#0b0b0b"),
                buttons=[
                    dict(label="Play", method="animate", args=[None, play]),
                    dict(label="Pause", method="animate", args=[[None], pause]),
                ],
            )
        ],
    )


def countercurrent_comparison_plot(n_selected):
    """Outlet concentration against the number of stages, for the illustrative case.

    Args:
        n_selected: Stage count to highlight on the curve.
    """
    stages = np.arange(1, MAX_STAGES + 1)
    outlets = [
        stage_concentrations(COUNTERCURRENT_FEED, ADSORPTION_FACTOR, n)[-1]
        for n in stages
    ]
    single_stage = COUNTERCURRENT_FEED / (1.0 + ADSORPTION_FACTOR)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[1, MAX_STAGES],
            y=[single_stage, single_stage],
            mode="lines",
            name="Single stage, same adsorbent",
            line=dict(color=EQUIPMENT_COLOR, width=2),
            hovertemplate="%{y:.1f} mg/L<extra>Single stage</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=stages,
            y=outlets,
            mode="lines+markers",
            name="Countercurrent",
            line=dict(color=FLUID_COLOR, width=2.5),
            marker=dict(size=9, color=FLUID_COLOR),
            hovertemplate="N = %{x}<br>c<sub>out</sub> = %{y:.1f} mg/L<extra></extra>",
        )
    )
    selected = outlets[n_selected - 1]
    fig.add_trace(
        go.Scatter(
            x=[n_selected],
            y=[selected],
            mode="markers",
            marker=CURRENT_POINT,
            showlegend=False,
            hovertemplate="N = %{x}<br>c<sub>out</sub> = %{y:.1f} mg/L<extra></extra>",
        )
    )
    fig.add_annotation(
        x=n_selected,
        y=selected,
        text=f"N = {n_selected}: {selected:.1f} mg/L",
        ax=0,
        ay=-30,
        arrowcolor=EQUIPMENT_COLOR,
        arrowwidth=1,
        arrowhead=0,
    )

    _style_chart(
        fig,
        "Number of stages N",
        "Outlet concentration c<sub>out</sub> (mg/L)",
        400,
        title="Illustrative only: ideal stages and a linear isotherm",
    )
    fig.update_xaxes(
        tickvals=stages, range=[0.7, MAX_STAGES + 0.3], showgrid=False
    )
    fig.update_yaxes(range=[0, single_stage * 1.3])
    return fig


# ---------------------------------------------------------------------------
# Tab 3: fixed bed
# ---------------------------------------------------------------------------


def fixed_bed_schematic():
    """Diagram of a packed column with its saturated, MTZ and fresh zones."""
    fig = _schematic_canvas([0, 12], [0, 8], 440)
    left, right, top, bottom = 3.4, 5.2, 6.9, 1.1
    mtz_top, mtz_bottom = 5.1, 3.1

    def fill_zone(lower, upper, loading):
        # The outline matches the fill so no gaps show between the bands.
        color = _bed_color(loading)
        fig.add_shape(
            type="rect",
            x0=left,
            x1=right,
            y0=lower,
            y1=upper,
            fillcolor=color,
            line=dict(color=color, width=1),
        )

    # The colours match the column in the demo, on either page theme.
    fill_zone(mtz_top, top, 1.0)
    fill_zone(bottom, mtz_bottom, 0.0)

    # Thin bands fade from saturated to fresh across the MTZ.
    n_bands = 30
    edges = np.linspace(mtz_top, mtz_bottom, n_bands + 1)
    for i, (upper, lower) in enumerate(zip(edges[:-1], edges[1:])):
        fill_zone(lower, upper, 1.0 - (i + 0.5) / n_bands)

    fig.add_shape(
        type="rect",
        x0=left,
        x1=right,
        y0=bottom,
        y1=top,
        line=dict(color=EQUIPMENT_COLOR, width=3),
    )

    # Flow through the column.
    middle = (left + right) / 2
    _arrow(fig, (middle, 7.9), (middle, 7.0), FLUID_COLOR)
    _label(fig, middle + 0.3, 7.5, "Feed in, c<sub>0</sub> (mg/L)", xanchor="left")
    _arrow(fig, (middle, 1.0), (middle, 0.1), FLUID_COLOR)
    _label(fig, middle + 0.3, 0.5, "Outlet, c (mg/L)", xanchor="left")

    # Zone names beside the column.
    _label(fig, 5.5, 6.0, "<b>Saturated zone</b><br>adsorbent is full", xanchor="left")
    _label(fig, 5.5, 4.1, "<b>Mass transfer zone (MTZ)</b><br>adsorption happens here", xanchor="left")
    _label(fig, 5.5, 2.1, "<b>Fresh zone</b><br>adsorbent is still empty", xanchor="left")

    # MTZ direction and total height, to the left of the column.
    _arrow(fig, (2.9, 5.0), (2.9, 3.2), EQUIPMENT_COLOR, width=2)
    _label(fig, 2.7, 4.1, "MTZ moves<br>down", xanchor="right", size=12)
    height_middle = (top + bottom) / 2
    _arrow(fig, (0.9, height_middle), (0.9, top), EQUIPMENT_COLOR, width=1)
    _arrow(fig, (0.9, height_middle), (0.9, bottom), EQUIPMENT_COLOR, width=1)
    _label(fig, 1.0, 2.0, "H<sub>T</sub> (cm)", xanchor="left", size=12)
    return fig


def fixed_bed_column(t):
    """Column coloured by loading at time t, with the MTZ picked out.

    Args:
        t: Time since the start of the run, in min.
    """
    depth = np.linspace(0.0, BED_HEIGHT, 201)
    loading = breakthrough_ratio(t, depth / BED_HEIGHT)

    fig = go.Figure(
        go.Heatmap(
            z=np.column_stack((loading, loading)),
            x=[0, 1],
            y=depth,
            zmin=0,
            zmax=1,
            colorscale=COLUMN_COLORSCALE,
            colorbar=dict(
                title=dict(text="Bed loading"),
                tickvals=[0, 1],
                ticktext=["Fresh", "Saturated"],
                thickness=12,
                len=0.6,
            ),
            hovertemplate="Depth %{y:.0f} cm<extra></extra>",
        )
    )
    fig.add_shape(
        type="rect",
        x0=-0.5,
        x1=1.5,
        y0=0,
        y1=BED_HEIGHT,
        line=dict(color=EQUIPMENT_COLOR, width=2),
    )

    _arrow(fig, (0.5, -20), (0.5, -2), FLUID_COLOR)
    _arrow(fig, (0.5, BED_HEIGHT + 2), (0.5, BED_HEIGHT + 20), FLUID_COLOR)
    _label(fig, 0.8, -12, "Feed in", xanchor="left", size=12)
    _label(fig, 0.8, BED_HEIGHT + 12, "Outlet", xanchor="left", size=12)

    # MTZ edges, where the local c/c_0 is 0.95 and 0.05. They move with time and
    # are limited to the bed, so a zone outside the column gets no label.
    half_length = BED_HEIGHT * _mtz_half_time() / MID_TIME
    front = BED_HEIGHT * t / MID_TIME
    mtz_top = float(np.clip(front - half_length, 0.0, BED_HEIGHT))
    mtz_bottom = float(np.clip(front + half_length, 0.0, BED_HEIGHT))
    for edge in (mtz_top, mtz_bottom):
        if 0.0 < edge < BED_HEIGHT:
            fig.add_shape(
                type="line",
                x0=1.5,
                x1=1.9,
                y0=edge,
                y1=edge,
                line=dict(color=EQUIPMENT_COLOR, width=1),
            )
    zones = [
        ("Saturated", 0.0, mtz_top),
        ("MTZ", mtz_top, mtz_bottom),
        ("Fresh", mtz_bottom, BED_HEIGHT),
    ]
    for name, zone_top, zone_bottom in zones:
        if zone_bottom - zone_top >= 6.0:
            _label(fig, 1.95, (zone_top + zone_bottom) / 2, name, xanchor="left", size=12)

    _style_chart(fig, None, "Depth in bed (cm)", 480)
    fig.update_xaxes(visible=False, range=[-1.0, 3.6], fixedrange=True)
    fig.update_yaxes(
        range=[BED_HEIGHT + 24, -24],
        tickvals=np.arange(0, BED_HEIGHT + 1, 25),
        showgrid=False,
        fixedrange=True,
    )
    return fig


def breakthrough_plot(t):
    """Illustrative S-shaped breakthrough curve with a marker at time t.

    Args:
        t: Time since the start of the run, in min.
    """
    times = np.linspace(0.0, END_TIME, 401)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=breakthrough_ratio(times),
            mode="lines",
            line=dict(color=FLUID_COLOR, width=2.5),
            hovertemplate="t = %{x:.0f} min<br>c/c<sub>0</sub> = %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[t],
            y=[breakthrough_ratio(t)],
            mode="markers",
            marker=CURRENT_POINT,
            hovertemplate="t = %{x:.0f} min<br>c/c<sub>0</sub> = %{y:.2f}<extra></extra>",
        )
    )

    # For this symmetric curve t_t falls at the midpoint of the S.
    for time, name in [(breakthrough_time(), "t<sub>b</sub>"), (MID_TIME, "t<sub>t</sub>")]:
        fig.add_shape(
            type="line",
            x0=time,
            x1=time,
            y0=0,
            y1=1.04,
            line=dict(color=EQUIPMENT_COLOR, width=1),
        )
        _label(fig, time, 1.08, name)

    _style_chart(
        fig,
        "Time t (min)",
        "Outlet c/c<sub>0</sub> (dimensionless)",
        480,
        title="Illustrative curve from a logistic function, not real data",
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(range=[0, END_TIME])
    fig.update_yaxes(range=[-0.04, 1.14], tickvals=[0, 0.25, 0.5, 0.75, 1.0])
    return fig
