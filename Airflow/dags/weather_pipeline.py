from airflow.decorators import dag, task
from datetime import datetime
import requests
import pandas as pd
import os

CITIES = {
    "Paris": {"latitude": 48.85, "longitude": 2.35},
    "London": {"latitude": 51.51, "longitude": -0.13},
    "Berlin": {"latitude": 52.52, "longitude": 13.41}
}


@dag(
    dag_id="daily_weather_pipeline",
    start_date=datetime(2025, 7, 1),
    schedule="0 8 * * *",
    catchup=False,
    tags=["weather", "etl"],
    description="Daily weather data ETL pipeline using Open-Meteo API"
)
def weather_etl_pipeline():
    @task
    def extract_weather_data():
        """Extract weather data from Open-Meteo API for 3 cities"""
        all_weather_data = []

        for city_name, coordinates in CITIES.items():
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={coordinates['latitude']}"
                f"&longitude={coordinates['longitude']}"
                f"&current_weather=true"
            )

            response = requests.get(url)
            data = response.json()
            current_weather = data['current_weather']

            weather_record = {
                'city': city_name,
                'temperature': current_weather['temperature'],
                'windspeed': current_weather['windspeed'],
                'weather_code': current_weather['weathercode']
            }

            all_weather_data.append(weather_record)
            print(f"Extracted data for {city_name}: {weather_record}")

        return all_weather_data

    @task
    def transform_weather_data(**context):
        """Transform the weather data and add timestamp"""
        raw_data = context['task_instance'].xcom_pull(task_ids='extract_weather_data')

        for record in raw_data:
            record['timestamp'] = datetime.now()

        print(f"Transformed {len(raw_data)} records with timestamps")
        return raw_data

    @task
    def load_weather_data(**context):
        """Load data to CSV file with idempotency"""
        transformed_data = context['task_instance'].xcom_pull(task_ids='transform_weather_data')

        df = pd.DataFrame(transformed_data)

        data_dir = "/opt/airflow/data"
        os.makedirs(data_dir, exist_ok=True)
        csv_file = os.path.join(data_dir, "weather_data.csv")

        if os.path.exists(csv_file):
            existing_df = pd.read_csv(csv_file)
            today = datetime.now().date()

            existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
            existing_today = existing_df[
                existing_df['timestamp'].dt.date == today
                ]

            if existing_today.empty:
                df.to_csv(csv_file, mode='a', header=False, index=False)
                print(f"Appended {len(df)} new records to existing file")
            else:
                print("Data already exists for today - skipped to avoid duplicates")
                return "Data already exists for today - skipped to avoid duplicates"
        else:
            df.to_csv(csv_file, index=False)
            print(f"Created new file with {len(df)} records")

        return f"Successfully loaded {len(df)} records"

    extract_weather_data() >> transform_weather_data() >> load_weather_data()


dag = weather_etl_pipeline()