# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 07:34:56 2020

@author: Adam
"""


# function to convert output data in standard format to the value corresponding to it's prefix in the output block.
# e.g, converts a Zin = 1000 ohms to Zin = 1 kohms if the kilo prefix is detected

# 'string' is the prefix. 't' is the piece of output data being converted


def prefixcalcinv(string,t):
    
           if int('p' in string) == 1: # pico prefix detected
                                                                         
               value = t*(10**12)               
               
           elif int('n' in string) == 1: # nano prefix detected
                                 
               value = t*(10**9)
                             
           elif int('u' in string) == 1: # micro prefix detected
                                           
               value = t*(10**6)
               
               
           elif int('m' in string) == 1: # milli prefix detected                          
               
               value = t*(10**3)
                             
           elif int('k' in string) == 1: # kilo prefix detected
                                            
               value = t*(10**-3)
               
               
           elif int('M' in string) == 1: # mega prefix detected
                                          
               value = t*(10**-6)
               
               
           elif int('G' in string) == 1: # giga prefix detected
                                        
               value = t*(10**-9)
               
               
           else: # no prefix detected
           
               value = t
               
           return value