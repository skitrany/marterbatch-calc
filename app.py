import streamlit as st
import json
import pandas as pd

# --- Tytuł ---
st.set_page_config(page_title="Masterbatch Calculator", layout="centered")
st.title("🎛️ Masterbatch Kalkulator")

# --- Wczytaj receptury ---
with open("recipes.json") as f:
    recipes = json.load(f)

recipe_names = list(recipes.keys())

# --- Wybór receptury ---
selected_recipe = st.selectbox("Wybierz recepturę:", recipe_names)

# --- Waga finalna ---
final_weight = st.number_input("Podaj docelową wagę mieszanki [g]:", min_value=1.0, value=1000.0, step=10.0)

# --- Obliczenia ---
if selected_recipe and final_weight > 0:
    composition = recipes[selected_recipe]
    total_percent = sum(composition.values())

    if abs(total_percent - 100.0) > 0.1:
        st.warning("⚠️ Udział procentowy składników nie sumuje się do 100%. Sprawdź recepturę.")
    
    st.subheader("📦 Skład receptury:")
    df = pd.DataFrame([
        {
            "Składnik": name,
            "Udział [%]": percent,
            "Waga [g]": round(final_weight * percent / 100.0, 2)
        }
        for name, percent in composition.items()
    ])

    st.dataframe(df, use_container_width=True)

    # --- Pobieranie pliku ---
    csv = df.to_csv(index=False)
    st.download_button("📥 Pobierz jako CSV", csv, file_name=f"{selected_recipe}.csv")
