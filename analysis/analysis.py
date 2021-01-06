from Helper import Downloader

# import constants for signal-cli
import constant


import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns
sns.set()

from subprocess import call


def datenstand(row):
    datenstand = row["daten_stand"]
    if type(datenstand) == str:
        return row["daten_stand"]
    else:
        splitted = row["filename"].split("_")[-1]
        point_splitted = splitted.split(".")[0]
        return point_splitted

def sendMessage(sender, recipient, message = ".", attachment = None):
 
    command = "/usr/local/bin/signal-cli -u " + sender + " send -m \"" + message + "\" " + recipient
    
    if attachment != None:
        command = command + " -a \"" + attachment + "\""
    
    call(command, shell=True)

def sendMessageToGroup(sender, groupId, message = ".", attachment = None):

    
    command = "/usr/local/bin/signal-cli -u " + sender + " send " +  "-g " + groupId + " -m \"" + message + "\""
    
    if attachment != None:
        command = command + " -a \"" + attachment + "\""
    
    call(command, shell=True)
    

sender = constant.SENDER
recipient = constant.RECIPIENT
corona_group = constant.CORONA_GROUP
   
# download new data
downloader = Downloader()
downloader.download()


files = glob.glob("../data/*.csv")
list_of_dfs = [pd.read_csv(file,dtype={"gemeindeschluessel": str}) for file in files]


for dataframe, filename in zip(list_of_dfs, files):
    dataframe["filename"] = filename.split("/")[-1]


df = pd.concat(list_of_dfs, ignore_index=True)

df = df.drop("Unnamed: 0",axis=1)
df = df.drop("kreis",axis=1)
df = df.drop("faelle_covid_aktuell_im_bundesland",axis=1)


df["daten_stand"] = df.apply(lambda x: datenstand(x), axis=1)

df["daten_stand"] = pd.to_datetime(df["daten_stand"])


# droppe 24.04. und 25.04, da diese keine Corona-Fallzahlen enthalten
df = df[~df["faelle_covid_aktuell_beatmet"].isna()]
df = df[~df["faelle_covid_aktuell"].isna()]


df["betten_gesamt"] = df["betten_frei"] + df["betten_belegt"]
df["anteil_belegt"] = df["betten_belegt"] / df["betten_gesamt"]


bundeslaender = pd.read_csv("../master_data/bundeslaender.csv")


df = df.merge(bundeslaender,how="left",left_on="bundesland",right_on = "ID")


gemeinden = pd.read_pickle("../master_data/gemeindeschluessel")

df = df.merge(gemeinden, how="left", on="gemeindeschluessel")

tagessicht = df.groupby("daten_stand").sum().reset_index().drop("anteil_belegt",axis=1)

tagessicht = tagessicht.drop(["bundesland","anzahl_meldebereiche"],axis=1)


tagessicht["wochentag"] = tagessicht["daten_stand"].dt.day_name()
tagessicht["woche"] = tagessicht["daten_stand"].dt.isocalendar().week


tagessicht["anteil_belegt"] = tagessicht["betten_belegt"] / tagessicht["betten_gesamt"]

tagessicht["anteil_beatmet"] = tagessicht["faelle_covid_aktuell_beatmet"] / tagessicht["faelle_covid_aktuell"]

tagessicht["anteil_corona_patienten"] = tagessicht["faelle_covid_aktuell"] / tagessicht["betten_belegt"]


daten_stand = tagessicht.iloc[tagessicht["daten_stand"].argmax()]["daten_stand"]
patienten = int(tagessicht.iloc[tagessicht["daten_stand"].argmax()]["faelle_covid_aktuell"])
beatmet = int(tagessicht.iloc[tagessicht["daten_stand"].argmax()]["faelle_covid_aktuell_beatmet"])

anteil_belegt = tagessicht.iloc[tagessicht["daten_stand"].argmax()]["anteil_belegt"]
anteil_belegt = round(anteil_belegt * 100,2)

