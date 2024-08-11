import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import OperationalError
import openai
import config

# Set the OpenAI API key with config.py
openai.api_key = config.api_key

def generate_sql_query(database_type, query_intent):
    if database_type == 'postgresql' and query_intent == 'transactions_per_year':
        query = """
        SELECT EXTRACT(YEAR FROM trans_date_trans_time) AS Year, COUNT(*) AS Transactions
        FROM fraud_data
        GROUP BY EXTRACT(YEAR FROM trans_date_trans_time);
        """
    elif database_type == 'mysql' and query_intent == 'transactions_per_year':
        query = """
        SELECT YEAR(trans_date_trans_time) AS Year, COUNT(*) AS Transactions
        FROM fraud_data
        GROUP BY YEAR(trans_date_trans_time);
        """
    return query



# Define the generate_text function
def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=prompt,
        temperature=0.2,
        top_p=0.9,
    )
    return response.choices[0].message['content'].strip()

# Function to connect to the PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=config.db_port,
            database="credit_card_fraud",
            user=config.db_user,
            password=config.db_password
        )
        return conn
    except OperationalError as e:
        st.error(f"Could not connect to the database: {e}")
        return None


def set_background(image_url):
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-attachment: fixed;
        filter: brightness(85%) contrast(100%);
    }}

    h1 {{
        font-size: 4em;
        color: #FFFFFF;
        font-weight: bold;
        text-align: center;
    }}

    .description {{
        font-size: 1.8em;
        color: #FFFFFF;
        text-align: justify;
        margin: 20px;
    }}

    label {{
        font-size: 1.5em;
        color: #FFFFFF;
    }}

    .stTextInput>div>div>input {{
        font-size: 1.5em;
        color: #000000;
        background-color: rgba(255, 255, 255, 0.9);
    }}

    .stButton>button {{
        font-size: 1.5em;
        color: #FFFFFF;
        background-color: rgba(0, 0, 0, 0.7);
    }}

    .stDataFrame {{
        font-size: 1.5em;
        color: #FFFFFF;
        background-color: rgba(0, 0, 0, 0.7);
    }}

    .footer {{
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 1.2em;
        color: #FFFFFF;
        background-color: rgba(0, 0, 0, 0.6);
        padding: 5px 10px;
        border-radius: 8px;
        z-index: 1000;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Use the online image as the background and set footer text
set_background("https://cdn.pixabay.com/photo/2015/12/01/15/43/black-1072366_1280.jpg")

# Display footer text
st.markdown('<div class="footer">Developed by Guneet Sharma</div>', unsafe_allow_html=True)

# Project title
st.title("Credit Card Fraud Analysis Tool")

# Project description
st.markdown("""
<div class="description" style="font-size:18px; line-height:1.6;">
This tool is designed to help you explore and analyze credit card transaction data to identify fraudulent activities. The tool provides the following key features:

- **Data Upload and Preprocessing:** Upload your CSV files containing credit card transaction data. The data will be preprocessed and inserted into a PostgreSQL database for efficient querying and analysis.

- **AI-Powered Chatbot Interface:** Use our AI-powered chatbot to generate accurate SQL queries for exploring the data. The chatbot converts natural language questions into SQL queries and executes them against the database.

- **In-depth Data Analysis:** Perform in-depth analysis of the data to identify patterns and trends related to fraudulent transactions. Utilize the generated SQL queries to fetch specific insights from the data.

**Technology Stack:** 
- Python
- Streamlit
- PostgreSQL
- OpenAI GPT-4
</div>
""", unsafe_allow_html=True)

# Step 1: File upload and processing
uploaded_file = st.file_uploader("Choose a CSV file to upload", type="csv")

if uploaded_file is not None:
    st.info("Processing the uploaded file...")
    df = pd.read_csv(uploaded_file)

    # Display the columns in the uploaded CSV
    st.write("Columns in the uploaded CSV file:")
    st.write(df.columns.tolist())

    df['dob'] = pd.to_datetime(df['dob'], format='%d-%m-%Y')
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'], format='%d-%m-%Y %H:%M')
    df['is_fraud'] = df['is_fraud'].astype(bool)

    st.success("File processed successfully!")
    st.write("Preview of the uploaded data:")
    st.write(df.head())

    # EDA Menu
    st.sidebar.header('Data Analysis Options')

    # Adding a slider for selecting a range of transaction amounts
    amount_slider = st.sidebar.slider(
        'Select Transaction Amount Range',
        min_value=0,
        max_value=10000,
        value=(500, 5000)
    )

    # EDA menu with options
    eda_options = st.sidebar.selectbox(
        'Select EDA Operation',
        ('Overview', 'Transaction Distribution', 'Time Series Analysis', 'Anomaly Detection')
    )

    st.sidebar.markdown("""
    **Select the transaction amount range and choose an EDA operation from the menu above to explore the data.**
    """)

    # EDA implementation
    filtered_df = df[(df['amt'] >= amount_slider[0]) & (df['amt'] <= amount_slider[1])]

    ## OVERVIEW
    if eda_options == 'Overview':
        st.subheader('Data Overview')
        st.write("Summary statistics and general information about the dataset within the selected range.")
        st.write(filtered_df.describe())  # Display summary statistics for filtered data

    ## Transaction distribution
    elif eda_options == 'Transaction Distribution':
        st.subheader('Transaction Distribution')

        # Histogram of transaction amounts
        st.write("Distribution of Transaction Amounts:")
        st.bar_chart(filtered_df['amt'].value_counts().head(20))  # Adjust or customize as needed

        # Count of fraud vs. non-fraud
        st.write("Fraudulent vs. Non-Fraudulent Transactions:")
        st.bar_chart(filtered_df['is_fraud'].value_counts())

    ## Time series
    elif eda_options == 'Time Series Analysis':
        st.subheader('Time Series Analysis')

        # Group by date and count transactions
        time_series_data = filtered_df.groupby(filtered_df['trans_date_trans_time'].dt.date).size()
        st.line_chart(time_series_data)

    ## Anomaly detection
    elif eda_options == 'Anomaly Detection':
        st.subheader('Anomaly Detection')

        # Using IQR to detect anomalies
        Q1 = filtered_df['amt'].quantile(0.25)
        Q3 = filtered_df['amt'].quantile(0.75)
        IQR = Q3 - Q1

        # Filtering out the outliers
        anomalies = filtered_df[(filtered_df['amt'] < (Q1 - 1.5 * IQR)) | (filtered_df['amt'] > (Q3 + 1.5 * IQR))]
        st.write("Number of detected anomalies: ", anomalies.shape[0])
        st.write(anomalies)

    # Function to insert data into the database
    def insert_data(conn, cur, df):
        try:
            # Insert unique merchants
            merchants = df[['merchant', 'category']].drop_duplicates().reset_index(drop=True)
            for _, row in merchants.iterrows():
                cur.execute("""
                INSERT INTO merchants (merchant_name, category) 
                VALUES (%s, %s) 
                ON CONFLICT DO NOTHING;
                """, (row['merchant'], row['category']))

            # Insert unique locations
            locations = df[['city', 'state', 'lat', 'long', 'city_pop']].drop_duplicates().reset_index(drop=True)
            for _, row in locations.iterrows():
                cur.execute("""
                INSERT INTO locations (city, state, lat, long, city_pop) 
                VALUES (%s, %s, %s, %s, %s) 
                ON CONFLICT DO NOTHING;
                """, (row['city'], row['state'], row['lat'], row['long'], row['city_pop']))

            # Insert unique users
            users = df[['job', 'dob']].drop_duplicates().reset_index(drop=True)
            for _, row in users.iterrows():
                cur.execute("""
                INSERT INTO users (job, dob) 
                VALUES (%s, %s) 
                ON CONFLICT DO NOTHING;
                """, (row['job'], row['dob']))

            conn.commit()
            st.success("Data uploaded and inserted into the database successfully!")

        except (psycopg2.Error, OperationalError) as db_error:
            st.error(f"Database operation failed: {db_error}")
            conn = connect_to_db()  # Reconnect if connection is lost
            if conn:
                cur = conn.cursor()
                insert_data(conn, cur, df)

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # Step 2: Database setup
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()

        # Create tables as per the normalized schema
        create_tables_query = """
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id SERIAL PRIMARY KEY,
            merchant_name VARCHAR(255),
            category VARCHAR(50)
        );

        CREATE TABLE IF NOT EXISTS locations (
            location_id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            state VARCHAR(10),
            lat NUMERIC,
            long NUMERIC,
            city_pop INTEGER
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            job VARCHAR(255),
            dob DATE
        );

        CREATE TABLE IF NOT EXISTS fraud_data (
            transaction_id SERIAL PRIMARY KEY,
            trans_date_trans_time TIMESTAMP,
            amt NUMERIC,
            trans_num VARCHAR(50),
            is_fraud BOOLEAN,
            merchant_id INT REFERENCES merchants(merchant_id),
            location_id INT REFERENCES locations(location_id),
            user_id INT REFERENCES users(user_id)
        );
        """
        cur.execute(create_tables_query)
        conn.commit()

        insert_data(conn, cur, df)

# Step 3: Chatbot Interface with GPT
st.write("### Chatbot Interface")
user_question = st.text_input("Ask a question about the credit card fraud data:")

if st.button("Submit"):
    try:
        gpt_prompt = [
            {"role": "system", "content": """
                You are a SQL expert with access to a database containing the following tables:
                - fraud_data (columns: trans_date_trans_time, amt, trans_num, is_fraud, merchant_id, location_id, user_id)
                - merchants (columns: merchant_id, merchant_name, category)
                - locations (columns: location_id, city, state, lat, long, city_pop)
                - users (columns: user_id, job, dob)
                Generate accurate SQL queries using the exact column names provided. 
                Handle various types of queries such as:
                1. Counting rows in a table.
                2. Summing values under certain conditions.
                3. Finding averages grouped by a column.
                4. Performing joins between tables based on foreign keys.
                Always select the most relevant columns for the query requested.
                Example: "Count the number of fraud transactions" should translate to "SELECT COUNT(*) FROM fraud_data WHERE is_fraud = TRUE;"
            """},
            {"role": "user",
             "content": f"Generate an SQL query for the following request: {user_question}. Provide only the SQL query."}
        ]

        query = generate_text(gpt_prompt)

        if query.lower().startswith(("select", "insert", "update", "delete")):
            st.write(f"Generated SQL Query: `{query}`")

            conn = connect_to_db()
            if conn:
                cur = conn.cursor()
                cur.execute(query)
                result = cur.fetchall()

                col_names = [desc[0] for desc in cur.description]
                st.write("Query Results:")
                st.write(pd.DataFrame(result, columns=col_names))

                cur.close()
                conn.close()
        else:
            st.warning(
                "The generated text doesn't seem to be an SQL query. Please try again or rephrase your question.")

    except Exception as e:
        st.error(f"An error occurred while generating the SQL query: {e}")
