import requests
import re
import os.path
from datetime import date


class Downloader:
    def __init__(self):
        pass
    
    def download(self):
        
        path = "../data/"

        base = "https://www.divi.de/joomlatools-files/docman-files/divi-intensivregister-tagesreports-csv/DIVI-Intensivregister_"
        times = ["09-15","12-15"]
        
        months = list(range(1,13))
        days = list(range(1,32))
        years = [2020,2021]

        today = date.today()

        firstDate = date(2020,5,1)
        
        not_succesful = []

        for year in years:
          for month in months:
            month_nr = month
            month = str(month).zfill(2)
            for day in days:
        
                try:
                    dateToDownload = date(year,month_nr,day)
            
                    if dateToDownload > today:
                        print("[INFO] {} in future, not downloading".format(dateToDownload))
                        continue

                    if dateToDownload < firstDate:
                         print("[INFO] {} too early, not downloading".format(dateToDownload))
                         continue
                
                except ValueError:
                    print("[ERROR] {}-{}-{} doesn't exist, skipping".format(year,month,day))
                    continue


        
                day = str(day).zfill(2)
        
                downloaded = False
        
                filename = path + "DIVI-Intensivregister_2020-" + month + "-" + day + ".csv"
        
                # if already download, skip
                if os.path.isfile(filename):
                    print("[INFO] Already downloaded: {}".format(filename))
                    continue
            
                for time in times:
                    url = base + str(year) + "-" + month + "-" + day + "_" + time + ".csv"

                    r = requests.get(url) 
                    if r.status_code == 404:
                        output = "-----Not valid: " + month + "-" + day + "_" + time
                        continue
                    else:

                        open(filename, 'wb').write(r.content)
                        output = "[SUCESS] Downloaded " + month + "-" + day + "_" + time
                        print(output)
                        downloaded = True
                        break
                
                if not downloaded:
                    file = month + "-" + day
                    not_succesful.append(file)
                    output = "--------Not succesful: " + month + "-" + day
                    print(output)
                    
