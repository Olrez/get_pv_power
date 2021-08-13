# -*- coding: utf-8 -*-
"""
Created on Tue May  7 16:35:29 2019

@author: Olde
"""

import csv

with open('out.csv', 'a', newline='') as f_out:
    writer = csv.writer(f_out)
    line = ['ID', 'Latitude', 'Longitude']
    writer.writerow(line)

for i in range(23):
    i=str(i+1)
    with open('weather stations ('+i+').csv', 'r') as f,open('out.csv', 'a', newline='') as f_out:
        #reader = csv.DictReader(f)
        reader = csv.reader(f, delimiter=',')
        writer = csv.writer(f_out)
       
        for row in reader:
            row = [col.strip() for col in row]
            new_line = [str(row[2][-6:]), str(row[5][-8:]), str(row[6][-9:])]
            writer.writerow(new_line)
            break


