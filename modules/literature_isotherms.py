"""Published isotherm constants for methylene blue on activated carbon.

Source, licensed CC BY 4.0:
    Lawtae, P.; Tangsathitkulchai, C. The Use of High Surface Area Mesoporous-
    Activated Carbon from Longan Seed Biomass for Increasing Capacity and Kinetics
    of Methylene Blue Adsorption from Aqueous Solution. Molecules 2021, 26(21),
    6521. https://doi.org/10.3390/molecules26216521

Constants are copied from Table 7 of the paper (fitted at 35 °C by non-linear
regression) and surface areas from Table 2. Units follow the app: c in mg/L and
q in mg/g. This file has no Streamlit code, so other sections can reuse it.
"""

from modules.isotherms import freundlich, langmuir, redlich_peterson

CITATION = (
    "Lawtae, P., & Tangsathitkulchai, C. (2021). The use of high surface area "
    "mesoporous-activated carbon from longan seed biomass for increasing capacity "
    "and kinetics of methylene blue adsorption from aqueous solution. Molecules, "
    "26(21), 6521."
)
DOI_URL = "https://doi.org/10.3390/molecules26216521"
LICENCE = "CC BY 4.0"

# Batch equilibrium tests (Table 1 and Section 2.4 of the paper).
CONDITIONS = {
    "volume_mL": 25,
    "initial_conc_mg_L": "50–500",
    "carbon_g": "0.010–0.020",
    "temperature_C": 35,
    "pH": 4.5,
    "contact_time_h": 48,
}

# The carbon dose was chosen so equilibrium concentrations reached up to 300 mg/L,
# so the curves are only drawn over the range the data covered.
C_MAX = 300.0  # mg/L

MODELS = ("Langmuir", "Freundlich", "Redlich–Peterson")

# One entry per carbon. "best" is the model the authors name as the best fit.
CARBONS = {
    "A1": {
        "sample": "A850–120", "pores": "Microporous",
        "made_by": "two-step CO₂ activation at 850 °C for 120 min", "bet_m2_g": 932,
        "langmuir": {"q_m": 459.35, "K_L": 0.056, "R2": 0.984, "dq": 24.39},
        "freundlich": {"n_F": 3.67, "K_F": 102.6, "R2": 0.992, "dq": 8.04},
        "redlich_peterson": {"K_R": 56.0, "beta": 0.81, "A_R": 0.34, "R2": 0.999, "dq": 5.87},
        "best": "Redlich–Peterson",
    },
    "A2": {
        "sample": "A850–180", "pores": "Microporous",
        "made_by": "two-step CO₂ activation at 850 °C for 180 min", "bet_m2_g": 926,
        "langmuir": {"q_m": 497.12, "K_L": 0.090, "R2": 0.995, "dq": 5.45},
        "freundlich": {"n_F": 4.61, "K_F": 152.2, "R2": 0.957, "dq": 12.46},
        "redlich_peterson": {"K_R": 90.2, "beta": 0.86, "A_R": 0.38, "R2": 0.998, "dq": 4.29},
        "best": "Redlich–Peterson",
    },
    "A3": {
        "sample": "A850–240", "pores": "Microporous",
        "made_by": "two-step CO₂ activation at 850 °C for 240 min", "bet_m2_g": 1140,
        "langmuir": {"q_m": 648.12, "K_L": 0.125, "R2": 0.989, "dq": 12.60},
        "freundlich": {"n_F": 5.31, "K_F": 244.2, "R2": 0.980, "dq": 11.75},
        "redlich_peterson": {"K_R": 125.0, "beta": 0.93, "A_R": 0.28, "R2": 0.992, "dq": 5.74},
        "best": "Redlich–Peterson",
    },
    "A4": {
        "sample": "A850–60–1", "pores": "Mesoporous",
        "made_by": "one OTA cycle (oxidation, thermal destruction and activation)", "bet_m2_g": 980,
        "langmuir": {"q_m": 488.29, "K_L": 0.076, "R2": 0.987, "dq": 22.80},
        "freundlich": {"n_F": 4.13, "K_F": 132.1, "R2": 0.996, "dq": 4.69},
        "redlich_peterson": {"K_R": 76.3, "beta": 0.86, "A_R": 0.32, "R2": 0.970, "dq": 7.54},
        "best": "Freundlich",
    },
    "A5": {
        "sample": "A850–60–2", "pores": "Mesoporous",
        "made_by": "two OTA cycles (oxidation, thermal destruction and activation)", "bet_m2_g": 1271,
        "langmuir": {"q_m": 714.29, "K_L": 0.154, "R2": 0.986, "dq": 15.42},
        "freundlich": {"n_F": 4.38, "K_F": 224.2, "R2": 0.996, "dq": 4.88},
        "redlich_peterson": {"K_R": 153.8, "beta": 0.85, "A_R": 0.45, "R2": 0.989, "dq": 9.40},
        "best": "Freundlich",
    },
    "A6": {
        "sample": "A850–60–3", "pores": "Mesoporous",
        "made_by": "three OTA cycles (oxidation, thermal destruction and activation)", "bet_m2_g": 1773,
        "langmuir": {"q_m": 1000.00, "K_L": 0.214, "R2": 0.986, "dq": 18.47},
        "freundlich": {"n_F": 4.38, "K_F": 328.9, "R2": 0.991, "dq": 6.82},
        "redlich_peterson": {"K_R": 214.0, "beta": 0.88, "A_R": 0.37, "R2": 0.981, "dq": 12.39},
        "best": "Freundlich",
    },
}


def model_loading(carbon, model, c):
    """Loading q in mg/g predicted by one fitted model for one carbon.

    Args:
        carbon: Carbon code, "A1" to "A6".
        model: "Langmuir", "Freundlich" or "Redlich–Peterson".
        c: Equilibrium concentration in mg/L. A single number or a NumPy array.
    """
    data = CARBONS[carbon]
    if model == "Langmuir":
        # Paper form q = q_m K_L c / (1 + K_L c) is the lecture form with K = 1/K_L.
        p = data["langmuir"]
        return langmuir(c, p["q_m"], 1.0 / p["K_L"])
    if model == "Freundlich":
        # Paper form q = K_F c^(1/n_F) is the lecture form with n = 1/n_F.
        p = data["freundlich"]
        return freundlich(c, p["K_F"], 1.0 / p["n_F"])
    if model == "Redlich–Peterson":
        p = data["redlich_peterson"]
        return redlich_peterson(c, p["K_R"], p["A_R"], p["beta"])
    raise ValueError(f"Unknown model: {model}")