anteil_beatmet = tagessicht.iloc[tagessicht["daten_stand"].argmax()]["anteil_beatmet"]
anteil_beatmet = round(anteil_beatmet * 100,2)

anteil_corona = tagessicht.iloc[tagessicht["daten_stand"].argmax()]["anteil_corona_patienten"]
anteil_corona = round(anteil_corona * 100,2)
delta_corona = tagessicht["anteil_corona_patienten"].pct_change().iloc[-1]
delta_corona = round(delta_corona * 100,3)
sign_corona = "+" if delta_corona > 0 else ""

message = """Datenstand: {}

ITS-Patienten: {}
beatmet: {}
Anteil beatmet:  {}%

Belegte Betten insgesamt: {}%

Anteil Corona-Patienten an belegten Betten: {}%
Veränderung zum Vortag: {}{}%
""".format(daten_stand,patienten,beatmet,anteil_beatmet,anteil_belegt, anteil_corona,sign_corona,delta_corona)

sendMessageToGroup(sender, corona_group, message)


### Gesamtsicht Patienten vs beatmet
plt.figure(figsize=(17,6))
plot = tagessicht[["daten_stand","faelle_covid_aktuell","faelle_covid_aktuell_beatmet"]].set_index("daten_stand")
g = sns.lineplot(data=plot)
g.set_title("Patienten auf ITS vs. beatmetete Patienten")
plt.savefig("patienten.png")

change_patienten = int(tagessicht["faelle_covid_aktuell"].diff().iloc[-1])
change_patienten_beatmet = int(tagessicht["faelle_covid_aktuell_beatmet"].diff().iloc[-1])

sign_pat = "+" if change_patienten > 0 else ""
sign_beat = "+" if change_patienten_beatmet > 0 else ""

message = """Patienten-Statistik

Änderungen zum Vortag:
Patienten auf ITS: {sign_pat}{change_patienten}
Beatmetete Patienten: {sign_beat}{change_pat_beatmet}
""".format(sign_pat=sign_pat,change_patienten=change_patienten, sign_beat=sign_beat, change_pat_beatmet=change_patienten_beatmet)

sendMessageToGroup(sender, corona_group, message,"patienten.png")

## Anteil belegter Betten
plt.figure(figsize=(17,6))
g = sns.lineplot(x="daten_stand",y="anteil_belegt",data=tagessicht)
g.axhline(1,color="red")
g.set_title("Zeitreihe: Anteil belegter Betten")
g.set_ylim(0,1.2)
g.set_yticklabels(['{:,.0%}'.format(x) for x in g.get_yticks()])
plt.savefig("anteil_belegt.png")

change_belegt = tagessicht["anteil_belegt"].pct_change().iloc[-1]
change_belegt = round(change_belegt,3)

sign = "+" if change_belegt > 0 else ""

#print(anteil_belegt)
message = """Betten-Belegung

Aktuell belegt: {anteil_belegt}%
Veränderung zum Vortag: {sign}{change_belegt}%
""".format(anteil_belegt=anteil_belegt, sign=sign, change_belegt=change_belegt)

sendMessageToGroup(sender, corona_group, message,"anteil_belegt.png")

### Gesamtauslastung vs. Anteil Corona-Patienten und Anteil beatmet
plt.figure(figsize=(17,6))
plot = tagessicht[["daten_stand","anteil_belegt","anteil_corona_patienten","anteil_beatmet"]].set_index("daten_stand")
g = sns.lineplot(data=plot)
g.set_ylim(0,1)
g.set_yticklabels(['{:,.0%}'.format(x) for x in g.get_yticks()])
g.set_title("Gesamtauslastung vs. Anteil Corona-Patienten und Anteil beatmet")
plt.savefig("anteile_auslastung_corona.png")

message = "Gesamtauslastung vs. Anteil Corona-Patienten (gesamt vs. beatmet)"
sendMessageToGroup(sender, corona_group, message,"anteile_auslastung_corona.png")

