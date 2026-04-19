import requests
import pandas as pd
import os

def download_datasets():
    print("Downloading actual historical weather dataset for North India (Delhi) from Open-Meteo...")
    # Open-Meteo Historical Weather API is free for non-commercial open data analysis
    delhi_url = "https://archive-api.open-meteo.com/v1/archive?latitude=28.6139&longitude=77.2090&start_date=2023-01-01&end_date=2023-12-31&hourly=temperature_2m&timezone=Asia%2FKolkata"
    
    r = requests.get(delhi_url)
    data = r.json()
    
    df_delhi = pd.DataFrame({
        "time": data["hourly"]["time"], 
        "temperature": data["hourly"]["temperature_2m"]
    })
    
    os.makedirs("data", exist_ok=True)
    df_delhi.to_csv("data/north_india_weather.csv", index=False)
    print("Saved to data/north_india_weather.csv")

    print("Downloading actual historical weather dataset for South India (Chennai) from Open-Meteo...")
    chennai_url = "https://archive-api.open-meteo.com/v1/archive?latitude=13.0827&longitude=80.2707&start_date=2023-01-01&end_date=2023-12-31&hourly=temperature_2m&timezone=Asia%2FKolkata"
    
    r = requests.get(chennai_url)
    data = r.json()
    
    df_chennai = pd.DataFrame({
        "time": data["hourly"]["time"], 
        "temperature": data["hourly"]["temperature_2m"]
    })
    
    df_chennai.to_csv("data/south_india_weather.csv", index=False)
    print("Saved to data/south_india_weather.csv")
    print("Dataset setup complete!")

if __name__ == "__main__":
    download_datasets()
