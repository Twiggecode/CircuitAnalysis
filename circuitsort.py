# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 19:30:52 2020

@author: Adam
"""


def circuitsort(arr): # sorts the circuit array so that components are stored in the order they appear in the circuit
    

    n1 = len(arr)
 
  
    flagy=1

    while (flagy == 1):
        flagy=0
 
        
        for j in range(0, n1-5,3):
    
            
            if arr[j] > arr[j+3] : # if n1 values not in ascending order, swap data
                  arr[j], arr[j+3] = arr[j+3], arr[j]
                  arr[j+1], arr[j+4] = arr[j+4], arr[j+1]
                  arr[j+2], arr[j+5] = arr[j+5], arr[j+2]
                  flagy=1
                  
                  
            if arr[j] == arr[j+3] and arr[j+1] > arr[j+4]: # if a shunt and series component are conncted to the same n1, store the shunt before the series
                
                  arr[j], arr[j+3] = arr[j+3], arr[j]
                  arr[j+1], arr[j+4] = arr[j+4], arr[j+1]
                  arr[j+2], arr[j+5] = arr[j+5], arr[j+2]
                  flagy=1
                                               
                
                
    x=arr
    return x