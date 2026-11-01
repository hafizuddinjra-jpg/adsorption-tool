# Adsorption Learning Tool

An interactive Streamlit tool for learning adsorption, for chemical engineering
students. It runs locally in a web browser, with no login or database.

| Section | Status |
|---|---|
| 1. Mechanism for Adsorption | Available |
| 2. Batch Adsorption Calculation | Coming soon |
| 3. Design Fixed Bed Reactor | Coming soon |

## Install and run on Windows

Open PowerShell in the `adsorption_tool` folder, then run:

```powershell
python -m venv "$env:USERPROFILE\.venvs\adsorption"
& "$env:USERPROFILE\.venvs\adsorption\Scripts\python.exe" -m pip install -r requirements.txt
& "$env:USERPROFILE\.venvs\adsorption\Scripts\python.exe" -m streamlit run app.py
```

The first two lines are only needed once. To open the tool again, run the last
line. The tool opens in your browser. To stop it, press `Ctrl+C` in PowerShell.

Keep the virtual environment in this short path, outside OneDrive. Streamlit
contains deeply nested files, so a long path can fail with an `OSError: [Errno 2]
No such file or directory` during install. OneDrive would also try to sync
thousands of package files.

## Project layout

```text
adsorption_tool/
├── app.py                            Home page
├── pages/
│   └── 1_Mechanism_for_Adsorption.py Mechanism section
├── modules/
│   ├── isotherms.py                  Isotherms and batch balance (reusable)
│   └── mechanism_plots.py            Plotly figures for the Mechanism page
├── requirements.txt
└── README.md
```

## Adding a section later

1. Add a file to `pages/`, such as `2_Batch_Adsorption_Calculation.py`.
2. In `app.py`, replace that section's "Coming soon" caption with a `st.page_link`.
3. Import from `modules/isotherms.py` to reuse the isotherms and the batch solver.

## Illustrative content

The countercurrent demo assumes ideal stages and a linear isotherm. The fixed bed
demo uses a logistic function. Both are for teaching and are labelled illustrative
in the tool, so neither should be used for design.
