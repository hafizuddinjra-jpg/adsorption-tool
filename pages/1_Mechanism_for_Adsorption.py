"""Mechanism for Adsorption: three contacting modes and a comparison table.

This page holds the text, controls and layout. The published isotherm data are
in modules/literature_isotherms.py and the figures are in modules/mechanism_plots.py.
"""

import pandas as pd
import streamlit as st

from modules.literature_isotherms import (
    C_MAX,
    CARBONS,
    CITATION,
    CONDITIONS,
    DOI_URL,
    LICENCE,
    MODELS,
    model_loading,
)
from modules.mechanism_plots import (
    END_TIME,
    breakthrough_plot,
    breakthrough_ratio,
    breakthrough_time,
    countercurrent_schematic,
    fixed_bed_column,
    fixed_bed_schematic,
    literature_isotherm_plot,
    stirred_tank_schematic,
)

st.set_page_config(page_title="Mechanism for Adsorption", layout="wide")

# Hide the Plotly toolbar. Students use the sliders, not the zoom tools.
CHART_CONFIG = {"displayModeBar": False}


def show_chart(fig, key):
    """Draw a figure at full width. Each chart needs its own key across tabs."""
    # Streamlit's default chart text is a pale grey, which is hard to read on the
    # small diagram labels, so the text colour follows the page theme instead.
    # The theme in .streamlit/config.toml wins; without one, follow the viewer's.
    base = st.get_option("theme.base") or st.context.theme.type
    if base == "dark":
        ink = "#fafafa"
    else:
        ink = st.get_option("theme.textColor") or "#31333f"
    fig.update_layout(font_color=ink)
    fig.update_xaxes(title_font_color=ink)
    fig.update_yaxes(title_font_color=ink)
    st.plotly_chart(fig, width="stretch", key=key, config=CHART_CONFIG)


def show_pros_and_cons(advantages, disadvantages, applications):
    """Show the three bullet lists that every tab shares, side by side."""
    sections = [
        ("Advantages", advantages),
        ("Disadvantages", disadvantages),
        ("Typical applications", applications),
    ]
    for column, (title, items) in zip(st.columns(3), sections):
        with column:
            st.markdown(f"#### {title}")
            st.markdown("\n".join(f"- {item}" for item in items))


# ---------------------------------------------------------------------------
# Tab 1: stirred tank
# ---------------------------------------------------------------------------


