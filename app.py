import streamlit as st
import json
import os

RECIPES_FILE = "recipes.json"

# Load recipes from JSON file
def load_recipes():
    if os.path.exists(RECIPES_FILE):
        with open(RECIPES_FILE, "r") as f:
            return json.load(f)
    return {}

# Save recipes to JSON file
def save_recipes(recipes):
    with open(RECIPES_FILE, "w") as f:
        json.dump(recipes, f, indent=2)

# Calculate base material percentage
def calculate_base(ingredients):
    return 100 - sum(ingredients.values())

# --- UI ---
st.set_page_config(page_title="Masterbatch Calculator")
st.title("🎨 Masterbatch Calculator")

tabs = st.tabs(["Kalkulator", "Dodaj recepturę"])

# --- Kalkulator ---
with tabs[0]:
    recipes = load_recipes()
    if not recipes:
        st.warning("Brak zdefiniowanych receptur. Dodaj nową w zakładce obok.")
    else:
        selected = st.selectbox("Wybierz recepturę", list(recipes.keys()))
        weight = st.number_input("Podaj wagę końcową (g)", min_value=0.0, step=10.0)

        if st.button("Oblicz ilości składników"):
            r = recipes[selected]
            ingredients = r["ingredients"]
            base = calculate_base(ingredients)
            st.subheader(f"Skład receptury: {selected}")
            st.write(f"**{r['base']}**: {round(base / 100 * weight, 2)} g")
            for k, v in ingredients.items():
                st.write(f"**{k}**: {round(v / 100 * weight, 2)} g")

# --- Dodawanie receptury ---
with tabs[1]:
    st.subheader("Nowa receptura")
    name = st.text_input("Nazwa receptury")
    base_type = st.text_input("Rodzaj bazy (np. Base PLA, PETG)", value="Base PLA")

    st.markdown("### Składniki kolorowe")
    ingredient_count = st.session_state.get("ingredient_count", 1)

    ingredients = {}
    for i in range(ingredient_count):
        col1, col2 = st.columns([2, 1])
        with col1:
            k = st.text_input(f"Nazwa składnika {i+1}", key=f"k{i}")
        with col2:
            v = st.number_input(f"% składnika {i+1}", min_value=0.0, max_value=100.0, step=0.1, key=f"v{i}")
        if k:
            ingredients[k] = v

    col_plus, col_save = st.columns([1, 2])
    if col_plus.button("+ Dodaj składnik"):
        st.session_state.ingredient_count = ingredient_count + 1

    if col_save.button("Zapisz recepturę"):
        if not name:
            st.error("Podaj nazwę receptury.")
        elif sum(ingredients.values()) > 100:
            st.error("Suma składników przekracza 100%!")
        else:
            recipes = load_recipes()
            recipes[name] = {
                "base": base_type,
                "ingredients": ingredients
            }
            save_recipes(recipes)
            st.success(f"Zapisano recepturę '{name}'!")
            st.session_state.ingredient_count = 1
            for i in range(20):
                st.session_state.pop(f"k{i}", None)
                st.session_state.pop(f"v{i}", None)
