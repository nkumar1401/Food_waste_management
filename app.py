import streamlit as st
import pandas as pd
from decouple import config
import MySQLdb
from MySQLdb.cursors import DictCursor

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection():
    try:
        conn = MySQLdb.connect(
            host=config('db_host'),
            user=config('db_user'),
            passwd=config('db_password'),
            port=int(config('db_port')),
            database='food_wastage_management_system',
            cursorclass=DictCursor
        )
        conn.autocommit(True)
        return conn
    except MySQLdb.Error as err:
        st.error(f"Database Connection Error: {err}")
        return None


# -----------------------------
# PAGE CONFIG & STYLES
# -----------------------------
st.set_page_config(
    page_title="Local Food Wastage Management System",
    layout="wide",
    page_icon="🍲"
)

# Inject custom CSS for modern look
st.markdown("""
    <style>
        /* Global background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(120deg, #f8f9fa 0%, #e3f2fd 100%);
        }
        [data-testid="stSidebar"] {
            background-color: #0d47a1;
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        .main-title {
            font-size: 40px;
            color: #0d47a1;
            font-weight: 700;
            text-align: center;
            padding: 10px;
        }
        .section-header {
            font-size: 22px;
            color: #1565c0;
            font-weight: 600;
            margin-top: 25px;
        }
        .metric-card {
            background-color: #ffffffcc;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .stDataFrame {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🍲 Local Food Wastage Management System</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Connecting surplus food providers with receivers using Streamlit + MySQL</p>", unsafe_allow_html=True)

menu =  ["Dashboard", "CRUD Operations", "SQL Analysis", "Query Explorer", "About"]

choice = st.sidebar.selectbox("📂 Navigation", menu)

conn = get_connection()
if conn:
    cursor = conn.cursor()

    # -------- DASHBOARD --------
    if choice == "Dashboard":
        st.markdown('<div class="section-header">📊 Food Distribution Insights</div>', unsafe_allow_html=True)

        # --- FILTERS SECTION ---
        with st.expander("🔍 Filter Options", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            try:
                cursor.execute("SELECT DISTINCT Location FROM food_listings;")
                cities = [row['Location'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT Provider_ID FROM food_listings;")
                providers = [str(row['Provider_ID']) for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT Food_Type FROM food_listings;")
                food_types = [row['Food_Type'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT Meal_Type FROM food_listings;")
                meal_types = [row['Meal_Type'] for row in cursor.fetchall()]
            except MySQLdb.Error:
                cities, providers, food_types, meal_types = [], [], [], []

            selected_city = col1.selectbox("City", ["All"] + cities)
            selected_provider = col2.selectbox("Provider ID", ["All"] + providers)
            selected_food_type = col3.selectbox("Food Type", ["All"] + food_types)
            selected_meal_type = col4.selectbox("Meal Type", ["All"] + meal_types)

        # --- FILTERED FOOD LISTINGS ---
        query = "SELECT * FROM food_listings WHERE 1=1"
        params = []

        if selected_city != "All":
            query += " AND Location = %s"
            params.append(selected_city)
        if selected_provider != "All":
            query += " AND Provider_ID = %s"
            params.append(selected_provider)
        if selected_food_type != "All":
            query += " AND Food_Type = %s"
            params.append(selected_food_type)
        if selected_meal_type != "All":
            query += " AND Meal_Type = %s"
            params.append(selected_meal_type)

        cursor.execute(query, params)
        food_data = pd.DataFrame(cursor.fetchall())

        st.markdown('<div class="section-header">🍱 Filtered Food Listings</div>', unsafe_allow_html=True)
        if not food_data.empty:
            st.dataframe(food_data, use_container_width=True)
        else:
            st.warning("No records found for the selected filters.")

        # --- PROVIDER CONTACT DETAILS ---
        st.markdown('<div class="section-header">📞 Provider Contact Details</div>', unsafe_allow_html=True)
        try:
            provider_query = """
                SELECT p.Provider_ID, p.Name AS Provider_Name, p.Type, p.City, p.Contact
                FROM providers p
                WHERE p.Provider_ID IN (
                    SELECT DISTINCT Provider_ID FROM food_listings
                )
                ORDER BY p.City;
            """
            cursor.execute(provider_query)
            provider_data = pd.DataFrame(cursor.fetchall())
            if not provider_data.empty:
                st.dataframe(provider_data, use_container_width=True)
            else:
                st.info("No provider contact data found.")
        except MySQLdb.Error as e:
            st.error(f"Error fetching provider contacts: {e}")

        # --- QUICK METRICS ---
        st.markdown('<div class="section-header">📈 Quick Statistics</div>', unsafe_allow_html=True)
        colm1, colm2, colm3 = st.columns(3)
        cursor.execute("SELECT COUNT(*) AS total FROM providers;")
        providers_count = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM receivers;")
        receivers_count = cursor.fetchone()['total']
        cursor.execute("SELECT SUM(Quantity) AS qty FROM food_listings;")
        total_food = cursor.fetchone()['qty']

        colm1.metric("Total Providers", providers_count)
        colm2.metric("Total Receivers", receivers_count)
        colm3.metric("Total Food Quantity", total_food if total_food else 0)

        # --- ADVANCED INSIGHTS ---
        st.markdown('<div class="section-header">📊 Analytical Reports</div>', unsafe_allow_html=True)
        insights = {
            "Providers per City": "SELECT City, COUNT(*) AS Providers FROM providers GROUP BY City;",
            "Top Provider Types": "SELECT Type, COUNT(*) AS Total FROM providers GROUP BY Type ORDER BY Total DESC;",
            "Claims by Status": "SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status;"
        }

        for name, q in insights.items():
            st.write(f"#### {name}")
            cursor.execute(q)
            df = pd.DataFrame(cursor.fetchall())
            st.dataframe(df, use_container_width=True)
            if len(df.columns) == 2:
                st.bar_chart(df.set_index(df.columns[0]))

    # -------- CRUD OPERATIONS --------
    elif choice == "CRUD Operations":
        st.markdown('<div class="section-header">🛠 Manage Food Listings</div>', unsafe_allow_html=True)
        action = st.selectbox("Select Action", ["Add", "View", "Update", "Delete"])

        if action == "Add":
            with st.form("add_form"):
                food_name = st.text_input("Food Name")
                qty = st.number_input("Quantity", min_value=1)
                expiry = st.date_input("Expiry Date")
                provider_id = st.number_input("Provider ID", min_value=1)
                location = st.text_input("Location")
                food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                submitted = st.form_submit_button("Add Record")
                if submitted:
                    cursor.execute("""
                        INSERT INTO food_listings 
                        (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (food_name, qty, expiry, provider_id, location, food_type, meal_type))
                    conn.commit()
                    st.success("✅ Record added successfully!")

        elif action == "View":
            cursor.execute("SELECT * FROM food_listings LIMIT 20;")
            st.dataframe(pd.DataFrame(cursor.fetchall()), use_container_width=True)

        elif action == "Update":
            food_id = st.number_input("Food ID to Update", min_value=1)
            new_qty = st.number_input("New Quantity", min_value=1)
            if st.button("Update Quantity"):
                cursor.execute("UPDATE food_listings SET Quantity=%s WHERE Food_ID=%s;", (new_qty, food_id))
                if cursor.rowcount == 0:
                    st.warning("⚠️ No record found with that Food_ID.")
                else:
                    conn.commit()
                    st.success("✅ Quantity updated successfully!")

        elif action == "Delete":
            food_id = st.number_input("Food ID to Delete", min_value=1)
            if st.button("Delete Record"):
                cursor.execute("DELETE FROM food_listings WHERE Food_ID=%s;", (food_id,))
                conn.commit()
                st.warning("🗑️ Record deleted successfully.")

    # -------- SQL ANALYSIS (15 Queries) --------
    elif choice == "SQL Analysis":
        st.markdown('<div class="section-header">🧮 SQL Analysis — 15 Key Insights</div>', unsafe_allow_html=True)
        st.write("Below are the results of the 15 SQL queries defined in the project requirements:")

        sql_queries = {
            # 1. Providers per City
            "1️⃣ Providers per City": """
                SELECT City, COUNT(*) AS Total_Providers 
                FROM providers 
                GROUP BY City;
            """,

            # 2. Receivers per City
            "2️⃣ Receivers per City": """
                SELECT City, COUNT(*) AS Total_Receivers 
                FROM receivers 
                GROUP BY City;
            """,

            # 3. Top Provider Types
            "3️⃣ Top Provider Types": """
                SELECT Type, COUNT(*) AS Total 
                FROM providers 
                GROUP BY Type 
                ORDER BY Total DESC;
            """,

            # 4. Contact Info of Providers by City
            "4️⃣ Provider Contact Info (Sample City: Delhi)": """
                SELECT Name, Contact, City 
                FROM providers 
                WHERE City = 'Delhi';
            """,

            # 5. Top Receivers by Food Claims
            "5️⃣ Top Receivers by Food Claims": """
                SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
                FROM receivers r
                JOIN claims c ON r.Receiver_ID = c.Receiver_ID
                GROUP BY r.Name
                ORDER BY Total_Claims DESC;
            """,

            # 6. Total Food Quantity Available
            "6️⃣ Total Food Quantity Available": """
                SELECT SUM(Quantity) AS Total_Quantity 
                FROM food_listings;
            """,

            # 7. Cities with Highest Food Listings
            "7️⃣ Cities with Highest Food Listings": """
                SELECT Location AS City, COUNT(*) AS Listings
                FROM food_listings
                GROUP BY Location
                ORDER BY Listings DESC;
            """,

            # 8. Most Common Food Types
            "8️⃣ Most Common Food Types": """
                SELECT Food_Type, COUNT(*) AS Count 
                FROM food_listings 
                GROUP BY Food_Type 
                ORDER BY Count DESC;
            """,

            # 9. Total Claims per Food Item
            "9️⃣ Total Claims per Food Item": """
                SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
                FROM food_listings f
                LEFT JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Food_Name;
            """,

            # 10. Top Providers with Most Successful Claims
            "🔟 Top Providers with Most Successful Claims": """
                SELECT p.Name AS Provider, COUNT(c.Claim_ID) AS Successful_Claims
                FROM providers p
                JOIN food_listings f ON p.Provider_ID = f.Provider_ID
                JOIN claims c ON f.Food_ID = c.Food_ID
                WHERE c.Status = 'Completed'
                GROUP BY p.Name
                ORDER BY Successful_Claims DESC;
            """,

            # 11. Claim Status Percentage
            "1️⃣1️⃣ Claim Status Percentage": """
                SELECT Status, 
                       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
                FROM claims 
                GROUP BY Status;
            """,

            # 12. Average Quantity Claimed per Receiver
            "1️⃣2️⃣ Average Quantity Claimed per Receiver": """
                SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
                FROM receivers r
                JOIN claims c ON r.Receiver_ID = c.Receiver_ID
                JOIN food_listings f ON c.Food_ID = f.Food_ID
                GROUP BY r.Name;
            """,

            # 13. Most Claimed Meal Type
            "1️⃣3️⃣ Most Claimed Meal Type": """
                SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
                FROM food_listings f
                JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Meal_Type
                ORDER BY Total_Claims DESC;
            """,

            # 14. Total Food Donated by Provider
            "1️⃣4️⃣ Total Food Donated by Provider": """
                SELECT p.Name, SUM(f.Quantity) AS Total_Donated
                FROM providers p
                JOIN food_listings f ON p.Provider_ID = f.Provider_ID
                GROUP BY p.Name;
            """,

            # 15. Food Wastage Trend by Expiry
            "1️⃣5️⃣ Food Wastage Trend (Expired Items)": """
                SELECT COUNT(*) AS Expired_Foods
                FROM food_listings
                WHERE Expiry_Date < CURDATE();
            """
        }

        for title, q in sql_queries.items():
            st.markdown(f"#### {title}")
            try:
                cursor.execute(q)
                result = pd.DataFrame(cursor.fetchall())
                if not result.empty:
                    st.dataframe(result, use_container_width=True)
                    # show chart if suitable
                    if len(result.columns) == 2:
                        st.bar_chart(result.set_index(result.columns[0]))
                else:
                    st.info("No data returned for this query.")
            except MySQLdb.Error as e:
                st.error(f"Error executing {title}: {e}")
            st.markdown("---")





    # -------- QUERY EXPLORER --------
    elif choice == "Query Explorer":
        st.markdown('<div class="section-header">🔍 Explore SQL Queries</div>', unsafe_allow_html=True)
        query = st.text_area("Enter SQL Query")
        if st.button("Run Query"):
            try:
                cursor.execute(query)
                st.dataframe(pd.DataFrame(cursor.fetchall()), use_container_width=True)
            except MySQLdb.Error as e:
                st.error(f"SQL Error: {e}")

    elif choice == "About":
        st.info("""
        **Developed by:** Nirmal Kumar Bhagatkar  
        **Technology Stack:** Streamlit, Python, MySQL  
        **Objective:** Connecting surplus food providers with receivers and NGOs to reduce food wastage.  
        """)

    cursor.close()
    conn.close()
else:
    st.error("❌ Database connection failed.")
