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
        return conn
    except MySQLdb.Error as err:
        st.error(f"Database Connection Error: {err}")
        return None

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.set_page_config(page_title="Local Food Wastage Management System", layout="wide")

st.title("🍲 Local Food Wastage Management System")
st.write("Connecting surplus food providers with receivers using Streamlit + MySQL")

menu = ["Dashboard", "CRUD Operations", "Query Explorer", "About"]
choice = st.sidebar.selectbox("Navigation", menu)

conn = get_connection()
if conn:
    cursor = conn.cursor()

    # -------- DASHBOARD --------
    if choice == "Dashboard":
        st.subheader("📊 Food Distribution Insights")

        # --- FILTERS SECTION ---
        st.markdown("### 🔍 Filter Food Listings")

        # Fetch unique filter options from database
        try:
            cursor.execute("SELECT DISTINCT Location FROM food_listings;")
            cities = [row['Location'] for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT Provider_ID FROM food_listings;")
            providers = [str(row['Provider_ID']) for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT Food_Type FROM food_listings;")
            food_types = [row['Food_Type'] for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT Meal_Type FROM food_listings;")
            meal_types = [row['Meal_Type'] for row in cursor.fetchall()]
        except MySQLdb.Error as e:
            st.error(f"Error loading filters: {e}")
            cities, providers, food_types, meal_types = [], [], [], []

        # Create Streamlit filter widgets
        col1, col2, col3, col4 = st.columns(4)
        selected_city = col1.selectbox("City", ["All"] + cities)
        selected_provider = col2.selectbox("Provider ID", ["All"] + providers)
        selected_food_type = col3.selectbox("Food Type", ["All"] + food_types)
        selected_meal_type = col4.selectbox("Meal Type", ["All"] + meal_types)

        # --- FILTERED QUERY ---
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

        # Execute filtered query
        cursor.execute(query, params)
        data = cursor.fetchall()
        df = pd.DataFrame(data)

        st.markdown("### 🍱 Filtered Food Listings")
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No records found for the selected filters.")

        # --- PROVIDER CONTACT DETAILS SECTION ---
        st.markdown("---")
        st.markdown("### 📞 Provider Contact Details")

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
            st.dataframe(provider_data)
        except MySQLdb.Error as e:
            st.error(f"Error loading provider details: {e}")

        # --- ADDITIONAL DASHBOARD INSIGHTS ---
        st.markdown("---")
        st.markdown("### 📈 Analytical Overview")

        queries = {
            "Providers per City": "SELECT City, COUNT(*) AS Providers FROM providers GROUP BY City;",
            "Top Provider Types": "SELECT Type, COUNT(*) AS Total FROM providers GROUP BY Type ORDER BY Total DESC;",
            "Available Food": "SELECT SUM(Quantity) AS Total_Available FROM food_listings;",
            "Claims by Status": "SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status;"
        }

        for name, q in queries.items():
            st.write(f"#### {name}")
            try:
                cursor.execute(q)
                result = pd.DataFrame(cursor.fetchall())
                st.dataframe(result)
                if len(result.columns) == 2:
                    st.bar_chart(result.set_index(result.columns[0]))
            except MySQLdb.Error as e:
                st.error(f"Error running {name}: {e}")


        queries = {
            # 1. Providers per City
            "Providers per City": """
                SELECT City, COUNT(*) AS Total_Providers 
                FROM providers 
                GROUP BY City;
            """,

            # 2. Receivers per City
            "Receivers per City": """
                SELECT City, COUNT(*) AS Total_Receivers 
                FROM receivers 
                GROUP BY City;
            """,

            # 3. Top Provider Types
            "Top Provider Types": """
                SELECT Type, COUNT(*) AS Total 
                FROM providers 
                GROUP BY Type 
                ORDER BY Total DESC;
            """,

            # 4. Contact Info of Providers by City
            "Provider Contact Info (Sample City)": """
                SELECT Name, Contact, City 
                FROM providers 
                WHERE City = 'Delhi';
            """,

            # 5. Top Receivers by Food Claims
            "Top Receivers by Food Claims": """
                SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
                FROM receivers r
                JOIN claims c ON r.Receiver_ID = c.Receiver_ID
                GROUP BY r.Name
                ORDER BY Total_Claims DESC;
            """,

            # 6. Total Food Quantity Available
            "Total Food Quantity Available": """
                SELECT SUM(Quantity) AS Total_Quantity 
                FROM food_listings;
            """,

            # 7. Cities with Highest Food Listings
            "Cities with Highest Food Listings": """
                SELECT Location AS City, COUNT(*) AS Listings
                FROM food_listings
                GROUP BY Location
                ORDER BY Listings DESC;
            """,

            # 8. Most Common Food Types
            "Most Common Food Types": """
                SELECT Food_Type, COUNT(*) AS Count 
                FROM food_listings 
                GROUP BY Food_Type 
                ORDER BY Count DESC;
            """,

            # 9. Total Claims per Food Item
            "Total Claims per Food Item": """
                SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
                FROM food_listings f
                LEFT JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Food_Name;
            """,

            # 10. Top Providers with Most Successful Claims
            "Top Providers with Most Successful Claims": """
                SELECT p.Name AS Provider, COUNT(c.Claim_ID) AS Successful_Claims
                FROM providers p
                JOIN food_listings f ON p.Provider_ID = f.Provider_ID
                JOIN claims c ON f.Food_ID = c.Food_ID
                WHERE c.Status = 'Completed'
                GROUP BY p.Name
                ORDER BY Successful_Claims DESC;
            """,

            # 11. Claim Status Percentage
            "Claim Status Percentage": """
                SELECT Status, 
                       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
                FROM claims 
                GROUP BY Status;
            """,

            # 12. Average Quantity Claimed per Receiver
            "Average Quantity Claimed per Receiver": """
                SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
                FROM receivers r
                JOIN claims c ON r.Receiver_ID = c.Receiver_ID
                JOIN food_listings f ON c.Food_ID = f.Food_ID
                GROUP BY r.Name;
            """,

            # 13. Most Claimed Meal Type
            "Most Claimed Meal Type": """
                SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
                FROM food_listings f
                JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Meal_Type
                ORDER BY Total_Claims DESC;
            """,

            # 14. Total Food Donated by Provider
            "Total Food Donated by Provider": """
                SELECT p.Name, SUM(f.Quantity) AS Total_Donated
                FROM providers p
                JOIN food_listings f ON p.Provider_ID = f.Provider_ID
                GROUP BY p.Name;
            """,

            # 15. Food Wastage Trend by Expiry
            "Food Wastage Trend (Expired Items)": """
                SELECT COUNT(*) AS Expired_Foods
                FROM food_listings
                WHERE Expiry_Date < CURDATE();
            """
        }

        for name, q in queries.items():
            st.write(f"### {name}")
            try:
                cursor.execute(q)
                data = cursor.fetchall()
                df = pd.DataFrame(data)
                st.dataframe(df)
                if len(df.columns) == 2:
                    st.bar_chart(df.set_index(df.columns[0]))
            except MySQLdb.Error as e:
                st.error(f"Error executing {name}: {e}")

    # -------- CRUD OPERATIONS --------
    elif choice == "CRUD Operations":
        st.subheader("🛠 Manage Food Listings")
        action = st.selectbox("Select Action", ["Add", "View", "Update", "Delete"])

        if action == "Add":
            food_name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=1)
            expiry = st.date_input("Expiry Date")
            provider_id = st.number_input("Provider ID", min_value=1)
            location = st.text_input("Location")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            if st.button("Add Record"):
                try:
                    cursor.execute("""
                        INSERT INTO food_listings 
                        (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (food_name, qty, expiry, provider_id, location, food_type, meal_type))
                    conn.commit()
                    st.success("✅ Record added successfully!")
                except MySQLdb.Error as e:
                    st.error(f"Insert failed: {e}")

        elif action == "View":
            cursor.execute("SELECT * FROM food_listings LIMIT 20;")
            st.dataframe(pd.DataFrame(cursor.fetchall()))

        elif action == "Update":
            food_id = st.number_input("Food ID to Update", min_value=1)
            new_qty = st.number_input("New Quantity", min_value=1)
            if st.button("Update Quantity"):
                try:
                    cursor.execute("UPDATE food_listings SET Quantity=%s WHERE Food_ID=%s;", (new_qty, food_id))
                    conn.commit()
                    st.success("✅ Quantity updated successfully!")
                except MySQLdb.Error as e:
                    st.error(f"Update failed: {e}")

        elif action == "Delete":
            food_id = st.number_input("Food ID to Delete", min_value=1)
            if st.button("Delete Record"):
                try:
                    cursor.execute("DELETE FROM food_listings WHERE Food_ID=%s;", (food_id,))
                    conn.commit()
                    st.warning("🗑️ Record deleted successfully.")
                except MySQLdb.Error as e:
                    st.error(f"Delete failed: {e}")

    # -------- QUERY EXPLORER --------
    elif choice == "Query Explorer":
        st.subheader("🔍 Explore SQL Queries")
        query = st.text_area("Enter SQL Query")
        if st.button("Run"):
            try:
                cursor.execute(query)
                st.dataframe(pd.DataFrame(cursor.fetchall()))
            except MySQLdb.Error as e:
                st.error(f"SQL Error: {e}")

    elif choice == "About":
        st.info("Developed by Nirmal Kumar Bhagatkar | Streamlit + MySQL Project")

    cursor.close()
    conn.close()

else:
    st.error("❌ Database connection failed.")
