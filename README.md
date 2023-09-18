# Water Usage Calculator for Crops

Implemented using information provided by **Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements (1998)** by Rick G. Allen and Food and Agriculture Organization of the United Nations.

## Description
The Penman–Monteith equation approximates net evapotranspiration (ET) from meteorological data. The equation is widely used, and was derived by the United Nations Food and Agriculture Organization for modeling potential evapotranspiration [ETo](https://www.fao.org/3/x0490e/x0490e08.htm). Utilizing this with a calculation of a numeric value corresponding to a [crop coefficient](https://farmwest.com/climate/calculator-information/et/crop-coefficients/#:~:text=The%20crop%20coefficients,%20Kc%20values,evaporation%20from%20the%20soil%20surface.) which allows us to calculate ETc, the water usage or net evapotranspiration of a crop. 

**ETc = ETo * Kc**

**ETc - Precipitation level = Irrigation in mm/day for a single crop unit**

## Usage

### Reference Evapotranspiration ETo
The function **calcEToPM()** takes max relative humidity (RHmax),  minimum temperature (Tmin),  maximum temperature (Tmax),  wind speed (u),  number of actual sunlight hours (n),  and altitude (yalt) as parameters. A table of variables and corresponding units can be found below:
 - **ETo** reference evapotranspiration [mm day-1]
 - **Rn** net radiation at the crop surface [MJ m-2 day-1]
 - **G** soil heat flux density [MJ m-2 day-1]
 - **T** air temperature [°C]
 - **u** wind speed [m s-1]
 - **es** saturation vapour pressure [kPa]
 - **ea** actual vapour pressure [kPa]
 - **es** - ea saturation vapour pressure deficit [kPa]
 - **D** slope vapour pressure curve [kPa°C-1]
 - **y** psychrometric constant [kPa °C-1].

The variables are used together to estimate ETo using the following equation found [here](https://www.fao.org/3/x0490e/x0490e08.htm). A number of these variables will be calculated using the meteorological tables provided by FAO [here](https://www.fao.org/3/x0490e/x0490e0j.htm#annex%202.%20meteorological%20tables).

### Crop Coefficient Kc
**calcKC()** uses the GSD, and Kc values from the Plant object that is inputted. Depending on the growth stage of a crop, the Kc value will be different. Currently, the program picks the higher of the Kc range values. However, in the future, a more accurate way of estimating Kc can be implemented. Instructions on how Kc can be determined from the Growth Stage Days can be found [here](https://www.fao.org/3/X0490E/x0490e0b.htm).

**Plant()** object stores the Growth Stage Days and corresponding [Kc](https://www.fao.org/3/X0490E/x0490e0b.htm) (crop coefficient) ranges. 

### Weather data
**WeatherDataGet()** takes in the weather api data from OpenWeatherMap and 1-2 arguments. This is merely for separating data into respective days for more easy manipulation. Weather data comes from [OpenWeatherMap's Hourly Forecast](https://openweathermap.org/api/hourly-forecast).
```
# will go into the data dict -> main -> temp
# print weatherdat to see more clearly
temp_data  =  WeatherDataGet(weatherdat,  'main',  'temp')
```

## Future Implementations 

 1. https://sunrise-sunset.org/api can be used to find sunlight hours
 2. A number of variables can be more accurately estimated. The [main page](https://www.fao.org/3/x0490e/x0490e08.htm) explicitly states the [corresponding tables](https://www.fao.org/3/x0490e/x0490e0j.htm#annex%202.%20meteorological%20tables) in which the values are estimated, and what formulas may also be used instead. 
 3. [PyOWM](https://github.com/csparpa/pyowm) can be used to more easily import weather data from OpenWeatherMap
 4. Precipitation levels as well as some other variables contain incomplete tables. They are marked as #INCOMPLETE in the code. The majority of the variable tables can be completed using this [link](https://www.fao.org/3/x0490e/x0490e0j.htm#annex%202.%20meteorological%20tables).
