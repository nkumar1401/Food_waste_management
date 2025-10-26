🍲 Local Food Wastage Management System

A data-driven Streamlit web application that connects food providers and receivers to minimize local food wastage.

📖 Overview

Food wastage is a growing global concern — millions of tons of edible food go to waste while many people remain hungry.
This project introduces a Local Food Wastage Management System, a full-stack analytical dashboard built using Python, MySQL, and Streamlit.

It enables:

Restaurants and individuals to list surplus food

NGOs and receivers to claim available food

Real-time insights into food donations and claims

Visual analytics on food distribution patterns

🧠 Features

✅ Dashboard & Insights

Interactive dashboard with filters (city, provider, food type, meal type)

Quick statistics on total food, providers, and receivers

Analytical charts (bar graphs, claim trends, provider analysis)

✅ CRUD Operations

Add, update, view, and delete food listings directly from the app

Auto-updates reflected in the MySQL database

✅ SQL Analysis (15 Key Queries)

Displays outputs of all 15 SQL queries required by project evaluation

Generates insights such as:

Top contributing providers

Most claimed meal types

Food wastage trends

Claim completion statistics

✅ Provider Coordination

View contact details of providers for direct communication

✅ Query Explorer

Run custom SQL queries dynamically and view the results instantly

🗂️ Project Architecture
📦 food_wastage_management_system/
│
├── food_wastage_analysis.py     # Main Streamlit app
├── .env                         # Environment variables (DB credentials)
├── requirements.txt              # Python dependencies
├── data/
│   ├── providers_data.csv
│   ├── receivers_data.csv
│   ├── food_listings_data.csv
│   └── claims_data.csv
└── README.md                    # Project documentation

🧰 Tech Stack
Component	Technology
Frontend	Streamlit
Backend	Python
Database	MySQL
ORM / Connector	MySQLdb



🚀 Deployment

You can deploy the app easily using:

Streamlit Cloud

Render

Google Cloud Run


🧑‍💻 Developed By

👤 Nirmal Kumar Bhagatkar
🎓 IT Engineer | Full Stack & AI Developer | Data Science Enthusiast |AI/ML Engineer
📍 India
💼 LinkedIn Profile
 www.linkedin.com/in/nirmal-kumar-bhagatkar

🏆 Highlights

✅ Real-time database integration
✅ Professional Streamlit dashboard UI
✅ Analytical visualization of SQL data
✅ Social impact project — Food Waste Reduction


📜 License

This project is licensed under the MIT License.
Feel free to use and improve it with proper credits.

⭐ Acknowledgements

Streamlit Documentation

MySQLdb Library

Python Decouple

Guidance from Mentor/Instructor (if applicable)

💬 “Code for change. Feed the future.” 🌱
Configuration Management	Python Decouple (.env)
Data Visualization	Streamlit Charts, Pandas
IDE Recommended	VS Code or PyCharm
