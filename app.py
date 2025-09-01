import streamlit as st
import json
import os

RECIPE_FILE = "recipes.json"

# Ensure the recipe file exists
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

# UI Starts Here
init_recipe_file()
recipes = load_recipes()

st.title("🎨 Masterbatch Calculator")
tabs = st.tabs(["📘 Oblicz recepturę", "➕ Dodaj recepturę", "✏️ Edytuj recepturę"])

# TAB 1 – Calculate
with tabs[0]:
    st.header("📘 Oblicz recepturę")
    recipe_name = st.selectbox("Wybierz recepturę", list(recipes.keys()))
    weight = st.number_input("Podaj wagę końcową (g)", min_value=0.0, value=1000.0)

    if recipe_name:
        st.subheader("📋 Wynik")
        for colorant, percent in recipes[recipe_name].items():
            grams = (percent / 100) * weight
            st.write(f"{colorant}: {grams:.2f} g ({percent:.2f}%)")

# TAB 2 – Add new recipe
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
            st.error("Suma składników przekracza 100%! Zmniejsz wartości.")
        else:
            new_ingredients["Base PLA"] = base_pct
            if st.button("💾 Zapisz recepturę"):
                recipes[new_recipe_name] = new_ingredients
                save_recipes(recipes)
                st.success("Dodano nową recepturę!")

# TAB 3 – Edit recipe
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
            st.error("Suma składników przekracza 100%")
        else:
            if st.button("💾 Zapisz zmiany"):
                recipes[selected] = edited
                save_recipes(recipes)
                st.success("Zapisano zmiany w recepturze!")

        st.markdown("---")
        st.subheader("🗑️ Usuń recepturę")
        confirm_1 = st.checkbox("Potwierdzam chęć usunięcia receptury")
        confirm_2 = st.checkbox("Na pewno?")

        if confirm_1 and confirm_2:
            if st.button("❌ Usuń recepturę"):
                recipes.pop(selected, None)
                save_recipes(recipes)
                st.success("Receptura została usunięta")
