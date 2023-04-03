import json
from math import exp
import pandas as pd
from statistics import mean

class Plant():
    """
    Stores crop information about (FAO) distinct growth stages and the 
    total growing period data as well as respective crop coefficient 
    pertaining to each stage. 
    """

    def __init__(self, name=""):
         self.name = name 

    def setDays(self, intINIT, intDEV, intMID, intLATE):
         self.intINIT = intINIT
         self.intDEV = intDEV
         self.intMID = intMID
         self.intLATE = intLATE

    def setK(self, KINIT, KMID, KEND):
         self.KINIT = KINIT
         self.KMID = KMID 
         self.KEND = KEND

    def getDays(self):
        return list(self.intINIT, self.intDEV, self.intMID, self.intLATE)
    
    def getK(self):
        return list(self.KINIT, self.KMID, self.KEND)

    def getConfig(self):
        format = {"intINIT": self.intINIT,
                "intDEV": self.intDEV,
                "intMID": self.intMID,
                "intLATE": self.intLATE,

                "KINIT": self.KINIT,
                "KMID": self.KMID,
                "KEND": self.KEND}
        
        return format

# CALCULATION OF ETO: Penman-Montieth
"""
ETo reference evapotranspiration [mm day-1],
Rn net radiation at the crop surface [MJ m-2 day-1],
G soil heat flux density [MJ m-2 day-1],
T air temperature [°C],
u wind speed [m s-1],
es saturation vapour pressure [kPa],
ea actual vapour pressure [kPa],
es - ea saturation vapour pressure deficit [kPa],
D slope vapour pressure curve [kPa °C-1],
y psychrometric constant [kPa °C-1].
"""
def calcEToPM(RHmax, Tmin, Tmax, u, n, yalt):
    # Average temperature calculation
    Tavg = (Tmax + Tmin)/2

    # Slope of vapour pressure curve calculation
    D = (4098*(0.618*exp((17.27*Tavg)/(Tavg+237.3))))/(Tavg+237.3)**2

    # Psychometric constant (g) for different altitudes (z)
    # INCOMPLETE TABLE (table 2.2 on fao site)
    # average altitude in Vancouver is 34m
    yalt = yalt
    ytable = {"0":0.067, "100":0.067, "200":0.066, "300":0.065}

    for key, val in ytable.items():
        if yalt >= float(key):
            y = val
        else:
            break

    # INCOMPLETE must call to api
    # Wind speed in m/s at 2m height
    u = u

    # Saturation Vapour Pressure kPa
    es = (0.6108*exp((17.21*Tmax)/(Tmax + 237.3)) + 0.6108*exp((17.21*Tmin)/(Tmin + 237.3)))/2
    
    # Can be derived from either dewpoint temperature or relative humidity 
    ea = 0.6108*exp((17.21*Tmin)/(Tmin + 237.3))*(RHmax/100)
    #ea = es*RHmax/100 less recommended due to non-linearities

    # Daily extraterrestrial radiation (Ra) for different latitudes for the 15th day of the month 
    # Vancouver latitude in degrees:
    lat = '48'
    month = 3
    # INCOMPLETE: Need one array for each latitiude, one element for each month per latitude
    RaTable = {'48':[10.1,15.7,23.3,32.2,38.8,41.8]}
    Ra = RaTable[lat][month-1]

    # Mean daylight hours (N) for different latitudes for the 15th of the month
    # INCOMPLETE: Need one array for each latitiude, one element for each month per latitude
    nTable = {'48':[8.6,10.0,11.6,13.4,15.0]} 
    n_max = nTable[lat][month-1]
    # ACTUAL sunshine hours INCOMPLETE must get sunrise and sunset
    n = n

    Rs = (0.25 + 0.50*(n/n_max))*Ra
    Rso = (0.75 + 2*yalt/100000)*Ra
    
    Rns = 0.77*Rs

    # (Stefan-Boltzmann law) at different temperatures (T)
    oTTable = {"1.0":27.70,"1.5":27.90,"3.0":28.52}
    for key, val in oTTable.items():
        if Tmax >= float(key):
            oTmax = val
        else:
            break
    for key, val in oTTable.items():
        if Tmax >= float(key):
            oTmin = val
        else:
            break

    Rnl = (oTmax + oTmin)/2 * (0.34-0.14*(ea)**(1/2)) * (1.35*Rs/Rso - 0.35)
    Rn = Rns - Rnl

    # INCOMPLETE
    # Soil Heat Influx
    # Since difficult to estimate and we are doing day to day
    G = 0 

    ETo = (0.408*D*(Rn - G) + y*(900/(Tavg + 273))*(u*(es-ea)))/(D + y*(1+0.34*u))

    return ETo

