import os
import json
import gspread
import time
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from serpapi import GoogleSearch

def search_flights():
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),  # Usa variabile d'ambiente per sicurezza
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
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    except Exception as e:
        print(f"Errore nella ricerca dei voli: {e}")
        return None

def save_flights_to_google_sheets(results, sheet_name="FlightsData"):
    if not results:
        print("Nessun risultato da salvare.")
        return
    
    try:
        creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open("FlightsData")
        worksheet = spreadsheet.worksheet(sheet_name)
        
        flights_data = []
        
        for flight_option in results.get("other_flights", []):
            for flight in flight_option.get("flights", []):
                flights_data.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                    flight.get("departure_airport", {}).get("name", "N/A"),
                    flight.get("departure_airport", {}).get("time", "N/A"),
                    flight.get("arrival_airport", {}).get("name", "N/A"),
                    flight.get("arrival_airport", {}).get("time", "N/A"),
                    flight.get("duration", "N/A"),
                    flight.get("airplane", "N/A"),
                    flight.get("airline", "N/A"),
                    flight.get("flight_number", "N/A"),
                    flight.get("travel_class", "N/A"),
                    flight.get("legroom", "N/A"),
                    flight_option.get("price", "N/A"),
                    flight_option.get("total_duration", "N/A")
                ])
        
        if flights_data:
            worksheet.append_rows(flights_data)
            print(f"{len(flights_data)} voli salvati su Google Sheets")
        else:
            print("Nessun dato valido da salvare.")
    
    except Exception as e:
        print(f"Errore nel salvataggio su Google Sheets: {e}")

if __name__ == "__main__":
    flight_results = search_flights()
    save_flights_to_google_sheets(flight_results)
