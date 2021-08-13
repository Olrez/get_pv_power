# -*- coding: utf-8 -*-
"""
Created on Wed May 27 20:23:31 2020

@author: Olde
"""
from numpy import exp, sin, cos, tan, arcsin, arccos, radians, degrees, mean
import pandas as pd
import matplotlib.pyplot as plt
from error_message import error
#El script calcula la energía producida por un sistema 
#fotovoltaico en un año típico meteorológico según la estación de datos climáticos cargada.

#Instrucciones:
#beta: ángulo de elevación del panel en °
#gamma: ángulo respesto al norte del sistema en ° (180 para orientación sur)
#Pcc_n: Potencia nominal del sistema en kWp para STC, para 1 kWh/m2 y 25°C
#modo de simulación:
    #'year': todo el año 2006 (TMY de estación GBS)
    #'month': un mes, especificar en date
    #'day': un día, especificar fecha en date
#date: fecha de simulación:
    #para año digite 0
    #para mes digite el número del 1 al 12
    #para día digite la fecha en formato 'num_dia-num_mes', por ejemplo: '22-6'

beta, gamma, Pcc_n, mode, date = [20,180,1,'year',0]

error(beta, gamma, Pcc_n, mode, date)

beta = radians(beta) #convertido a rad
gamma = radians(gamma) #convertido a rad
#Modelo transmitancia
#####################
K = 4         #coeficiente de extinción
L = 2e-3      #grosor del lente de vidrio en m
n_air = 1     #índice de refracción del aire
n_vid = 1.526 #índice de refracción del vidrio

def tau_0(x): # con x = theta, ángulo de incidencia en rad
#pérdidas por refracción en vidrio de celda fotovoltaica.    
    tau_o = 1-((n_air-n_vid)/(n_air+n_vid))**2
    return tau_o*exp(-(K*L))

def tau(x): # con x = theta, ángulo de incidencia en rad
#pérdidas por refracción en vidrio de celda fotovoltaica.    
    theta_r = arcsin((n_air/n_vid)*sin(x))
    return exp(-(K*L/cos(theta_r)))*(1-0.5*(((sin(theta_r-x))**2/(sin(theta_r+x))**2)+((tan(theta_r-x))**2/(tan(theta_r+x))**2)))

#Parámetros Modelo
##################

rho = 0.1      #reflectancia
NOCT = 44.6    #temperatura de la celda (°C) para condición nominal
T_ref = 25     #temeperatura de referencia según la prueba STC para una irradancia de 1kW/m2
u = -0.00509   #coeficiente de reducción de potencia por temperatura en #/°C (se divide entre 100)
Ltot = 0.1408  #pérdidas en %
n_ref = 0.9637 #eficiencia típica inversor
n_nom = 0.96   #eficiencia nominal inversor
Pca_0 = Pcc_n  #potencia nominal de corriente alterna del inversor


#Variables climáticas
#####################

climateData = pd.read_csv('output_weather_file.csv')
#Si el archivo es exportado de GBS, debe utilizar el script de python para
#obtener posición solar

#Formato csv entrada:
#1     2      3    4     5             6           7             8              9            10              11            12
#Year, Month, Day, Hour, GlobHorizRad, DirNormRad, DiffHorizRad, TotalSkyCover, DryBulbTemp, SolarElevation, SolarAzimuth, ClearSkyRad
#.to_numpy(dtype=object) #convert pandas series to numpy array
year = climateData['Year']+2000
month = climateData['Month']
day = climateData['Day']
hour = climateData['Hour']
Gh = climateData['Gh']/1000     #Irradiación Global Horizontal en kWh/m2
Gn = climateData['Gn']/1000     #Irradiancia Directa Normal en kWh/m2
Gdh = climateData['Gdh']/1000   #Irradiación Difusa Horizontal en kWh/m2
T_amb = climateData['DBT']      #temperatura ambiente, temperatura del aire o temperatura de bulbo seco en °C
theta_e =radians(climateData['Selev']) #ángulo de elevación del sol en rad (altitud)
theta_z = radians(90) - theta_e        #ángulo de cenital del sol en rad
gamma_sol = radians(climateData['Sazi']) #ángulo azimut del sol respecto al norte en rad