def journal_isotherm_section():
    """Published isotherms for methylene blue on activated carbon, with their source."""
    st.markdown("#### From a journal: methylene blue on activated carbon")
    st.markdown(
        "Lawtae and Tangsathitkulchai (2021) made six activated carbons from longan "
        "fruit seeds and measured how much methylene blue (MB) dye each one adsorbs "
        "at equilibrium. They fitted three isotherm models to their data. The curves "
        "below use the constants they published."
    )
    st.caption(
        f"Batch tests: {CONDITIONS['volume_mL']} mL of MB solution at "
        f"{CONDITIONS['initial_conc_mg_L']} mg/L with {CONDITIONS['carbon_g']} g of "
        f"carbon, {CONDITIONS['temperature_C']} °C, pH {CONDITIONS['pH']}, and "
        f"{CONDITIONS['contact_time_h']} h to reach equilibrium. The constants come "
        "from non-linear regression."
    )

    controls, chart = st.columns([1, 2])
    with controls:
        carbon = st.selectbox(
            "Activated carbon",
            list(CARBONS),
            index=5,
            format_func=lambda k: (
                f"{k}: {CARBONS[k]['pores'].lower()}, {CARBONS[k]['bet_m2_g']:,} m²/g"
            ),
            key="lit_carbon",
        )
        data = CARBONS[carbon]
        st.caption(f"{data['sample']}, made by {data['made_by']}.")
        st.markdown("Models to show")
        models = [m for m in MODELS if st.checkbox(m, value=True, key=f"lit_model_{m}")]
        c_read = st.slider(
            "Read the curves at $C_e$ (mg/L)", 0, int(C_MAX), 100, 5, key="lit_c_read"
        )
    with chart:
        if models:
            show_chart(literature_isotherm_plot(carbon, models, c_read), "lit_plot")
        else:
            st.info("Tick at least one model to draw its curve.")

    if models:
        for column, model in zip(st.columns(len(MODELS)), models):
            best = " (best fit)" if model == data["best"] else ""
            column.metric(
                f"{model}{best}, q_e (mg/g)", f"{float(model_loading(carbon, model, c_read)):.0f}"
            )
        st.caption(f"Each value is the predicted loading at C_e = {c_read} mg/L.")

    lp, fp, rp = data["langmuir"], data["freundlich"], data["redlich_peterson"]
    st.table(
        pd.DataFrame(
            {
                "Model": list(MODELS),
                "Constants": [
                    f"q_m = {lp['q_m']:.2f} mg/g, K_L = {lp['K_L']:.3f} L/mg",
                    f"K_F = {fp['K_F']:.1f}, n_F = {fp['n_F']:.2f}",
                    f"K_R = {rp['K_R']:.1f} L/g, A_R = {rp['A_R']:.2f}, β = {rp['beta']:.2f}",
                ],
                "R²": [f"{p['R2']:.3f}" for p in (lp, fp, rp)],
                "Δq (%)": [f"{p['dq']:.2f}" for p in (lp, fp, rp)],
                "Authors' best fit": ["Yes" if m == data["best"] else "" for m in MODELS],
            }
        ).set_index("Model")
    )
    st.caption(
        "Δq is the authors' relative error, so a lower value means a closer fit. "
        "The paper prints no units for K_F and A_R."
    )

    st.markdown("**The models as the paper writes them**")
    st.latex(r"q_e = \frac{q_m K_L C_e}{1 + K_L C_e} \quad \text{(Langmuir)}")
    st.latex(r"q_e = K_F\, C_e^{1/n_F} \quad \text{(Freundlich)}")
    st.latex(r"q_e = \frac{K_R C_e}{1 + A_R C_e^{\beta}} \quad \text{(Redlich-Peterson)}")
    st.markdown(
        "In the lecture's notation, this carbon's Langmuir constants are "
        f"$q_0 = q_m$ = {lp['q_m']:.0f} mg/g and $K = 1/K_L$ = {1 / lp['K_L']:.1f} mg/L. "
        f"Its Freundlich exponent is $n = 1/n_F$ = {1 / fp['n_F']:.3f}, because the "
        "lecture's $n$ is the paper's $1/n_F$. Redlich–Peterson blends the two: "
        "$\\beta = 1$ turns it into Langmuir, and at high $C_e$ it behaves like Freundlich."
    )
    st.markdown(
        "The authors found that Redlich–Peterson best describes the microporous "
        "carbons (A1–A3) and Freundlich the mesoporous ones (A4–A6)."
    )

    with st.expander("Constants for all six carbons (Table 7 of the paper)"):
        st.table(
            pd.DataFrame(
                [
                    {
                        "Carbon": k,
                        "Pores": v["pores"],
                        "BET (m²/g)": f"{v['bet_m2_g']:,}",
                        "q_m (mg/g)": f"{v['langmuir']['q_m']:.2f}",
                        "K_L (L/mg)": f"{v['langmuir']['K_L']:.3f}",
                        "Langmuir R²": f"{v['langmuir']['R2']:.3f}",
                        "K_F": f"{v['freundlich']['K_F']:.1f}",
                        "n_F": f"{v['freundlich']['n_F']:.2f}",
                        "Freundlich R²": f"{v['freundlich']['R2']:.3f}",
                        "K_R (L/g)": f"{v['redlich_peterson']['K_R']:.1f}",
                        "A_R": f"{v['redlich_peterson']['A_R']:.2f}",
                        "β": f"{v['redlich_peterson']['beta']:.2f}",
                        "R–P R²": f"{v['redlich_peterson']['R2']:.3f}",
                        "Best fit": v["best"],
                    }
                    for k, v in CARBONS.items()
                ]
            ).set_index("Carbon")
        )

    st.caption(
        "Curves are the authors' fitted models over the range they measured "
        f"(C_e up to {C_MAX:.0f} mg/L). Their measured points are plotted in Figure 4 "
        "of the paper and are not reproduced here."
    )
    st.markdown(f"Source: {CITATION} [{DOI_URL}]({DOI_URL}). Open access under {LICENCE}.")


