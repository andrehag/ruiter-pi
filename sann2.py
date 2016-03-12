#!/usr/bin/python
import sys
import time, datetime
import requests, json, math
LCD = 1
if LCD == 0:
  import urllib.request
else:
  import urllib
from time import sleep
if LCD == 1:
  from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate


# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
if LCD == 1:
  lcd = Adafruit_CharLCDPlate()

    
def MakeLine(aTime, aStationName):
	d2_ts = time.mktime(t_now.timetuple())	 
	#Naa kan finne ut hvor mange sekunder det er igjen
	seconds_left = int(aTime-d2_ts)
	
	#Her konverterer vi til minutter
	time_left_str = " " + str(int(seconds_left/60)) + " min"
	  
	#Vi har totalt 16 tegn paa skjermen. Her regner vi ut hvor mye plass vi har til destinasjonsnavnet
	dest_len = 16 - len(time_left_str)- 1

	#Todo: troor kanskje jeg regnet en plass feil
	#Fjern tegn det ikke er plass til
	aStationName.ljust(16) 
	aStationName = aStationName[:dest_len]

	#Todo: gjore om minimum tid til variabel?
	#Setter kun opp dersom over 2min gjenstar 
	if seconds_left > 120: 
	  Line = aStationName + " " + time_left_str
	else:
	  Line = ""

	return Line
    
def GetTime(Index):
    destinasjon = data[Index]["MonitoredVehicleJourney"]["DestinationName"]
    #Todo: Sjekk om dette er riktig felt. Vi ma skille paa sanntid og rutetid
    ankomst = data[Index]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"]

    #Her gjoer vi om ankomsttiden fra tekst til et tidsobjekt
    t_ankomst = datetime.datetime.strptime(ankomst[:19], "%Y-%m-%dT%H:%M:%S")
    print( str(t_ankomst))
     
    #Her henter vi tiden akkurat naa
    t_now = datetime.datetime.now()
     
    #Saa gjoer vi om disse tidsobjektene til et standardformat
    return time.mktime(t_ankomst.timetuple())
	
def GetInfo(StationID): 
  #Holdeplass nr 3012020 er Vollebekk
  ruterapi_url = "http://reisapi.ruter.no/StopVisit/GetDepartures/" + str(StationID)
   #Her henter vi sanntidsdata for holdeplassen
  if LCD == 0:
    response = urllib.request.urlopen(ruterapi_url)
    content = response.read()
    data = json.loads(content.decode("utf8"))
  else:
    response = urllib.urlopen(ruterapi_url)
    content = response.read()
    data = json.loads(content)
  return data

def WriteInfo(data, Direction, StationName, Counter):    
  i = 0
  linje1 = ""
  linje2 = ""
#  print (str(len(data)))
#  tall = len(data)
  while (i < len(data)) and (linje2 == ""):
#    print(str(i))
    direct = data[i]["MonitoredVehicleJourney"]["DirectionName"]
#    print (direct)
    if (not (direct is None)) and (int(direct) == Direction):
      if linje1 == "":
        linje1 = MakeLine(GetTime(i), StationName)
        linje1 = linje1 + str(Counter)
      else:
        if ("Extensions" in data[i]) and ("Deviations" in data[i]["Extensions"]) and ("Deviation" in data[i]["Extensions"]["Deviations"]):
          tekst = data[i]["Extensions"]["Deviations"]["Deviation"]
          linje2 = str(tekst)
        else:
          linje2 = MakeLine(GetTime(i), StationName)
          linje2 = linje2 + str(Counter)
    i = i + 1
        
   
  #Her skriver vi ut resultatet paa PC-skjermen
  print ("")
  print (linje1)
  print (linje2)
  print ("")
  if LCD == 1:
    lcd.clear()
  melding = linje1 + "\n" + linje2
  melding = melding.encode('ascii', 'ignore')
  if LCD == 1:
    lcd.message(melding)



# Clear display and show greeting, pause 1 sec
if LCD == 1:
  lcd.clear()
  lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
sleep(1)

# Set backlight to ON
if LCD == 1:
  lcd.ON

# Poll buttons, display message & set backlight accordingly
if LCD == 1:
  btn = ((lcd.LEFT  , -1          , lcd.RED),
       (lcd.UP    , 0           , lcd.BLUE),
       (lcd.DOWN  , 0           , lcd.GREEN),
       (lcd.RIGHT , 1           , lcd.VIOLET),
       (lcd.SELECT, 0           , lcd.ON))

prev = -1

#Legg inn stasjoner her. (holdeplassID, retning, displaynavn)
#Todo: Endre tilbake fra displaynavn til a hente det fra holdeplassen
Stasjoner = ((3012020, 2, "0steras"),
	     (3012020, 1, "Vestli"))
Stasjon = 0

LastReq = 0
LastWrite = 0 
Counter = 0
while True:
  try:
	  t_now = datetime.datetime.now()
      d_ts = time.mktime(t_now.timetuple())
      if int(d_ts - LastReq) > 60:
        LastReq = d_ts
        print ("Refreshing data from server")
        data = GetInfo(Stasjoner[Stasjon][0])
        print ("Got data from server")
      if not(data is None) and (int(d_ts - LastWrite) > 1):
        Counter = (Counter + 1) % 5; #Just to see a visual update
        WriteInfo(data,Stasjoner[Stasjon][1],Stasjoner[Stasjon][2], Counter)
        LastWrite = d_ts
      if LCD == 1:
		 for b in btn:
		   if lcd.buttonPressed(b[0]):
			 Stasjon = (Stasjon + b[1]) % len(Stasjoner)
			 if Stasjon < 0:
			   Stasjon = len(Stasjoner)
			 GetInfo(Stasjoner[Stasjon][0],Stasjoner[Stasjon][1],Stasjoner[Stasjon][2])
  except Exception,e:
    if LCD == 1:
      lcd.message("error:\n" + str(e))
    print ("error: " + str(e))
    sleep(60)
