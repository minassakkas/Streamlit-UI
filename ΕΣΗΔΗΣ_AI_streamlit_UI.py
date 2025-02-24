import streamlit as st

# Set the title of the app
st.title("My Simple Streamlit App")

# Text input
name = st.text_input("Enter your name:")

# Slider for demonstration
age = st.slider("Select your age:", 1, 100, 25)

# Button
if st.button("Submit"):
    st.write(f"Hello, {name}!")
    st.write(f"You are {age} years old.")
