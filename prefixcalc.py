# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 05:36:02 2020

@author: Adam
"""

 # function to convert values with exponents in the circuit and terms block into standard format

def prefixcalc(string):
    
           if int('p' in string) == 1: # pico prefix detected
               
               string=string[0:len(string)-1]
               
               q = float(string)
               
               q = q*(10**-12)
               
               
           elif int('n' in string) == 1: # nano prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**-9)
               
               
           elif int('u' in string) == 1: # micro prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**-6)
               
               
           elif int('m' in string) == 1: # milli prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**-3)
               
               
           elif int('k' in string) == 1: # kilo prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**3)
               
               
           elif int('M' in string) == 1: # mega prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**6)
               
               
           elif int('G' in string) == 1: # giga prefix detected
               
               string=string[0:len(string)-1]
                                 
               q = float(string)
               
               q = q*(10**9)
               
               
           else: # no prefix detected
           
               q=float(string)
               
           return q