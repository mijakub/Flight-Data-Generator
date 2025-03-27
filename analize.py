#zaimportowanie modułów
import datetime
import json
import argparse
import csv
import random
import os
import pandas as pd
from sqlalchemy import create_engine

#tworzenie losowych godzin
def getHoursAndDuration():
    durationTime = random.randint(1, 10)
    duration = datetime.datetime.strptime(f"{durationTime:02}:00:00", "%H:%M:%S")
    random_hour = random.randint(0, 23)
    departure = datetime.datetime.strptime(f"{random_hour:02}:00:00", "%H:%M:%S")
    arrival = departure + datetime.timedelta(hours=durationTime)
    return [duration, departure.time(), arrival.time()]

#dodawanie godzin do dataframe
def AddToFrame(iterations):
    frame = pd.DataFrame(columns=["duration", "departure", "arrival"],)
    for i in range(0, iterations):
        timeData = getHoursAndDuration()
        frame.loc[i] = [timeData[0], timeData[1], timeData[2]]
    return frame  

#funkcja main
def main():

    # Tworzenie silnika SQLAlchemy
    engine = create_engine("mysql+mysqlconnector://user:loty@loty.cp6wpeysl1qs.eu-central-1.rds.amazonaws.com:3306/Airport")

    # Sprawdzenie połączenia
    with engine.connect() as connection:
        print("Połączono z bazą MySQL!")

    #utworzenie argumentu
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, nargs="+", help="Ścieżki do plików wejściowych", required=True)
    args = parser.parse_args()

    #odczytanie danych do jednego DataSeries
    #TRZEBA JESZCZE DODAĆ ODCZYTANIE CAŁEGO KATALOGU
    frames = []
    for file in args.input:
        data = pd.read_json(path_or_buf=file)
        timeFrame = AddToFrame(data["flights"].count())
        frame = pd.concat([data["start_date"], pd.json_normalize(data["flights"]), timeFrame], axis=1)
        frames.append(frame)
    mainFrame = pd.concat(frames, axis=0)

    #raporty
    topAirlines = mainFrame.groupby("airline").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
    minAndMaxPrices = mainFrame.agg(min_price=("price", "min"), max_price=("price", "max"))
    avgAvailable = mainFrame.agg(avg_available=("tickets_available", "mean"))
    mostPopularConnections = mainFrame[["origin", "destination"]].value_counts().reset_index(name="count").sort_values(by="count", ascending=False).head()
    mostPopularDestinations = mainFrame.groupby("destination").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
    mostRangeAirlines = mainFrame.groupby("airline")["price"].agg(lambda x: x.max()- x.min()).sort_values(ascending=False).head()
    airlinessAirports = mainFrame.groupby(["airline", "origin"]).size().reset_index(name="count_flights").sort_values(by=["airline", "count_flights"], ascending=[True, False])
    
    sqlFrame = mainFrame[["origin", "destination", "start_date", "tickets_available", "price", "duration", "airline", "departure", "arrival"]]
    print(sqlFrame.query("origin == 'LAX'"))
    sqlFrame.to_sql("Flights", con=engine, if_exists="append", index=False)
#Wywołanie funkcji main
if __name__ == "__main__":
    main()