long_datos = range(len(month))

#Variables modelo
#################

"""
Gn = pd.Series(0, index=long_datos, name='Gn')
Gbh = Gh-Gdh                  #Irradiación Directa Horizontal en kWh/m2
cos_theta_z = cos(theta_z)

#Cálculo de Gn (ya viene en datos climáticos GBS)
for j in long_datos:
    if theta_e[j] <= 0:
       Gn[j] = 0
    elif theta_z[j] >=87.5 and theta_z[j] <= 90:
       theta_z[j]=87.5 #límite para la variable
       Gn[j] = Gbh[j]/cos_theta_z[j]
    else:
       Gn[j] = Gbh[j]/cos_theta_z[j]

"""

#Cálculo de theta, ángulo de incidencia en rad
cos_theta = sin(theta_z)*cos(gamma-gamma_sol)*sin(beta)+cos(theta_z)*cos(beta)
#gamma ángulo azimut de la celda respecto al norte en °C, beta ángulo de elevación de la celda en °C

theta = arccos(cos_theta)
        
for i in long_datos:
    if theta[i] >= radians(90) and theta[i] <= 0:
       theta[i] = radians(90) #límite teórico

Gb = Gn*cos_theta #irradancia que incide directamente en la superficie en kWh/m2
Rd = (1/3)*(2+cos(beta)) #factor de transposición

Gd = Rd*Gdh #Irradiancia Difusa que alcanza la superficie inclinada en kWh/m2
Rr = 0.5*(1-cos(beta)) #factor de transposición por reflexión
    
Gr = rho*Gh*Rr #Irradancia Reflejada por la superficie horizontal donde se encuentra el panel en kWh/m2

beta_deg = degrees(beta)
theta_cd = radians(59.7-0.1388*beta_deg+0.001497*beta_deg**2) #ángulo de incidencia de radiación difusa en rad
theta_cr = radians(90-0.5788*beta_deg+0.002693*beta_deg**2) #ángulo de incidencia de radiación reflejada en rad

Kb = tau(theta)/tau_0(0) #factor de corrección de la irradancia directa
Kd = tau(theta_cd)/tau_0(0) #factor de corrección de la irradancia difusa
Kr = tau(theta_cr)/tau_0(0) #factor de corrección de la irradancia reflejada

Gt = Kb*Gb + Kd*Gd + Kr*Gr #Irradiancia Global inclinada en kWh/m2


#Modelo térmico
###############

T_cel = T_amb + ((NOCT-20)/(0.8))*Gt #temperatura de la celda en °C, para 20 °C, 1 m/s y 0.8 kWh/m2 (condiciones NOCT)

#Potencia
#########

a = (1+u*(T_cel-T_ref))
Pcc = Pcc_n*Gt*a #Potencia corriente continua de celda para kWp de entrada STC

Pcc_inv = (1-Ltot)*Pcc #Potencia corriente continua de inversor
Pcc_0 = Pca_0/n_nom

Pca = [] #Potencia corriente alterna
xi = []
n_inv = [] #eficiancia del inversor

#Cálculo de Pca
for i in long_datos:
    
    if Pcc_inv[i] > 0 and Pcc_inv[i] < Pcc_0:
        xi.append(Pcc_inv[i]/Pcc_0)
      
        #Se limita el valor de n_inv ya que para valores muy pequeños de Pccinv, xi es MUY pequeña y por lo tanto n_inv negativo.
        if xi[i] < 6e-3:
            n_inv.append(0)
        else:
            n_inv.append((n_nom/n_ref)*(-0.0162*xi[i] -(0.0059/xi[i])+0.9858))
      
        Pca.append(n_inv[i]*Pcc_inv[i])
      
    elif Pcc_inv[i] >= Pcc_0:
        xi.append(0)
        n_inv.append(0)
        Pca.append(Pca_0)

    else: #Pcc_inv[i] == 0 
        xi.append(0)
        n_inv.append(0)
        Pca.append(0)