def stirred_tank_tab():
    """Single-stage batch contacting."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(stirred_tank_schematic(), "st_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "1. Fill a tank with a known volume $S$ of solution at concentration "
            "$c_F$.\n"
            "2. Add a mass $M$ of adsorbent and stir, so every particle touches "
            "the solution.\n"
            "3. Solute moves onto the solid. The fluid concentration $c$ falls "
            "and the loading $q$ rises until they reach equilibrium.\n"
            "4. Stop stirring and separate the solid by filtering or settling."
        )

    st.markdown("#### Governing equations")
    st.markdown("Solute balance: what enters the tank equals what is there at the end.")
    st.latex(r"q_F M + c_F S = q M + c S")
    st.markdown("Rearranged, this is the operating line, with a slope of $-S/M$:")
    st.latex(r"q = q_F + \frac{S}{M}\,(c_F - c)")
    st.markdown("The isotherm gives the equilibrium relationship. Three common forms:")
    st.latex(r"q = K c \quad \text{(Linear, Henry's law, for dilute solutions)}")
    st.latex(r"q = K c^{\,n} \quad \text{(Freundlich)}")
    st.latex(r"q = \frac{q_0\, c}{K + c} \quad \text{(Langmuir)}")
    st.caption(
        "In each form, K (and n or $q_0$) are constants found by experiment at a "
        "fixed temperature."
    )
    st.markdown(
        "The answer lies where the operating line crosses the isotherm, because "
        "only that point satisfies both. The removal is then:"
    )
    st.latex(r"\%\ \text{removal} = \frac{c_F - c}{c_F} \times 100")

    show_pros_and_cons(
        advantages=[
            "Simple, low-cost equipment",
            "Works well with fine powdered adsorbents",
            "Easy to run in the lab, so it suits isotherm tests",
        ],
        disadvantages=[
            "One equilibrium stage limits the removal",
            "All the adsorbent ends in contact with the final, dilute fluid, so "
            "its capacity is under-used",
            "Solid must be separated from the fluid afterwards",
        ],
        applications=[
            "Decolourising sugar solutions and vegetable oils",
            "Small-volume water and wastewater treatment",
            "Laboratory screening of adsorbents",
        ],
    )

    st.divider()
    journal_isotherm_section()


# ---------------------------------------------------------------------------
# Tab 2: continuous countercurrent
# ---------------------------------------------------------------------------


def countercurrent_tab():
    """Multi-stage contacting with fluid and adsorbent flowing in opposite ways."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(countercurrent_schematic(3), "cc_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "Fluid and adsorbent flow in opposite directions through a series of "
            "stages. Fresh adsorbent meets the most dilute fluid, so it can still "
            "pull out the last of the solute. Nearly full adsorbent meets the "
            "strongest fluid, so it can still pick up more.\n\n"
            "This keeps a driving force in every stage. For the same removal, it "
            "needs less adsorbent than a single stage."
        )

    st.markdown("#### Governing equations")
    st.markdown(
        "Here $S$ and $M$ are flow rates, in L/min and g/min. The overall solute "
        "balance says that solute in equals solute out:"
    )
    st.latex(r"S c_F + M q_{in} = S c_{out} + M q_{out}")
    st.markdown("The operating line links the two streams passing each other:")
    st.latex(r"q = q_{in} + \frac{S}{M}\,(c - c_{out})")
    st.markdown(
        "Its slope is $+S/M$, whereas the single-stage line has a slope of $-S/M$. "
        "It runs from ($c_{out}$, $q_{in}$) at the dilute end to ($c_F$, $q_{out}$) "
        "at the strong end."
    )

    show_pros_and_cons(
        advantages=[
            "Highest driving force across the process",
            "Uses less adsorbent for the same removal",
            "Runs continuously at a steady outlet quality",
        ],
        disadvantages=[
            "Moving solids is mechanically difficult",
            "Particles wear down as they move",
            "More complex equipment and control",
        ],
        applications=[
            "Carbon-in-pulp gold recovery",
            "Moving-bed and pulsed-bed carbon columns for water treatment",
            "Simulated moving beds for xylene and sugar separation",
        ],
    )


