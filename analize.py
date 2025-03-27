#zaimportowanie modułów
import datetime
import json
import argparse
import csv
import random
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

#tworzenie losowych godzin
def getHoursAndDuration():
    durationTime = random.randint(1, 10)
    duration = datetime.datetime.strptime(f"{durationTime:02}:00:00", "%H:%M:%S")
    random_hour = random.randint(0, 23)
    departure = datetime.datetime.strptime(f"{random_hour:02}:00:00", "%H:%M:%S")
    arrival = departure + datetime.timedelta(hours=durationTime)
    return [duration.time(), departure.time(), arrival.time()]

#dodawanie godzin do dataframe
def AddToFrame(iterations):
    frame = pd.DataFrame(columns=["duration", "departure", "arrival"],)
    for i in range(0, iterations):
        timeData = getHoursAndDuration()
        frame.loc[i] = [timeData[0], timeData[1], timeData[2]]
    return frame  

#tworzenie frame
def CreateDataFrame(arguments):
    if os.path.isdir(arguments[0]):
        files = [os.path.join(arguments[0], f) for f in os.listdir(arguments[0]) if f.endswith('.json')]
        frames = []
        for file in files:
            data = pd.read_json(path_or_buf=file)
            timeFrame = AddToFrame(data["flights"].count())
            frame = pd.concat([data["start_date"], pd.json_normalize(data["flights"]), timeFrame], axis=1)
            frames.append(frame)
        mainFrame = pd.concat(frames, axis=0)
        return mainFrame 
    elif isinstance(arguments, list) and all(os.path.isfile(arg) for arg in arguments):
        frames = []
        for file in arguments:
            data = pd.read_json(path_or_buf=file)
            timeFrame = AddToFrame(data["flights"].count())
            frame = pd.concat([data["start_date"], pd.json_normalize(data["flights"]), timeFrame], axis=1)
            frames.append(frame)
        mainFrame = pd.concat(frames, axis=0)
        return mainFrame
    else:
        return "Niepoprawna ścieżka. Spróbuj ponownie :)"

#funkcja main
def main():

    try:

        #dane do połączenia z bazą danych
        load_dotenv()
        user = os.environ.get('DB_USER')
        password = os.environ.get("DB_PASSWORD")
        host = os.environ.get("DB_HOST")
        port = os.environ.get("DB_PORT")
        dbname = os.environ.get("DB_NAME")
        
        #połączenie z bazą danych
        engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}")

        #sprawdzenie połączenia
        with engine.connect() as connection:
            print("Połączono z bazą MySQL!")

        #utworzenie argumentu
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", type=str, nargs="+", help="Ścieżki do plików wejściowych", required=True)
        args = parser.parse_args()

        #odczytanie danych do jednego DataSeries lub wywalenie błędu
        mainFrame = CreateDataFrame(args.input)
        if isinstance(mainFrame, str):
            print(mainFrame)
            return
        
        #raporty
        topAirlines = mainFrame.groupby("airline").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
        minAndMaxPrices = mainFrame.agg(min_price=("price", "min"), max_price=("price", "max"))
        avgAvailable = mainFrame.agg(avg_available=("tickets_available", "mean"))
        mostPopularConnections = mainFrame[["origin", "destination"]].value_counts().reset_index(name="count").sort_values(by="count", ascending=False).head()
        mostPopularDestinations = mainFrame.groupby("destination").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
        mostRangeAirlines = mainFrame.groupby("airline")["price"].agg(lambda x: x.max()- x.min()).sort_values(ascending=False).head()
        airlinessAirports = mainFrame.groupby(["airline", "origin"]).size().reset_index(name="count_flights").sort_values(by=["airline", "count_flights"], ascending=[True, False])
        
        #przygotowanie DataFrame o strukturze jak tabelka w sql
        sqlFrame = mainFrame[["origin", "destination", "start_date", "tickets_available", "price", "duration", "airline", "departure", "arrival"]]
        
        #dodanie do bazy danych
        #sqlFrame.to_sql("Flights", con=engine, if_exists="append", index=False)
        print(sqlFrame)

        #generowanie raportu
        with open('raport.txt', 'w') as file:
            file.write(f"Top 5 linii lotniczych pod wzgledem liczby lotow:\n{topAirlines}\n\n")
            file.write(f"Najpopularniejsze kierunki lotów (najczesciej wystepujace polaczenia):\n{mostPopularConnections}\n\n")
            file.write(f"Maksymalna i minimalna cena biletu w zestawie danych:\n{minAndMaxPrices}\n\n")
            file.write(f"Srednia liczba dostepnych miejsc na lot:\n{avgAvailable}\n\n")
            file.write(f"Linie lotnicze z najwiekszym rozrzutem cenowym biletow:\n{mostRangeAirlines}\n\n")
            file.write(f"Najpopularniejsze kierunki docelowe:\n{mostPopularDestinations}\n\n")
            file.write(f"Lotniska pogrupowane dla danej linii:\n{airlinessAirports}\n\n")
            file.write(f"\n\nLiczba przetworzonych rekordow: {sqlFrame["origin"].count()}\nDodano dane do bazy!")

    except Exception as e:

        #dodanie błędów do raportu
        with open('raport.txt', 'w') as file:
            file.write(f"Błąd: {str(e)}\n")

#Wywołanie funkcji main
if __name__ == "__main__":
    main()