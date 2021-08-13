# -*- coding: utf-8 -*-
"""
Created on Tue May  7 20:45:03 2019

@author: Olde
"""
from pysolar import solar, radiation
import csv                         #
from datetime import datetime,tzinfo,timedelta   #import the librairies   

with open('GBS_06M12_15_273032.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
       
    for row in reader:
        row = [col.strip() for col in row]
        latitude = float(row[5][-8:])
        longitude = float(row[6][-9:])
        break

Year = []
Month = []
Day = []
Hour = []
GlobHorizRad = []
DirNormRad = []
DiffHorizRad = []
TotalSkyCover = []
DryBulbTemp = []
with open('GBS_06M12_15_273032.csv', 'r') as fh:
    reader = csv.reader(fh)
    next(reader)
    next(reader)
    for row in reader:
        Year0 = row[0]
        # list comprehension for float conversion
        Month0, Day0, Hour0, GlobHorizRad0, DirNormRad0, DiffHorizRad0, TotalSkyCover0, DryBulbTemp0, DewPointTemp0, RelHumidty0, Pressure0, WindDir0, WindSpeed0 = [str(value) for value in row[1:]]
        Year.append(Year0)
        Month.append(Month0)
        Day.append(Day0)
        Hour.append(Hour0)
        GlobHorizRad.append(GlobHorizRad0)
        DirNormRad.append(DirNormRad0)
        DiffHorizRad.append(DiffHorizRad0)
        TotalSkyCover.append(TotalSkyCover0)
        DryBulbTemp.append(DryBulbTemp0)
    
class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

GMT = Zone(-6,False,'GMT')

date = []
se = []
sa = []
rad = [] 
with open('output_weather_file.csv', 'a', newline='') as f_out:
    writer = csv.writer(f_out)
    for i in range(0, len(Year)): 
        date0 = datetime.strptime('20'+Year[i]+'-'+Month[i]+'-'+Day[i]+' '+Hour[i], '%Y-%m-%d %H')
        date0 = date0.replace(tzinfo=GMT)
        #date0 = date0 + timedelta(hours=-18)
        date.append(date0)
        se0 = solar.get_altitude(latitude, longitude, date0)
        se.append(se0)
        sa0 = solar.get_azimuth(latitude, longitude, date0)
        sa.append(sa0)
        rad0 = radiation.get_radiation_direct(date0, se0)
        rad.append(rad0)
        new_line = [Year[i], Month[i], Day[i], Hour[i], GlobHorizRad[i], DirNormRad[i], DiffHorizRad[i], TotalSkyCover[i], DryBulbTemp[i], str(se[i]), str(sa[i]),str(rad[i])]
        writer.writerow(new_line)
