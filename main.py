def main():

    #Funkcja wyszukująca linię lotniczą, w zależności od lotniska wylotu
    def findAirline(country, airlines):
        searchedAirline = ""
        airlineCode = ""
        for airline in airlines:
            if airline["Kraj pochodzenia"] == country:
                searchedAirline = airline["Nazwa linii lotniczej"]
                airlineCode = airline["Kod IATA"]
                return (searchedAirline, airlineCode)
    
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

    #odczytanie pliku z lotniskami i uporządkowanie danych w liście słowników
    airportsDicts = []
    with open("C:\\Users\\krzys\\Desktop\\Projektt\\Flight-Data-Generator\\data\\airports.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for airport in reader:
            airportDict = dict()
            for index in range(0, len(airport)):
                airportDict[header[index]] = airport[index]
            airportsDicts.append(airportDict)

    #odczytanie pliku z liniami lotniczymi i uporządkowanie danych w liście słowników
    airlinesDicts = []
    with open("C:\\Users\\krzys\\Desktop\\Projektt\\Flight-Data-Generator\\data\\airlines.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for airline in reader:
            airlineDict = dict()
            for index in range(0, len(airline)):
                airlineDict[header[index]] = airline[index]
            airlinesDicts.append(airlineDict)

    #przetwarzanie danych do wynikowego słownika
    output = {"date" : args.date}
    flightsList = []
    while len(flightsList) != args.num_records:

        #wylosowanie losowych liczb
        originRandom = random.randint(0, len(airportsDicts)-1)
        destinationRandom = random.randint(0, len(airportsDicts)-1)

        #przetwarzanie informacji o lotach
        originAP = airportsDicts[originRandom]["Kod IATA"]
        destinationAP = airportsDicts[destinationRandom]["Kod IATA"]
        airlineInfo = findAirline(airportsDicts[originRandom]["Kraj"], airlinesDicts)

        #Ponowny przelot pętli w sytuacji, gdy nie znaleziono linii z danego kraju
        if airlineInfo == None:
            continue
        
        flightNumber = airlineInfo[1] + str(random.randint(1000, 9999))
        
        #dodanie słownika do listy słowników
        flightsList.append({"flight_number": flightNumber, "departure_airport" : originAP, "arrival_airport" : destinationAP, "airline" : airlineInfo[0]})
    output["flights"] = flightsList
    print(output)
main()
