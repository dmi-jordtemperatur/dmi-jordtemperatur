# DMI jordtemperatur – 10 cm

GitHub Actions henter aktuelle `temp_soil`-observationer fra DMI hver time og skriver `jordtemperatur.csv`.

Datawrapper: Opret et **Symbol map**, vælg **Link external data**, og brug den offentlige raw-CSV-URL:
`https://raw.githubusercontent.com/DIT_BRUGERNAVN/dmi-jordtemperatur/main/jordtemperatur.csv`

Vælg **Serve data file directly** for at undgå Datawrappers 30-dages grænse. Kontrollér, at Datawrapper accepterer URL'en og dens CORS-headere. Hvis ikke, skal CSV'en hostes på en HTTPS-server med CORS (fx en korrekt konfigureret statisk hostingtjeneste).

Bemærk: DMI's observationsdata er ikke kvalitetskontrollerede. Scriptet tager den nyeste observation per station, højst 2 timer gammel. Ved fejl bevares den eksisterende CSV, så kontroller workflowets status ved mistanke om forældede data.
