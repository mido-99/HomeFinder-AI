import streamlit as st

st.title("🧪 Welcome to Streamlit Lab!")

def lbs_to_kg():
    st.session_state.kg = st.session_state.lbs / 2.2046
def kg_to_lbs():
    st.session_state.lbs = st.session_state.kg * 2.2046


col1, buff, col2 = st.columns([2,1,2])

with col1:
    pounds = st.number_input( "Pounds:" , key='lbs', step=1, on_change=lbs_to_kg)
with col2:
    kilogram = st.number_input("Ki10grams:", key='kg', step=1, on_change=kg_to_lbs)
