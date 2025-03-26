#zaimportowanie modułów
import datetime
import json
import argparse
import csv
import random
import os
import pandas as pd

#funkcja main
def main():

    #utworzenie argumentu
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, nargs="+", help="Ścieżki do plików wejściowych", required=True)
    args = parser.parse_args()

    #odczytanie danych do jednego DataSeries
    #TRZEBA JESZCZE DODAĆ ODCZYTANIE CAŁEGO KATALOGU
    frames = []
    for file in args.input:
        data = pd.read_json(path_or_buf=file)
        frame = pd.concat([data["date"], pd.json_normalize(data["flights"])], axis=1)
        frames.append(frame)
    mainFrame = pd.concat(frames, axis=0)

    #raporty
    topAirlines = mainFrame.groupby("airline").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
    minAndMaxPrices = mainFrame.agg(min_price=("price", "min"), max_price=("price", "max"))
    avgAvailable = mainFrame.agg(avg_available=("available_tickets", "mean"))
    mostPopularConnections = mainFrame[["departure_airport", "arrival_airport"]].value_counts().reset_index(name="count").sort_values(by="count", ascending=False).head()
    mostPopularDestinations = mainFrame.groupby("arrival_airport").size().reset_index(name="count").sort_values(by="count", ascending=False).head()
    mostRangeAirlines = mainFrame.groupby("airline")["price"].agg(lambda x: x.max()- x.min()).sort_values(ascending=False).head()
    airlinessAirports = mainFrame.groupby(["airline", "departure_airport"]).size().reset_index(name="count_flights").sort_values(by=["airline", "count_flights"], ascending=[True, False])
    
#Wywołanie funkcji main
if __name__ == "__main__":
    main()