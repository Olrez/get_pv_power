# -*- coding: utf-8 -*-
"""
Created on Thu May 28 19:45:32 2020

@author: Olde
"""
import sys 

def error(beta, gamma, Pcc_n, mode, date):
    if beta > 45:
        return print("El ángulo beta ingresado es muy elevado")
        return sys.exit();
    elif beta < 0:
        return print("El ángulo beta ingresado debe ser positivo")
        return sys.exit();
    elif gamma > 360:
        return print("El ángulo gamma ingresado no debe ser mayor a 360° \n 0: orientación norte \n 90: oeste \n 180: sur \n 270: este")
        return sys.exit();
    elif Pcc_n < 0:
        return print("Ingresar una potencia kWp positiva")
        return sys.exit();
    #elif mode != 'year' or mode != 'month' or mode != 'day':
        #return print("Solo se admiten modos year, month o day")
        #return sys.exit();
    else:
        return