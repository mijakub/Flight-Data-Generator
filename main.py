def main():
    #zaimportowanie modułów
    import datetime
    import json
    import argparse
    import csv
    import random

    #utworzenie argumentów
    parser = argparse.ArgumentParser(description="A simple example using argparse.")
    parser.add_argument('--num_records', type=int, help='Liczba generowanych rekordów', required=True)
    parser.add_argument('--date', type=str, help='Data wygenerowania cennika', required=True)
    parser.add_argument('--filter_continent', type=str, help='Ograniczenie lotów do wybranego kontynentu')
    parser.add_argument('--filter_origin', type=str, help='Ograniczenie lotnisk wylotu do konkretnej listy lotnisk')
    parser.add_argument('--filter_destintion', type=str, help='Ograniczenie lotnisk docelowych do konkretnej listy lotnisk')
    args = parser.parse_args()

    #odczytanie pliku i uporządkowanie danych w liście słowników
    airportsDicts = []
    with open("C:\\Users\\krzys\\Desktop\\Projektt\\Flight-Data-Generator\\data\\airports.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for airport in reader:
            airportDict = dict()
            for index in range(0, len(airport)):
                airportDict[header[index]] = airport[index]
            airportsDicts.append(airportDict)

    #próby losowania lotnisk
    origin = random.randint(0, len(airportsDicts)-1)
    destination = random.randint(0, len(airportsDicts)-1)
    print("%s -> %s" % (airportsDicts[origin]["Kod IATA"], airportsDicts[destination]["Kod IATA"]))
    print(datetime.date.today())
    print(args.num_records, args.date)
main()