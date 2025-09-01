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

st.markdown("""
<link rel="stylesheet" href="https://use.typekit.net/eno7qox.css">
<style>
  /* Stylowanie głównych tytułów i nagłówków */
  .stApp h1, .stApp h2, .stApp h3, .stApp .stMarkdown h1 {
      font-family: "blow-up", sans-serif;
      font-weight: 400;
      font-style: normal;
  }

  /* Stylowanie tekstu w aplikacji */
  .stApp, .stApp p, .stApp label, .stApp span, .stApp input, .stApp textarea {
      font-family: "sofia-pro", sans-serif;
      font-weight: 400;
  }
  .stButton>button {
    font-family: "sofia-pro", sans-serif;
    font-weight: 700;
    text-transform: uppercase;
  }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Masterbatch Calculator")

tabs = st.tabs(["Kalkulator", "Dodaj recepturę", "Edytuj recepturę"])

# --- Zakładka 1: Kalkulator ---
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

# --- Zakładka 2: Dodaj recepturę ---
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

# --- Zakładka 3: Edytuj recepturę ---
with tabs[2]:
    st.subheader("Edytuj istniejącą recepturę")

    recipes = load_recipes()
    if not recipes:
        st.warning("Brak receptur do edycji.")
    else:
        selected_recipe = st.selectbox("Wybierz recepturę do edycji", list(recipes.keys()))
        recipe_data = recipes[selected_recipe]
        base_name = recipe_data.get("base", "Base")
        ingredients = recipe_data.get("ingredients", {})

        st.markdown("#### Składniki kolorowe")
        new_ingredients = {}
        for k, v in ingredients.items():
            col1, col2 = st.columns([2, 1])
            with col1:
                new_k = st.text_input(f"Nazwa dla '{k}'", value=k, key=f"edit_k_{k}")
            with col2:
                new_v = st.number_input(f"% dla '{k}'", min_value=0.0, max_value=100.0, value=v, step=0.1, key=f"edit_v_{k}")
            new_ingredients[new_k] = new_v

        new_base_name = st.text_input("Nazwa bazy", value=base_name, key="edit_base")
        base_pct = calculate_base(new_ingredients)

        st.markdown(f"**Baza `{new_base_name}` zajmie: {base_pct:.2f}%**")

        if base_pct < 0:
            st.error("Suma składników przekracza 100%!")
        else:
            if st.button("💾 Zapisz zmiany w recepturze"):
                recipes[selected_recipe] = {
                    "base": new_base_name,
                    "ingredients": new_ingredients
                }
                save_recipes(recipes)
                st.success("Zapisano zmiany!")

        st.markdown("---")
        st.markdown("### 🗑️ Usuń recepturę")
        confirm_1 = st.checkbox("Potwierdzam chęć usunięcia receptury")
        confirm_2 = st.checkbox("Na pewno?")

        if confirm_1 and confirm_2:
            if st.button("❌ Usuń recepturę"):
                recipes.pop(selected_recipe, None)
                save_recipes(recipes)
                st.success("Receptura została usunięta.")
