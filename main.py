import pandas as pd
import streamlit as st
from libs import Shoes, Store

if "store" not in st.session_state:
    st.session_state.store = Store(1, "My Shoes Store", "Rengasdengklok Street No. 45")

if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

if "redirect_to_dashboard" not in st.session_state:
    st.session_state.redirect_to_dashboard = False


def load_shoes_to_store():
    try:
        shoes_df = pd.read_csv("shoes_data.csv")

        st.session_state.store.bunch_of_shoes = []

        for _, row in shoes_df.iterrows():
            shoe = Shoes(
                shoes_id=row["shoes_id"],
                brand=row["brand"],
                model=row["model"],
                category=row["category"],
                color=row["color"],
                size_eu=row["size_eu"],
                price_idr=row["price_idr"],
            )
            st.session_state.store.add_shoes_as_stock(shoe)
    except FileNotFoundError:
        pass


if "shoes_loaded" not in st.session_state:
    load_shoes_to_store()
    st.session_state.shoes_loaded = True


csv_file_path = "shoes_data.csv"
try:
    csv = pd.read_csv(csv_file_path)
except FileNotFoundError:
    # Create a new CSV with headers if the file doesn't exist
    csv = pd.DataFrame(
        columns=[
            "shoes_id",
            "brand",
            "model",
            "category",
            "color",
            "size_eu",
            "price_idr",
        ]
    )
    csv.to_csv(csv_file_path, index=False)

# Check if we should redirect to dashboard
if st.session_state.redirect_to_dashboard:
    st.session_state.redirect_to_dashboard = False
    page = "Dashboard"
else:
    page = st.sidebar.selectbox("Select Page", ["Dashboard", "Create Shoes"])

# Check if we should show balloons
if st.session_state.show_balloons:
    st.balloons()
    st.session_state.show_balloons = False


if page == "Create Shoes":
    st.title("Expand Your Collection")
    st.write("### Fill in the details to add new shoes to your inventory")

    with st.form(key="shoes_form"):
        shoes_id = st.text_input("Shoes ID")
        brand = st.text_input("Brand")
        model = st.text_input("Model")
        category = st.selectbox(
            "Category",
            [
                "Running",
                "Lifestyle",
                "Casual",
                "Skateboarding",
                "Basketball",
                "Boots",
                "Sandals",
                "Football",
            ],
        )
        color = st.text_input("Color")
        size = st.select_slider("Size EU", options=list(range(35, 50)))
        price = st.number_input("Price IDR", step=10000)
        submit_button = st.form_submit_button("Add Shoes to the stats")

    if submit_button:
        if not (shoes_id and brand and model and color and price):
            st.warning("Please fill in all required fields 😉")
        else:
            # Add to CSV
            new_data = pd.DataFrame(
                [[shoes_id, brand, model, category, color, size, price]],
                columns=[
                    "shoes_id",
                    "brand",
                    "model",
                    "category",
                    "color",
                    "size_eu",
                    "price_idr",
                ],
            )
            csv = pd.concat([csv, new_data], ignore_index=True)
            csv.to_csv(csv_file_path, index=False)

            # Add to store object
            new_shoes = Shoes(shoes_id, brand, model, category, color, size, price)
            st.session_state.store.add_shoes_as_stock(new_shoes)

            st.session_state.show_balloons = True
            st.session_state.redirect_to_dashboard = True
            st.rerun()


if page == "Dashboard":
    st.title("Shoes Dashboard")

    # Display store information
    st.write("### Store Information")
    st.write(f"Store Name: {st.session_state.store.store_name}")
    st.write(f"Store Address: {st.session_state.store.store_address}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Filter section
    st.write("### Filter Shoes")
    col1, col2 = st.columns(2)

    with col1:
        show_football_shoes = st.toggle("Show shoes suitable for football")

    with col2:
        show_running_shoes = st.toggle("Show shoes suitable for running")

    # Apply filters if selected
    filtered_df = csv.copy()

    if show_football_shoes and not show_running_shoes:
        # Only football shoes
        football_shoes = [
            shoe
            for shoe in st.session_state.store.bunch_of_shoes
            if shoe.category == "Football"
        ]
        football_shoe_ids = [shoe.shoes_id for shoe in football_shoes]
        filtered_df = csv[
            csv["shoes_id"].astype(str).isin([str(id) for id in football_shoe_ids])
        ]
        st.write("🥅 Showing shoes suitable for playing football")

    elif show_running_shoes and not show_football_shoes:
        # Only running shoes
        running_categories = ["Running", "Basketball", "Football"]
        running_shoes = [
            shoe
            for shoe in st.session_state.store.bunch_of_shoes
            if shoe.category in running_categories
        ]
        running_shoe_ids = [shoe.shoes_id for shoe in running_shoes]
        filtered_df = csv[
            csv["shoes_id"].astype(str).isin([str(id) for id in running_shoe_ids])
        ]
        st.write("🏃‍♂️ Showing shoes suitable for running")

    elif show_football_shoes and show_running_shoes:
        # Both filters
        football_shoes = [
            shoe
            for shoe in st.session_state.store.bunch_of_shoes
            if shoe.category == "Football"
        ]
        running_categories = ["Running", "Basketball", "Football"]
        running_shoes = [
            shoe
            for shoe in st.session_state.store.bunch_of_shoes
            if shoe.category in running_categories
        ]
        # Combine the IDs
        all_shoe_ids = set(
            [shoe.shoes_id for shoe in football_shoes]
            + [shoe.shoes_id for shoe in running_shoes]
        )
        filtered_df = csv[
            csv["shoes_id"].astype(str).isin([str(id) for id in all_shoe_ids])
        ]
        st.write("⚽🏃‍♂️ Showing shoes suitable for playing football and running")

    # Display the filtered data
    st.write("### Shoes Data Table")
    st.dataframe(filtered_df)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    if not filtered_df.empty:
        # Bar Chart
        st.write("### Mean Shoes Price Chart by Brand")
        filtered_df["price_idr"] = pd.to_numeric(
            filtered_df["price_idr"], errors="coerce"
        )
        st.bar_chart(filtered_df.groupby("brand")["price_idr"].mean())
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Area Chart
        st.write("### Shoes Count by Category")
        category_counts = filtered_df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]
        st.area_chart(category_counts.set_index("category"), color="#bff3ca")
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Line Chart
        st.write("### Price Trends by Size")
        csv_numeric = filtered_df.copy()
        csv_numeric["price_idr"] = pd.to_numeric(
            csv_numeric["price_idr"], errors="coerce"
        )
        csv_numeric["size_eu"] = pd.to_numeric(csv_numeric["size_eu"], errors="coerce")

        size_price_df = csv_numeric.groupby("size_eu")["price_idr"].mean().reset_index()
        size_price_df = size_price_df.sort_values("size_eu")

        st.line_chart(size_price_df.set_index("size_eu"), color="#d946ef")
    else:
        st.info("No shoes match your filter criteria.")

    # Show all shoes again button
    if show_football_shoes or show_running_shoes:
        if st.button("Show All Shoes"):
            st.rerun()
