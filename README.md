# Digital kommunikasjon

Digital kommunikasjon handler om å sende informasjon fra én enhet til en annen. Informasjonen kan være tekst, lyd, bilde, video eller sensordata. Hvordan informasjonen sendes avhenger blant annet av datatype, avstand, hastighet, sikkerhet og hvor mye støy det er i omgivelsene.

I dette prosjektet skal dere gjøre det på en litt upraktisk, men lærerik måte: Dere skal sende digitale bits som lyd. En ESP32 spiller av to ulike frekvenser gjennom en høyttaler, og en Raspberry Pi bruker mikrofon til å finne ut hva som ble sendt.

Metoden kalles **FSK**, eller [Frequency Shift Keying](https://en.wikipedia.org/wiki/Frequency-shift_keying). Ideen er enkel: en frekvens betyr `0`, og en annen frekvens betyr `1`. Selv om dette prosjektet bruker lyd, er prinsippet det samme som i mange ekte kommunikasjonssystemer. Bluetooth LE bruker en variant kalt **GFSK**, eller **Gaussian Frequency Shift Keying**.

## Kode

Dere får litt hjelp med å sette i gang.

- `adc_sampler.c` tar opp data fra ADC-en og skriver det rett til minne.
- `raspi_import.py` konverterer ADC-dataen til et array.
- `fsk_decoder.py` tar arrayet og ved hjelp av litt fiffig signalbehandling gir ut en liste med nuller og enere.

I `main.py` er det et lite eksempel på hvordan disse filene kan brukes. Hvis dere holder pekeren over `fsk_decoder()` vil det dukke opp en kort forklaring av funksjonen.

For at mottaker skal vite hvor i opptaket meldingen er, så er det greit med et signal som signaliserer dette. Det viser seg at noen slike signal er bedre egnet enn andre. Mine tips er å se på [Barker code](https://en.wikipedia.org/wiki/Barker_code) eller [MLS](https://en.wikipedia.org/wiki/Maximum_length_sequence).

Valg av frekvenser vil ha en stor påvirkning på hvor godt kommunikasjonssystemet deres fungerer. Velg med omhu! Unngå å velg de samme frekvensene som de rundt deg. Hvis dere trenger inspirasjon, kan dere se på den gamle standarden [Bell 202](https://en.wikipedia.org/wiki/Bell_202).

## Raspberry Pi oppsett
1. Last ned Raspberry Pi Imager 
3. Sett SD-kortet inn i SD-kortleseren
5. Klikk på "DEVICE" og velg "Raspberry Pi 3"
6. Klikk på "OS" og velg "Raspberry pi OS (32/bit)"
7. Klikk på "STORAGE", og velg det SD-kortet dere satte inn.
8. På "Customistation" velg følgende:

   1. Sett hostname til «elsys"gruppenummer"», eksempel: elsys14
   2. Localisation:
      - Time zone: Europe/Oslo
      - Keyboard layout: NO
   3. Choose username:
      - Username: pi
      - Password: 123
   4. Choose Wi-Fi:
      - Bruk delt nett fra mobilene deres.
   5. SSH authentication: 
      - Aktiver SSH 
      - Velg "Use password authentication"
   6. Raspberry Pi Connect:
      - NEXT
   7. WRITE

For å koble til Raspberry Pi-en, åpne terminalen og skriv:
  ```bash
  ssh pi@<hostname>.local
  ```

Om dere ikke får koblet til så se på feilsøkingstipsene nedenfor:
* Prøv å bruke IPv4-adressen til PI-en istedenfor ```<hostname>.local```. Den finner dere vanligvis i nettverksdelingsinnstillingene på mobilen og har på formatet ```<xxx.xxx.xxx.xxx>```, hvor x er tall. Kommandoen blir da f.eks. ```ssh pi@192.168.195.162```.
* Det kan ta litt tid før Pi-en starter, så om den ikke finner Pi-en med en gang, vent noen minutter og prøv igjen. Dere kan også trykke piltast opp på tastaturet for å bruke den siste kommandoen dere brukte.
* Dobbeltsjekk også at det delte nettet opererer på 2.4GHz. På iPhone gjøres dette ved å gå inn i "settings"->"personal hotspot", og skru på "maximise compatibility".
* Hvis dere har koblet dere av internettet og på et annet en eller annen gang i løpet av dagen så kan det hende programmet ikke gjenkjenner igjen ip-adressen. Ta å skriv på SD kortet igjen, men denne gangen endre brukernavnet til noe annet enn gruppenavnet. Brukernavnet kan dermed ikke være det samme som det noen andre har brukt før.

Tips til å skrive i terminalen:
- Grunnleggende terminalkommandoer for navigering:
  - **`cd <directory>`**: Bytter katalog. Denne kommandoen lar deg navigere mellom forskjellige mapper på datamaskinen din. For eksempel, `cd Documents` vil navigere til Documents-mappen fra din nåværende lokasjon.
  - **`ls`**: List opp innholdet i den nåværende mappen. Denne kommandoen viser alle filer og mapper i den nåværende mappen, hvor mapper vil dukke opp i blått.
  - **`cd ..`**: Gå opp ett nivå i mappestrukturen. Dette tar deg tilbake til mappen som inneholder den nåværende mappen.

## Installere pigpio

For å kommunisere med ADC-en bruker vi et C-bibliotek som heter **pigpio**. Dette biblioteket gjør det mulig å styre GPIO-pinnene på Raspberry Pi på lavt nivå, og brukes her for å sample data fra ADC-en med DMA.

Dere kan laste ned `pigpio` direkte med:

```bash
wget https://github.com/joan2937/pigpio/archive/master.zip
```

Pakk deretter ut filen:

```bash
unzip master.zip
```

Gå inn i mappen som ble laget:

```bash
cd pigpio-master
```

Kompiler biblioteket:

```bash
make
```

Installer biblioteket:

```bash
sudo make install
```

Kommandoen `make` bruker en fil som heter `Makefile` til å finne ut hvordan programmet skal kompileres. Kommandoen `sudo make install` installerer biblioteket slik at det kan brukes av andre programmer på Raspberry Pi-en.

## Filoverføring med SFTP

For å flytte filer mellom laptopen og Raspberry Pi-en kan dere bruke **SFTP**. SFTP står for **SSH File Transfer Protocol**, og bruker samme tilkobling som SSH. Det betyr at filoverføringen er kryptert og sikker.

Dere kan bruke disse programmene:

- **Windows/macOS:** Cyberduck
- **Linux:** FileZilla

Når dere åpner SFTP-programmet, fyller dere inn:

- Hostname eller IP-adresse til Raspberry Pi-en
- Brukernavn
- Passord
- Port: `22`

Port `22` er standardporten for SSH.

Når dere er koblet til, kan dere dra filer mellom laptopen og Raspberry Pi-en. Hjemmemappen til brukeren på Raspberry Pi ligger her:

```bash
/home/pi/
````

## Kjøre kode på Raspberry Pi

For å kjøre kode på raspberry pi må dere først skrive i terminalen:

```bash
make
```

og så:

```bash
sudo python3 main.py 
```