# ---------------------------------------------------------------------------
# Tab 3: fixed bed
# ---------------------------------------------------------------------------


def bed_status(t):
    """Describe in words what the bed is doing at time t (min)."""
    t_b = breakthrough_time()
    ratio = float(breakthrough_ratio(t))
    if t < t_b:
        return (
            f"Outlet c/c₀ = {ratio:.2f}. The MTZ is still inside the bed, so the "
            "outlet stays clean."
        )
    if ratio < 0.95:
        return (
            f"Outlet c/c₀ = {ratio:.2f}. The MTZ has reached the outlet, so solute "
            "is breaking through. A real bed would already be stopped."
        )
    return (
        f"Outlet c/c₀ = {ratio:.2f}. The whole bed is saturated, so solute passes "
        "straight through."
    )


def fixed_bed_demo():
    """Time slider driving the column and the breakthrough curve together."""
    st.markdown("#### Try it: watch the MTZ move")
    st.caption(
        "Illustrative only. Both views come from one logistic function for a bed of "
        "height $H_T$ = 100 cm, not from real data."
    )

    t = st.slider(
        "Time since the start of the run (min)",
        0,
        int(END_TIME),
        50,
        1,
        key="fb_time",
    )
    column, curve = st.columns([2, 3])
    with column:
        show_chart(fixed_bed_column(t), "fb_column")
    with curve:
        show_chart(breakthrough_plot(t), "fb_breakthrough")
    st.markdown(f"**At t = {t} min:** {bed_status(t)}")


def fixed_bed_tab():
    """Packed column with fluid flowing through a stationary adsorbent."""
    schematic, explanation = st.columns([3, 2])
    with schematic:
        show_chart(fixed_bed_schematic(), "fb_schematic")
    with explanation:
        st.markdown("#### How it works")
        st.markdown(
            "Fluid flows through a column packed with adsorbent while the solid "
            "stays still. The bed near the inlet fills up first and becomes the "
            "**saturated zone**. Just ahead of it is the **mass transfer zone "
            "(MTZ)**, where the concentration falls from $c_0$ to almost zero. "
            "Further on, the **fresh zone** has not yet taken up any solute.\n\n"
            "The MTZ moves down the bed with time. While it stays inside the bed, "
            "the outlet is almost free of solute."
        )

    st.markdown("#### The breakthrough curve")
    st.markdown(
        "A breakthrough curve plots the outlet ratio $c/c_0$ against time. It stays "
        "near zero, then rises in an S shape when the MTZ reaches the outlet. The "
        "**breakthrough time** $t_b$ is when the outlet reaches its allowed limit, "
        "often $c/c_0$ between 0.01 and 0.05. The bed is stopped near $t_b$, then "
        "regenerated or replaced."
    )

    st.markdown("#### Key ideas")
    st.markdown(
        "- $t_t$ is the **time equivalent to total capacity**: how long the feed "
        "would take to fill the whole bed if all solute were captured.\n"
        "- $t_u$ is the **time equivalent to usable capacity**: the same idea, but "
        "only up to $t_b$.\n"
        "- $H_B$ is the **used bed length**: the part of the bed filled by $t_b$.\n"
        "- $H_{UNB}$ is the **unused bed length**: the part wasted when the bed is "
        "stopped, which is about half the MTZ."
    )
    st.latex(
        r"t_t = \int_0^\infty \left(1 - \frac{c}{c_0}\right) dt"
        r"\qquad t_u = \int_0^{t_b} \left(1 - \frac{c}{c_0}\right) dt"
    )
    st.latex(
        r"H_B = \frac{t_u}{t_t}\, H_T"
        r"\qquad H_{UNB} = \left(1 - \frac{t_u}{t_t}\right) H_T"
    )
    st.info("Full design calculation is in the Design Fixed Bed section.")

    show_pros_and_cons(
        advantages=[
            "No moving solids, so the equipment is simple",
            "Can reach very low outlet concentrations",
            "Adsorbent can often be regenerated in place",
        ],
        disadvantages=[
            "Runs in cycles, so continuous service needs two or more beds",
            "The unused part of the MTZ is lost capacity in every cycle",
            "Pressure drop, and fouling by suspended solids",
        ],
        applications=[
            "Drinking water treatment with activated carbon",
            "Solvent vapour recovery from air",
            "Drying gases with molecular sieves or alumina",
        ],
    )

    st.divider()
    fixed_bed_demo()


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

