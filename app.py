import streamlit as st
import json
import os
import pandas as pd

RECIPE_FILE = "recipes.json"

# --- Plik receptur ---
def init_recipe_file():
    if not os.path.exists(RECIPE_FILE):
        with open(RECIPE_FILE, "w") as f:
            json.dump({}, f)

def load_recipes():
    with open(RECIPE_FILE, "r") as f:
        return json.load(f)

def save_recipes(recipes):
    with open(RECIPE_FILE, "w") as f:
        json.dump(recipes, f, indent=2)

# --- Inicjalizacja ---
init_recipe_file()
recipes = load_recipes()

# --- Walidacja danych JSON ---
for rname, composition in recipes.items():
    for k, v in composition.items():
        if not isinstance(v, (int, float)):
            st.warning(f"⚠️ W recepturze '{rname}', składnik '{k}' ma nieprawidłową wartość: {v}")

# --- UI ---
st.title("🎨 Masterbatch Calculator")
tabs = st.tabs(["📘 Oblicz recepturę", "➕ Dodaj recepturę", "✏️ Edytuj recepturę"])

# --- TAB 1: Oblicz recepturę ---
with tabs[0]:
    st.header("📘 Oblicz recepturę")
    recipe_name = st.selectbox("Wybierz recepturę", list(recipes.keys()))
    weight = st.number_input("Podaj wagę końcową (g)", min_value=0.0, value=1000.0)

    if recipe_name:
    st.subheader("📋 Wynik")
    composition = recipes[recipe_name]

    try:
        total_percent = sum(float(v) for v in composition.values())
        if abs(total_percent - 100.0) > 0.1:
            st.warning("⚠️ Udział procentowy składników nie sumuje się do 100%. Sprawdź recepturę.")

        df = pd.DataFrame([
            {
                "Składnik": colorant,
                "Udział [%]": float(percent),
                "Waga [g]": round((float(percent) / 100.0) * weight, 2)
            }
            for colorant, percent in composition.items()
        ])
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Błąd podczas przeliczania receptury: {e}")

# --- TAB 2: Dodaj nową recepturę ---
with tabs[1]:
    st.header("➕ Dodaj recepturę")
    new_recipe_name = st.text_input("Nazwa nowej receptury")
    new_ingredients = {}

    num_colors = st.number_input("Ile składników chcesz dodać?", min_value=1, step=1, value=2)

    for i in range(int(num_colors)):
        col_name = st.text_input(f"Nazwa składnika {i+1}", key=f"add_name_{i}")
        col_percent = st.number_input(f"Procent składnika {i+1}", min_value=0.0, max_value=100.0, step=0.1, key=f"add_val_{i}")
        if col_name:
            new_ingredients[col_name] = col_percent

    if new_ingredients:
        total_pct = sum(new_ingredients.values())
        base_pct = 100.0 - total_pct
        if base_pct < 0:
            st.error("❌ Suma składników przekracza 100%! Zmniejsz wartości.")
        else:
            new_ingredients["Base PLA"] = base_pct
            if st.button("💾 Zapisz recepturę"):
                recipes[new_recipe_name] = new_ingredients
                save_recipes(recipes)
                st.success(f"✅ Dodano nową recepturę: {new_recipe_name}")

# --- TAB 3: Edytuj recepturę ---
with tabs[2]:
    st.header("✏️ Edytuj recepturę")
    selected = st.selectbox("Wybierz recepturę do edycji", list(recipes.keys()), key="edit_recipe")

    if selected:
        edited = {}
        st.subheader(f"Edytuj składniki: {selected}")
        for ing, val in recipes[selected].items():
            if ing != "Base PLA":
                new_val = st.number_input(f"{ing}", min_value=0.0, max_value=100.0, value=val, key=f"edit_{ing}")
                edited[ing] = new_val

        total = sum(edited.values())
        base_val = 100.0 - total
        edited["Base PLA"] = base_val

        if total > 100:
            st.error("❌ Suma składników przekracza 100%.")
        else:
            if st.button("💾 Zapisz zmiany"):
                recipes[selected] = edited
                save_recipes(recipes)
                st.success(f"✅ Zapisano zmiany w: {selected}")

        st.markdown("---")
        st.subheader("🗑️ Usuń recepturę")
        confirm_1 = st.checkbox("Potwierdzam chęć usunięcia receptury")
        confirm_2 = st.checkbox("Na pewno?")

        if confirm_1 and confirm_2:
            if st.button("❌ Usuń recepturę"):
                recipes.pop(selected, None)
                save_recipes(recipes)
                st.success("🗑️ Receptura została usunięta.")