Pca = pd.Series(Pca, name='Pca')
Pca_date = pd.concat([year, month,day,hour,Pca], axis=1)
Pca_date.to_csv('Pac.csv') #Production export


#Energía producida
##################

names = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Setiembre','Octubre','Noviembre','Diciembre']
if mode == 'year':
    
    energia = []
    for i in range(12):
        Pca_date_month = Pca_date[Pca_date['Month'] == i+1]
        energia.append(Pca_date_month['Pca'].sum())
    energia = pd.Series(energia,index = names, name='Produccion kWh mensual')
    energia.to_csv('energia_anual.csv') #guardado de resultados para análisis financiero en Excel

    plt.figure(figsize=(10,5))
    energia.plot.bar(x="index", y="Produccion kWh mensual", rot=70, title='Producción anual del sistema FV de '+str(Pcc_n)+'kWp, a '+str(degrees(beta))+'° de elevacion')
    plt.xlabel('Mes')
    plt.ylabel('kWh')
    plt.grid(which='major', linestyle=':', linewidth='0.5', color='black')
    plt.savefig("energia_anual.png", bbox_inches='tight') #image export

    energia_total = energia.sum()
    energia_prom = mean(energia)

    print('La produccion anual es de '+str(round(energia_total,1))+' kWh \n con un promedio mensual de producción de '+str(round(energia_prom,1))+' kWh')

elif mode == 'month':
    
    Pca_date_month = Pca_date[Pca_date['Month'] == date].reset_index()
    energia = []
    month_days = Pca_date_month['Day'].max()
    month_name = names[date-1]
    
    for i in range(month_days):
        Pca_date_day = Pca_date_month[Pca_date_month['Day'] == i+1]
        energia.append(Pca_date_day['Pca'].sum())

    energia = pd.Series(energia, name='Produccion kWh por dia')
    num_day = pd.Series(range(month_days), name = 'dia')+1
    energia = pd.concat([num_day, energia], axis=1)
    energia.to_csv('energia_mes_de_'+str(month_name)+'.csv', index = False) #guardado de resultados del mes
    #energia = energia.set_index('dia')

    plt.figure(figsize=(10,5))
    energia.plot.bar(x='dia', y="Produccion kWh por dia", rot=70, title='Producción para el mes de '+str(month_name)+'\n del sistema FV de '+str(Pcc_n)+'kWp, a '+str(degrees(beta))+'° de elevacion')
    plt.xlabel('Día')
    plt.ylabel('kWh')
    plt.grid(which='major', linestyle=':', linewidth='0.5', color='black')
    plt.savefig('energia_'+str(month_name)+'.png', bbox_inches='tight') #image export

    energia_total = energia['Produccion kWh por dia'].sum()
    energia_prom = mean(energia['Produccion kWh por dia'])

    print('La produccion del mes es de '+str(round(energia_total,1))+' kWh \n con un promedio diario de producción de '+str(round(energia_prom,1))+' kWh')

elif mode == 'day':
    
    dia = int(date[:2])
    mes = int(date[3:])
    month_name = names[mes-1]

    Pca_date_month = Pca_date[Pca_date['Month'] == mes]
    energia = Pca_date_month[Pca_date_month['Day'] == dia]
    energia.to_csv('energia_dia_'+str(dia)+'_de_'+str(month_name)+'.csv', index = False) #guardado de resultados del dia

    plt.figure(figsize=(10,5))
    energia.plot.bar(x='Hour', y='Pca', rot=70, title='Producción del '+str(dia)+' de '+str(month_name)+'\n del sistema FV de '+str(Pcc_n)+'kWp, a '+str(degrees(beta))+'° de elevacion')
    plt.xlabel('Hora')
    plt.ylabel('kWh')
    plt.grid(which='major', linestyle=':', linewidth='0.5', color='black')
    plt.savefig('energia_'+str(dia)+'_de_'+str(month_name)+'.png', bbox_inches='tight') #image export

    energia_total = energia['Pca'].sum()
    energia_prom = mean(energia['Pca'])

    print('La produccion del dia es de '+str(round(energia_total,1))+' kWh \n con un promedio horario de producción de '+str(round(energia_prom,1))+' kWh')