st.title("Mechanism for Adsorption")
st.write(
    "Adsorption is a separation process in which a solute moves from a fluid and "
    "attaches to the surface of a porous solid. The solute keeps transferring until "
    "equilibrium is reached, when the amount on the solid stops changing. At that "
    "point the fluid concentration and the solid loading are linked by an isotherm. "
    "How the fluid and solid are brought together decides how well the solid is used, "
    "and the tabs below compare three ways of doing this."
)

terms = st.columns(4)
terms[0].markdown("**Adsorbent**  \nThe porous solid that takes up the solute, such as activated carbon.")
terms[1].markdown("**Adsorbate**  \nThe solute removed from the fluid, such as phenol.")
terms[2].markdown("**Equilibrium loading, q**  \nSolute held per mass of adsorbent at equilibrium, in mg/g.")
terms[3].markdown("**Fluid concentration, c**  \nSolute per volume of fluid, in mg/L.")

tab_stirred, tab_countercurrent, tab_fixed = st.tabs(
    ["Stirred Tank", "Continuous Countercurrent", "Fixed Bed"]
)
with tab_stirred:
    stirred_tank_tab()
with tab_countercurrent:
    countercurrent_tab()
with tab_fixed:
    fixed_bed_tab()

st.divider()
st.subheader("Comparing the three modes")
comparison = pd.DataFrame(
    {
        "Contacting mode": ["Stirred tank", "Continuous countercurrent", "Fixed bed"],
        "Operation type": [
            "Batch",
            "Continuous",
            "Batch/cyclic (fluid flows continuously, adsorbent stays in place)",
        ],
        "Adsorbent use efficiency": [
            "Low: all solid ends in equilibrium with the final, dilute fluid",
            "High: fresh solid meets the most dilute fluid",
            "Medium to high: only the MTZ is left partly unused",
        ],
        "Equipment": [
            "Stirred tank plus filter or settler",
            "Staged contactors or a moving bed, with solids handling",
            "Packed column, usually two or more in rotation",
        ],
        "Typical use": [
            "Small volumes, powdered adsorbent, lab tests",
            "Large, steady flows that use a lot of adsorbent",
            "Water treatment, gas drying, solvent recovery",
        ],
        "Main limitation": [
            "One equilibrium stage limits the removal",
            "Moving solids is complex and wears the particles",
            "Must stop to regenerate, and runs in cycles",
        ],
    }
).set_index("Contacting mode")
st.table(comparison)
