"""Home page of the adsorption learning tool.

Run with: streamlit run app.py

Streamlit finds every file in pages/ automatically. To add a section later, put
its file in pages/ and swap its "Coming soon" card below for a st.page_link.
"""

import streamlit as st

st.set_page_config(page_title="Adsorption Learning Tool", layout="wide")

st.title("Adsorption Learning Tool")
st.write(
    "An interactive guide to adsorption for chemical engineering students. Start "
    "with how adsorption works, then move on to calculations and column design as "
    "those sections become available."
)

mechanism, batch, fixed_bed = st.columns(3)

with mechanism:
    with st.container(border=True):
        st.subheader("1. Mechanism for Adsorption")
        st.write(
            "See how stirred tank, countercurrent and fixed bed contacting work, "
            "with interactive demos for each."
        )
        st.page_link(
            "pages/1_Mechanism_for_Adsorption.py", label="Open this section", icon="➡️"
        )

with batch:
    with st.container(border=True):
        st.subheader("2. Batch Adsorption Calculation")
        st.write("Work through batch adsorption calculations step by step.")
        st.caption("Coming soon")

with fixed_bed:
    with st.container(border=True):
        st.subheader("3. Design Fixed Bed Reactor")
        st.write("Size a fixed bed column from breakthrough data.")
        st.caption("Coming soon")
