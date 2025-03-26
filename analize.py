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
    parser.add_argument('--input', type=str, nargs="+", help='Ścieżki do plików wejściowych', required=True)
    args = parser.parse_args()

    frames = []
    for file in args.input:
        data = pd.read_json(path_or_buf=file)
        frames.append(data)
    mainFrame = pd.concat(frames, axis=0)
    print(mainFrame)
    
#Wywołanie funkcji main
if __name__ == "__main__":
    main()