### CALCULATES KC
def calcKC(GSD, plantObject):
    
    plantData = plantObject.getConfig()

    # Initial
    KC = -1

    # Must take cumulative sum of days
    if GSD > 0 and GSD < plantData["intINIT"]:
        KC = plantData["KINIT"]

    elif GSD > plantData["intINIT"] and GSD < plantData["intDEV"]:
        KC = (plantData["KINIT"] + plantData["KMID"])/2

    # Development
    elif GSD > plantData["intDEV"] and GSD < plantData["intMID"]:
        KC = plantData["KMID"]

    # Mid season
    elif GSD > plantData["intMID"] and GSD < plantData["intLATE"]:
        KC = (plantData["KMID"] + plantData["KEND"])/2
    
    return KC

# Retrieves specific weather data for each day individually
def WeatherDataGet(weatherdat, *args):
    # Weather data per hour
    data_dict = {}

    time_focus = weatherdat['list'][0]['dt_txt']
    data_dict[time_focus[:len(time_focus)-9]] = []

    for i in range(len(weatherdat['list'])):

        print(f"{weatherdat['list'][i]}\n")

        # EXISTS
        if time_focus[:len(time_focus)-9] == weatherdat['list'][i]['dt_txt'][:len(weatherdat['list'][i]['dt_txt'])-9]:
            if len(args) == 1:
                data_dict[time_focus[:len(time_focus)-9]].append(weatherdat['list'][i][args[0]])
            elif len(args) == 2:
                data_dict[time_focus[:len(time_focus)-9]].append(weatherdat['list'][i][args[0]][args[1]])
        else:
            time_focus = weatherdat['list'][i]['dt_txt']
            data_dict[time_focus[:len(time_focus)-9]] = []
            if len(args) == 1:
                data_dict[time_focus[:len(time_focus)-9]].append(weatherdat['list'][i][args[0]])
            elif len(args) == 2:
                data_dict[time_focus[:len(time_focus)-9]].append(weatherdat['list'][i][args[0]][args[1]])

    return data_dict



# https://pro.openweathermap.org/data/2.5/forecast/hourly?lat=49&lon=123&appid={TOKEN}&units=metric
df = pd.read_csv('data.csv', sep=',')
f = open('weatherdata.json')
weatherdat = json.load(f)

# DATA FORMATTING
temp_data = WeatherDataGet(weatherdat, 'main', 'temp')
wind_speed_data = WeatherDataGet(weatherdat, 'wind', 'speed')
humidity_data = WeatherDataGet(weatherdat, 'main', 'humidity')

### EXAMPLE FOR DAT 2023-04-02
# RH, Tmin, Tmax, wind speed
Tmin = min(temp_data['2023-04-02'])
Tmax = max(temp_data['2023-04-02'])
RHmax = max(humidity_data['2023-04-02'])
uavg = mean(wind_speed_data['2023-04-02'])

# CREATING PLANT OBJECT
BroccoliParam = Plant()
BroccoliParam.setDays(35, 45+35, 40+45+35, 15+40+45+35)
BroccoliParam.setK(0.7, 1.05, 0.95)

# Growth stage days
GSD = 100
Kc = calcKC(GSD,BroccoliParam)
# % cels cels m/s hours m
# (RHmax, Tmin, Tmax, u, n, yalt)
EToPM = calcEToPM(RHmax, Tmin, Tmax, uavg, 9.25, 100)
ETc = EToPM * Kc

## INCOMPLETE
# precipitation in mm
precip = 0


print(Kc)
#print(f"{EToHS} mm/day")
print(f"{EToPM} mm/day")
print(f"{ETc} mm/day")
print(f"{ETc} - {precip} mm/day")

# ETc = KC * ETo, returns in mm/day per unit area of crop



