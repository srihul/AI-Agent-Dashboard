import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
import openai
import os
import time
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Get OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure your .env file has OPENAI_API_KEY=your-api-key-here
google_credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')  # Ensure your .env file has GOOGLE_CREDENTIALS_PATH=path-to-your-credentials

# Function to connect to Google Sheets
def connect_google_sheets(sheet_url, credentials_json):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(credentials_json, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# Function to search the web using SerpAPI with retry logic
def search_web(query, api_key):
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": api_key, "num": 1}
    attempts = 3
    for attempt in range(attempts):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises error for bad responses
            return response.json().get("organic_results", [])
        except requests.exceptions.RequestException as e:
            if attempt < attempts - 1:
                time.sleep(2)  # Wait before retrying
                continue
            else:
                return []

# Function to extract information using OpenAI
def extract_information_from_results(results, prompt):
    try:
        search_results_text = "\n".join([result.get("snippet", "") for result in results])
        full_prompt = f"{prompt}\n\n{search_results_text}"
        response = openai.Completion.create(
            model="text-davinci-003",  # You can change the model if needed
            prompt=full_prompt,
            max_tokens=150,  # Adjust token limit as needed
            temperature=0.5
        )
        extracted_info = response.choices[0].text.strip()
        return extracted_info
    except Exception as e:
        return f"Error: {e}"

# Streamlit app title
st.title("AI Agent Dashboard")
st.write("Upload CSV or connect to Google Sheets")

# CSV File Upload
csv_file = st.file_uploader("Upload your CSV file", type=["csv"])
df = None
if csv_file:
    df = pd.read_csv(csv_file)
    st.write("CSV Data Preview:")
    st.dataframe(df)

# Google Sheets Integration Section
st.subheader("Connect to Google Sheets")
sheet_url = st.text_input("Enter Google Sheet URL")
if sheet_url:
    try:
        df = connect_google_sheets(sheet_url, google_credentials_path)
        st.write("Google Sheet Data Preview:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error connecting to the sheet: {e}")

# Dynamic Query Input for Information Retrieval
st.subheader("Define Your Query")
user_prompt = st.text_input("Enter your prompt (use {entity} as a placeholder)", value="Get the email address of {entity}")

if user_prompt:
    st.write(f"Your prompt: {user_prompt}")

# Entity Selection
st.subheader("Select or Enter an Entity")
selected_entity = None

if df is not None and not df.empty:
    # Use entities from Google Sheet if available
    entity_column = st.selectbox("Select the column containing entities", df.columns)
    selected_entity = st.selectbox("Select an entity", df[entity_column].unique())
else:
    # Allow manual entry if no Google Sheet is used
    selected_entity = st.text_input("Or enter an entity manually")

# SerpAPI Key Input and Search Execution
serpapi_key = st.text_input("Enter your SerpAPI key")

if serpapi_key and user_prompt and selected_entity:
    query = user_prompt.replace("{entity}", selected_entity)
    results = search_web(query, serpapi_key)

    if results:
        extracted_data = extract_information_from_results(results, f"Extract the email address of {selected_entity} from the following web results:")
        st.subheader("Extracted Information")
        st.write(extracted_data)  # Display the extracted data
    else:
        st.write("No results found.")

# Store the extracted data in a structured format (for example, a dataframe)
if 'extracted_data' in locals() and extracted_data:
    extracted_data_structured = [{
        "Entity": selected_entity,
        "Extracted Info": extracted_data  # This is the data returned by OpenAI
    }]

    df_extracted = pd.DataFrame(extracted_data_structured)
    st.dataframe(df_extracted)  # Display the extracted data in Streamlit

    # Convert dataframe to CSV format
    csv = df_extracted.to_csv(index=False)

    # Create a download button for the CSV file
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="extracted_data.csv",
        mime="text/csv"
    )

# Google Sheets Output Integration (Optional)
def update_google_sheet(sheet_url, extracted_data, credentials_json):
    try:
        credentials = Credentials.from_service_account_file(credentials_json, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        client = gspread.authorize(credentials)
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)

        # Append extracted data to the Google Sheet
        for data in extracted_data:
            worksheet.append_row([data['Entity'], data['Extracted Info']])

        st.success("Google Sheet updated successfully.")
    except Exception as e:
        st.error(f"Error updating Google Sheet: {e}")

if st.button("Update Google Sheet"):
    if 'extracted_data_structured' in locals():
        update_google_sheet(sheet_url, extracted_data_structured, google_credentials_path)
