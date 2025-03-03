import os
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from serpapi import GoogleSearch

def search_flights():
    params = {
        "api_key": "9ecd0d88d36b62002fef347438388c8d9e42b06f2baee9935f36cb5d3e66093f",
        "engine": "google_flights",
        "hl": "it",
        "departure_id": "MXP",
        "arrival_id": "TAS",
        "outbound_date": "2025-08-31",
        "return_date": "2025-09-13",
        "currency": "EUR",
        "type": "1",
        "travel_class": "1",
        "sort_by": "2",
        "adults": "2"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

def save_flights_to_google_sheets(results, sheet_name="Flights Data"):
    creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    
    spreadsheet = client.open("Flights Data")
    worksheet = spreadsheet.worksheet(sheet_name)
    
    flights_data = [[
        "Departure Airport", "Departure Time", "Arrival Airport", "Arrival Time",
        "Duration (min)", "Airplane", "Airline", "Flight Number", "Travel Class",
        "Legroom", "Price (EUR)", "Total Duration (min)"
    ]]
    
    for flight_option in results.get("other_flights", []):
        for flight in flight_option.get("flights", []):
            flights_data.append([
                flight["departure_airport"]["name"],
                flight["departure_airport"]["time"],
                flight["arrival_airport"]["name"],
                flight["arrival_airport"]["time"],
                flight["duration"],
                flight["airplane"],
                flight["airline"],
                flight["flight_number"],
                flight["travel_class"],
                flight.get("legroom", "N/A"),
                flight_option.get("price", "N/A"),
                flight_option.get("total_duration", "N/A")
            ])
    
    worksheet.clear()
    worksheet.update("A1", flights_data)
    print("Dati salvati su Google Sheets")

if __name__ == "__main__":
    flight_results = search_flights()
    save_flights_to_google_sheets(flight_results)
