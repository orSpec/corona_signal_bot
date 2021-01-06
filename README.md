
# Corona Signal Bot
Mithilfe des Codes können die tagesaktuellen Reports des [DIVI-Intensivregisters](https://www.divi.de/register/tagesreport) heruntergeladen werden. Basierend auf den aktuellen und zurückliegenden Reports werden Auswertungen durchgeführt, z.B.

 - Anzahl der Patienten auf der Intensivstation und beatmetete Patienten:
<img src="https://user-images.githubusercontent.com/59450716/103759097-73a92e00-5013-11eb-99de-91affd22bc13.png" width="1200">

 - Gesamtauslastung des Systems, Anteil der Corona-Patienten, Anteil der beatmeten Corona-Patienten
  <img src="https://user-images.githubusercontent.com/59450716/103759256-bcf97d80-5013-11eb-96e2-326dbf9c3f19.png" width="1200">

Die Auswertungen können dann mithilfe von [signal-cli](https://github.com/AsamK/signal-cli), einem Kommandozeilen-Interface für die Bibliothek [signal-service-java](https://github.com/signalapp/libsignal-service-java) (Java-Bibliothek für die Kommunikation mit dem Messengerdienst Signal) zu einem einzelnen Empfänger oder an eine Signal-Gruppe geschickt werden.

Unter Linux kann z.B. mithilfe von cron eingerichtet werden, dass das Python-Programm jeden Tag zu einer bestimmten Uhrzeit ausgeführt wird und aktuelle Auswertungen an die Empfänger pusht:
Cron Expression für eine Ausführung jeden Tag um 13 Uhr Systemzeit:
`0 13 * * * python /path/to/analysis.py`

### Module / Technologien
 - pandas
 - numpy
 - matplotlib
 - seaborn
 - [signal-cli](https://github.com/AsamK/signal-cli) (auf ausführendem System installiert und mit registrierter Rufnummer zum Versenden von Nachrichten)

### Daten
 - tagesaktuelle Reports von [DIVI-Intensivregister](https://www.divi.de/register/tagesreport)
 - Gemeindeverzeichnis von [Github/digineo](https://github.com/digineo/gemeindeverzeichnis)

