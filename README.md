# AI Agent Dashboard

## Project Description
The AI Agent Dashboard is a powerful tool designed to integrate and manage AI-driven tasks with ease. It connects to Google Sheets, allowing seamless data management, search functionality, and dashboard customization. Key features include setting up search queries, visualizing data, and automating tasks, all within an intuitive interface. The dashboard offers flexibility for further integrations and can be tailored to specific user needs, making it ideal for both personal and professional applications.

Setup Instructions

1. Clone the repository:
   bash
   git clone https://github.com/srihul/AI-Agent-Dashboard.git
   cd AI-Agent-Dashboard
2. Install dependencies:

bash
pip install -r requirements.txt
Create a .env file in the root directory and add your Google Sheets API key:

env
GOOGLE_SHEET_API_KEY=your-api-key
If you have other environment variables, make sure to add them to the .env file.

## Usage Guide
Connect Google Sheets:

Obtain the Google Sheets API credentials from the Google Sheets API Quickstart Guide.
Place your credentials in the .env file as shown above.
Set Up Search Queries:

Open the dashboard interface and define search queries to filter and display data from your Google Sheets.
## Interact with the Interface:

Launch the dashboard to interact with your data, input search queries, visualize data, and customize settings.
API Keys and Environment Variables
To use the dashboard, you need to provide the following API keys and environment variables:

Google Sheets API Key: Obtain it from the Google Developer Console and add it to the .env file.

Other API keys can be added to the .env file in the same format:

env
API_KEY_NAME=your-api-key
