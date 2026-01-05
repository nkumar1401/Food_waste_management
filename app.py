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
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Epicurean Reserve | Waste Management",
    layout="wide",
    page_icon="🍽️"
)


# -----------------------------
# INDO-GLOBAL LUXURY CSS
# -----------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@300;400;600&display=swap');

        /* Global Canvas - Silk Finish */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #F9F7F2; 
            font-family: 'Inter', sans-serif;
        }

        /* Sidebar - Royal Emerald & Saffron */
        [data-testid="stSidebar"] {
            background-color: #1B3022; 
            border-right: 3px solid #FF9933;
        }
        [data-testid="stSidebar"] * { color: #F9F7F2 !important; }

        /* Branding Headers */
        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 52px; color: #1B3022;
            text-align: center; margin-bottom: 0px; font-weight: 700;
        }
        .cultural-sub {
            text-align: center; color: #FF9933;
            font-family: 'Playfair Display', serif;
            font-style: italic; font-size: 24px; margin-bottom: 5px;
        }
        .global-sub {
            text-align: center; color: #666; font-size: 14px;
            letter-spacing: 2px; text-transform: uppercase; margin-bottom: 40px;
        }

        /* Section Accents */
        .section-header {
            font-family: 'Playfair Display', serif;
            font-size: 30px; color: #1B3022;
            border-bottom: 2px solid #FF9933;
            display: inline-block; padding-right: 50px;
            margin-top: 30px; margin-bottom: 20px;
        }

        /* Luxury Metric Cards */
        .metric-card {
            background: white; padding: 25px; border-radius: 8px;
            border-left: 6px solid #FF9933;
            box-shadow: 0 12px 24px rgba(0,0,0,0.05);
        }
        
        /* Indo-Global Buttons */
        .stButton>button {
            background-color: #FF9933 !important;
            color: white !important; border: none !important;
            border-radius: 4px !important; text-transform: uppercase;
            letter-spacing: 2px; font-weight: 700; width: 100%;
        }
        .stButton>button:hover {
            background-color: #1B3022 !important; color: #FF9933 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# REFINED HEADER
# -----------------------------
st.markdown('<div class="main-title">The Epicurean Reserve</div>', unsafe_allow_html=True)
st.markdown('<div class="cultural-sub">अन्नं ब्रह्म – Food is Divine</div>', unsafe_allow_html=True)
st.markdown('<div class="global-sub">A Global Standard in Dignified Resource Redistribution</div>', unsafe_allow_html=True)

menu = ["Exhibition Dashboard", "Inventory Management (CRUD)", "Concierge SQL Insights", "Direct SQL Access", "The Portfolio"]
choice = st.sidebar.selectbox("📂 Select Department", menu)

conn = get_connection()
if conn:
    cursor = conn.cursor()

    # -------- EXHIBITION DASHBOARD --------
    if choice == "Exhibition Dashboard":
        # --- QUICK METRICS ---
        cm1, cm2, cm3 = st.columns(3)
        cursor.execute("SELECT COUNT(*) AS total FROM providers;")
        p_count = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM receivers;")
        r_count = cursor.fetchone()['total']
        cursor.execute("SELECT SUM(Quantity) AS qty FROM food_listings;")
        total_qty = cursor.fetchone()['qty']

        with cm1: st.markdown(f'<div class="metric-card"><small>PREMIUM PROVIDERS</small><h2>{p_count}</h2></div>', unsafe_allow_html=True)
        with cm2: st.markdown(f'<div class="metric-card"><small>DIGNIFIED RECEIVERS</small><h2>{r_count}</h2></div>', unsafe_allow_html=True)
        with cm3: st.markdown(f'<div class="metric-card"><small>AVAILABLE SERVINGS</small><h2>{total_qty if total_qty else 0}</h2></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Live Inventory & Filtering</div>', unsafe_allow_html=True)

        # --- FILTERS SECTION ---
        with st.expander("🔍 Refine Search Results", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            try:
                cursor.execute("SELECT DISTINCT Location FROM food_listings;")
                cities = [row['Location'] for row in cursor.fetchall()]
                cursor.execute("SELECT DISTINCT Provider_ID FROM food_listings;")
                providers_list = [str(row['Provider_ID']) for row in cursor.fetchall()]
                cursor.execute("SELECT DISTINCT Food_Type FROM food_listings;")
                food_types = [row['Food_Type'] for row in cursor.fetchall()]
                cursor.execute("SELECT DISTINCT Meal_Type FROM food_listings;")
                meal_types = [row['Meal_Type'] for row in cursor.fetchall()]
            except:
                cities, providers_list, food_types, meal_types = [], [], [], []

            selected_city = col1.selectbox("Metropolitan Area", ["All"] + cities)
            selected_provider = col2.selectbox("Provider Reference", ["All"] + providers_list)
            selected_food_type = col3.selectbox("Culinary Category", ["All"] + food_types)
            selected_meal_type = col4.selectbox("Service Time", ["All"] + meal_types)

        # --- FILTERED FOOD LISTINGS ---
        query = "SELECT * FROM food_listings WHERE 1=1"
        params = []
        if selected_city != "All": query += " AND Location = %s"; params.append(selected_city)
        if selected_provider != "All": query += " AND Provider_ID = %s"; params.append(selected_provider)
        if selected_food_type != "All": query += " AND Food_Type = %s"; params.append(selected_food_type)
        if selected_meal_type != "All": query += " AND Meal_Type = %s"; params.append(selected_meal_type)

        cursor.execute(query, params)
        food_data = pd.DataFrame(cursor.fetchall())
        if not food_data.empty:
            st.dataframe(food_data, use_container_width=True)
        else:
            st.warning("No records found for the current selection.")

        # --- PROVIDER CONTACT DETAILS ---
        st.markdown('<div class="section-header">📞 Concierge Contact Registry</div>', unsafe_allow_html=True)
        try:
            provider_query = "SELECT Provider_ID, Name, Type, City, Contact FROM providers ORDER BY City;"
            cursor.execute(provider_query)
            p_contact_df = pd.DataFrame(cursor.fetchall())
            st.dataframe(p_contact_df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load registry: {e}")

# -------- EXECUTIVE MASTER REGISTRY (FULL CRUD) --------
    elif choice == "Inventory Management (CRUD)":
        st.markdown('<div class="section-header">Executive Master Registry</div>', unsafe_allow_html=True)
        
        # Select target registry [cite: 39, 40, 41, 42]
        manage_target = st.radio("Select Department to Manage", ["Food Listings", "Providers", "Receivers", "Claims"], horizontal=True)
        
        # Action selection for CRUD [cite: 20, 110]
        action = st.selectbox("Select Management Action", ["View & Search", "Add New Record", "Update Existing Record", "Archive (Delete) Record"])

        # Table Mapping for SQL Logic [cite: 44, 52, 59, 70]
        table_map = {"Food Listings": "food_listings", "Providers": "providers", "Receivers": "receivers", "Claims": "claims"}
        id_map = {"Food Listings": "Food_ID", "Providers": "Provider_ID", "Receivers": "Receiver_ID", "Claims": "Claim_ID"}

        # --- FEATURE 1: VIEW & SEARCH (READ) ---
        if action == "View & Search":
            search_query = st.text_input(f"🔍 Search {manage_target} by Name, City, or ID")
            
            sql = f"SELECT * FROM {table_map[manage_target]} WHERE 1=1"
            params = []
            
            if search_query:
                # Dynamic search based on table columns [cite: 47, 50, 55, 62, 67]
                if manage_target == "Food Listings":
                    sql += " AND (Food_Name LIKE %s OR Location LIKE %s)"
                elif manage_target == "Claims":
                    sql += " AND Status LIKE %s"
                else: # Providers or Receivers
                    sql += " AND (Name LIKE %s OR City LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            cursor.execute(sql, params)
            df = pd.DataFrame(cursor.fetchall())
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No records found.")

        # --- FEATURE 2: ADD NEW RECORD (CREATE) ---
        elif action == "Add New Record":
            with st.form(f"add_{manage_target}_form"):
                if manage_target == "Food Listings":
                    f_name = st.text_input("Food Item Name")
                    f_qty = st.number_input("Quantity", min_value=1)
                    f_exp = st.date_input("Expiry Date")
                    p_id = st.number_input("Provider ID Reference", min_value=1)
                    loc = st.text_input("Location City")
                    f_t = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
                    m_t = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                    
                    if st.form_submit_button("Commit to Registry"):
                        cursor.execute("INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                       (f_name, f_qty, f_exp, p_id, loc, f_t, m_t))
                        st.success("Food Listing Created Successfully")

                elif manage_target == "Providers":
                    p_name = st.text_input("Provider Name")
                    p_type = st.selectbox("Type", ["Restaurant", "Grocery Store", "Supermarket"])
                    p_city = st.text_input("City")
                    p_contact = st.text_input("Contact Number")
                    if st.form_submit_button("Register Provider"):
                        cursor.execute("INSERT INTO providers (Name, Type, City, Contact) VALUES (%s, %s, %s, %s)", (p_name, p_type, p_city, p_contact))
                        st.success("Provider Registered")

                elif manage_target == "Receivers":
                    r_name = st.text_input("Receiver/NGO Name")
                    r_type = st.selectbox("Category", ["NGO", "Community Center", "Individual"])
                    r_city = st.text_input("City")
                    r_contact = st.text_input("Contact")
                    if st.form_submit_button("Register Beneficiary"):
                        cursor.execute("INSERT INTO receivers (Name, Type, City, Contact) VALUES (%s, %s, %s, %s)", (r_name, r_type, r_city, r_contact))
                        st.success("Receiver Registered")

                elif manage_target == "Claims":
                    f_id = st.number_input("Food ID", min_value=1)
                    r_id = st.number_input("Receiver ID", min_value=1)
                    status = st.selectbox("Initial Status", ["Pending", "Completed"])
                    if st.form_submit_button("Log Claim"):
                        cursor.execute("INSERT INTO claims (Food_ID, Receiver_ID, Status) VALUES (%s, %s, %s)", (f_id, r_id, status))
                        st.success("Claim Logged")

# --- FEATURE 3: DYNAMIC MASTER UPDATE ENGINE ---
        elif action == "Update Existing Record":
            st.markdown(f"### 📝 Modify {manage_target} Entry")
            
            # Identify the record
            target_id = st.number_input(f"Enter {id_map[manage_target]} to Modify", min_value=1)
            
            if target_id:
                # Fetch current data to ensure accuracy and dignify the process
                cursor.execute(f"SELECT * FROM {table_map[manage_target]} WHERE {id_map[manage_target]}=%s", (target_id,))
                current_record = cursor.fetchone()
                
                if current_record:
                    st.info(f"Targeting Record: **{target_id}**")
                    
                    # --- DYNAMIC FIELD SELECTOR BASED ON TARGET ---
                    if manage_target == "Food Listings":
                        fields = ["Food_Name", "Quantity", "Expiry_Date", "Location", "Food_Type", "Meal_Type"]
                    elif manage_target == "Providers":
                        fields = ["Name", "Type", "Address", "City", "Contact"]
                    elif manage_target == "Receivers":
                        fields = ["Name", "Type", "City", "Contact"]
                    elif manage_target == "Claims":
                        fields = ["Status"]
                    
                    field_to_modify = st.selectbox("Select Attribute to Revise", fields)
                    
                    # --- DYNAMIC INPUT GENERATION ---
                    # Handles specialized inputs like dates or dropdowns to ensure data consistency [cite: 17]
                    if field_to_modify in ["Food_Type", "Type"]:
                        options = ["Vegetarian", "Non-Vegetarian", "Vegan"] if manage_target == "Food Listings" else ["Restaurant", "Grocery Store", "Supermarket"]
                        new_val = st.selectbox(f"New {field_to_modify}", options)
                    elif field_to_modify == "Meal_Type":
                        new_val = st.selectbox("New Meal Category", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                    elif field_to_modify == "Status":
                        new_val = st.selectbox("Update Fulfillment Status", ["Pending", "Completed", "Cancelled"])
                    elif field_to_modify == "Expiry_Date":
                        new_val = st.date_input("Select New Expiry Date")
                    elif field_to_modify == "Quantity":
                        new_val = st.number_input("Revised Quantity", min_value=1)
                    else:
                        new_val = st.text_input(f"Enter New {field_to_modify}", value=str(current_record[field_to_modify]))

                    # --- EXECUTION ---
                    if st.button(f"AUTHORIZE {field_to_modify.upper()} CHANGE"):
                        try:
                            # Dynamic SQL to minimize manual code workload
                            sql = f"UPDATE {table_map[manage_target]} SET {field_to_modify}=%s WHERE {id_map[manage_target]}=%s"
                            cursor.execute(sql, (new_val, target_id))
                            conn.commit()
                            st.success(f"✅ Registry updated: {field_to_modify} is now '{new_val}'.")
                        except Exception as e:
                            st.error(f"Modification halted: {e}")
                else:
                    st.warning(f"Identification failed: No record found with {id_map[manage_target]} {target_id}.")

        # --- FEATURE 4: ARCHIVE RECORD (DELETE) ---
        elif action == "Archive (Delete) Record":
            delete_id = st.number_input(f"Enter {id_map[manage_target]} to Permanently Archive", min_value=1)
            st.warning("Warning: Archival is permanent and cannot be undone.")
            if st.button("Confirm Archival"):
                cursor.execute(f"DELETE FROM {table_map[manage_target]} WHERE {id_map[manage_target]}=%s", (delete_id,))
                st.error("Record has been purged from the system.")

    # -------- CONCIERGE SQL INSIGHTS (The 15 Queries) --------
    elif choice == "Concierge SQL Insights":
        st.markdown('<div class="section-header">Operational Analytics & Trend Intelligence</div>', unsafe_allow_html=True)
        
        sql_queries = {
            "1️⃣ Provider Density per City": "SELECT City, COUNT(*) AS Total FROM providers GROUP BY City;",
            "2️⃣ Receiver Density per City": "SELECT City, COUNT(*) AS Total FROM receivers GROUP BY City;",
            "3️⃣ Dominant Provider Classifications": "SELECT Type, COUNT(*) AS Total FROM providers GROUP BY Type ORDER BY Total DESC;",
            "4️⃣ Delhi Provider Registry": "SELECT Name, Contact, City FROM providers WHERE City = 'Delhi';",
            "5️⃣ Top Beneficiary Organizations": "SELECT r.Name, COUNT(c.Claim_ID) AS Claims FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID GROUP BY r.Name ORDER BY Claims DESC;",
            "6️⃣ Global Inventory Volume": "SELECT SUM(Quantity) AS Total_Servings FROM food_listings;",
            "7️⃣ Regional Supply Leaders": "SELECT Location, COUNT(*) AS Count FROM food_listings GROUP BY Location ORDER BY Count DESC;",
            "8️⃣ Culinary Preference Trends": "SELECT Food_Type, COUNT(*) AS Count FROM food_listings GROUP BY Food_Type ORDER BY Count DESC;",
            "9️⃣ Engagement per Listing": "SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID GROUP BY f.Food_Name;",
            "🔟 Provider Success Metrics": "SELECT p.Name, COUNT(c.Claim_ID) AS Success FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID JOIN claims c ON f.Food_ID = c.Food_ID WHERE c.Status = 'Completed' GROUP BY p.Name ORDER BY Success DESC;",
            "1️⃣1️⃣ Distribution Fulfillment Ratio": "SELECT Status, ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM claims), 2) AS Percent FROM claims GROUP BY Status;",
            "1️⃣2️⃣ Average Allocation per Receiver": "SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY r.Name;",
            "1️⃣3️⃣ Peak Demand Service Hours": "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claims FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID GROUP BY f.Meal_Type ORDER BY Claims DESC;",
            "1️⃣4️⃣ Provider Contribution Leaderboard": "SELECT p.Name, SUM(f.Quantity) AS Donated FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID GROUP BY p.Name ORDER BY Donated DESC;",
            "1️⃣5️⃣ Perishability Audit (Expired)": "SELECT COUNT(*) AS Expired FROM food_listings WHERE Expiry_Date < CURDATE();"
        }

        for title, q in sql_queries.items():
            with st.expander(title):
                cursor.execute(q)
                res = pd.DataFrame(cursor.fetchall())
                if not res.empty:
                    st.dataframe(res, use_container_width=True)
                    if len(res.columns) == 2: st.bar_chart(res.set_index(res.columns[0]), color="#C5A059")

    # -------- DIRECT SQL ACCESS --------
    elif choice == "Direct SQL Access":
        st.markdown('<div class="section-header">Executive Query Terminal</div>', unsafe_allow_html=True)
        raw_q = st.text_area("Enter SQL Command for Direct Database Interfacing...")
        if st.button("Authorize Execution"):
            try:
                cursor.execute(raw_q)
                st.dataframe(pd.DataFrame(cursor.fetchall()), use_container_width=True)
            except Exception as e:
                st.error(f"Command Error: {e}")

    # -------- THE PORTFOLIO --------
    elif choice == "The Portfolio":
        st.markdown('<div class="section-header">Developer Pedigree & Vision</div>', unsafe_allow_html=True)
        st.info(f"Principal Architect: Nirmal Kumar Bhagatkar [cite: 113]\n\nFoundation: Python 3.10 | Streamlit Core | MySQL Relational Engine")
        st.write("> **Global Mission:** To solve fundamental world problems by orchestrating AI/ML systems that minimize human workload and restore dignity to all living creatures.")
        st.success("Milestone Goal: To become the first trillionaire person through a founder-led AI/ML revolution.")

    cursor.close()
    conn.close()