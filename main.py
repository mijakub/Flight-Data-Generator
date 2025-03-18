#zaimportowanie modułów
import datetime
import json
import argparse
import csv
import random
import os

#funkcja wyszukująca linię lotniczą, w zależności od kraju lotniska wylotu
def findAirline(country, airlines):
    searchedAirline = ""
    airlineCode = ""
    for airline in airlines:
        if airline["Kraj pochodzenia"] == country:
            searchedAirline = airline["Nazwa linii lotniczej"]
            airlineCode = airline["Kod IATA"]
            return (searchedAirline, airlineCode)
            
#funkcja wyszukująca kraj, w zależności od podanych kodów lotniska
def findCountry(apcode, airports):
    country = ""
    for airport in airports:
        if airport["Kod IATA"] == apcode:
            country = airport["Kraj"]
            return country
            
#funkcja wyszukująca kontynent, w zależności od podanych kodów lotniska
def findContinent(apcode, airports):
    continent = ""
    for airport in airports:
        if airport["Kod IATA"] == apcode:
            continent = airport["Kontynent"]
            return continent

#funkcja main
def main():

    #utworzenie argumentów
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_records', type=int, help='Liczba generowanych rekordów', required=True)
    parser.add_argument('--date', type=str, help='Data wygenerowania cennika', required=True)
    parser.add_argument('--filter_continent', type=str, help='Ograniczenie lotów do wybranego kontynentu')
    parser.add_argument('--filter_origin', type=str, nargs="+", help='Ograniczenie lotnisk wylotu do konkretnej listy lotnisk')
    parser.add_argument('--filter_destination', type=str, nargs="+", help='Ograniczenie lotnisk docelowych do konkretnej listy lotnisk')
    args = parser.parse_args()

    #sprawdzenie poprawności wpisanych argumentów 
    if args.date != datetime.datetime.strptime(args.date, "%Y-%m-%d").date().strftime("%Y-%m-%d"):
        print("Wpisz poprawną datę!")
        return
    
    #odczytanie pliku z lotniskami i uporządkowanie danych w liście słowników
    airportsDicts = []
    with open(os.path.join("data", "airports.csv"), newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for airport in reader:
            airportDict = dict()
            for index in range(0, len(airport)):
                airportDict[header[index]] = airport[index]
            airportsDicts.append(airportDict)

    #odczytanie pliku z liniami lotniczymi i uporządkowanie danych w liście słowników
    airlinesDicts = []
    with open(os.path.join("data", "airlines.csv"), newline="", encoding="utf-8") as csvfile:
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

        #wylosowanie losowych liczb i lotnisk, w zależności od podanych filtrów
        if args.filter_origin:
            originRandom = random.randint(0, len(args.filter_origin)-1)
            originAP = args.filter_origin[originRandom]
            airlineInfo = findAirline(findCountry(originAP, airportsDicts), airlinesDicts)
        else:
            originRandom = random.randint(0, len(airportsDicts)-1)
            originAP = airportsDicts[originRandom]["Kod IATA"]
            airlineInfo = findAirline(airportsDicts[originRandom]["Kraj"], airlinesDicts)
        if args.filter_destination:
            destinationRandom = random.randint(0, len(args.filter_destination)-1)
            destinationAP = args.filter_destination[destinationRandom]
        else:
            destinationRandom = random.randint(0, len(airportsDicts)-1)
            destinationAP = airportsDicts[destinationRandom]["Kod IATA"]

        #obsługa przypadków, gdy pętla musi wykonać się ponownie
        if originAP == destinationAP:
            continue

        if args.filter_continent:
            if (findContinent(originAP, airportsDicts) != args.filter_continent) | (findContinent(destinationAP, airportsDicts) != args.filter_continent):
                continue

        if airlineInfo == None:
            continue
        
        #ustalenie przelicznika ceny i długości trasy w zależności od kontynentów
        if airportsDicts[destinationRandom]["Kontynent"] == airportsDicts[originRandom]["Kontynent"]:
            distance = random.randint(0, 10000)
            distancePercent = 0.5
        else:
            distance = random.randint(0, 200000)
            distancePercent = 1

        #przetwarzanie informacji o lotach
        flightNumber = airlineInfo[1] + str(random.randint(1000, 9999))
        classes = ["Economy", "Premium", "Business", "First"]
        flightClass = classes[random.randint(0, 3)]

        #ustalenie ceny i dostępności biletów na podstawie wylosowanej klasy lotu
        if flightClass == "Economy":
            price = random.randint(50, 2000) * distancePercent
            ticketsAvailable = random.randint(0, 120)
        elif flightClass == "Premium":
            price = random.randint(2000, 5000) * distancePercent
            ticketsAvailable = random.randint(0, 80)
        elif flightClass == "Business":
            price = random.randint(5000, 20000) * distancePercent
            ticketsAvailable = random.randint(0, 40)
        elif flightClass == "First":
            price = random.randint(20000, 100000) * distancePercent
            ticketsAvailable = random.randint(0, 20)

        #dodanie słownika do listy słowników
        flightsList.append({"flight_number": flightNumber, "departure_airport" : originAP, "arrival_airport" : destinationAP, "airline" : airlineInfo[0], "price": float(price), "available_tickets": ticketsAvailable, "class": flightClass, "distance_km" : distance})
    output["flights"] = flightsList
    
    #zapis wyniku do pliku JSON
    with open(os.path.join("data", "output.json"), "w") as file:
        json.dump(output, file, indent=4)

if __name__ == "__main__":
    main()