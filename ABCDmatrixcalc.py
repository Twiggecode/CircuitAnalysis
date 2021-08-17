# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 21:30:26 2020

@author: Adam
"""
import numpy as np

def ABCDmatrixcalc(array): # calculates the ABCD matrix for a given array of circuit data
    
    matrix1=np.zeros((2,2), dtype=complex)        
    matrix2=np.zeros((2,2), dtype=complex) # predefine temp storage matrices to do the ABCD calculation
    tempmatrix=np.zeros((2,2), dtype=complex)


         
         
    flag=1


    if array[1] == 0:   # define the first ABCD matrix if it's a shunt impedance
        matrix1[0,0] = 1
        matrix1[0,1] = 0
        matrix1[1,0] = 1/(array[2])
        matrix1[1,1] = 1
    
    
    else: # else it's a series impedance, define first ABCD matrix using series impedance formula
    
        matrix1[0,0] = 1
        matrix1[0,1] = array[2]
        matrix1[1,0] = 0
        matrix1[1,1] = 1
    
    
    for i in range (5,len(array),3):
    
    
        if flag == 1: # flag=1 means it's the first iteration of the loop, calculate stuff a little differently
         
            flag = 0
         
            if array[4] == 0:   # checks if it's a shunt
                tempmatrix[0,0] = 1
                tempmatrix[0,1] = 0
                tempmatrix[1,0] = 1/(array[5])
                tempmatrix[1,1] = 1
             
             
             
            else:   # else it's a series impedance
                tempmatrix[0,0] = 1
                tempmatrix[0,1] = array[5]
                tempmatrix[1,0] = 0
                tempmatrix[1,1] = 1
             
             
            matrix2 = matrix1 @ tempmatrix       
             
        else:  
         
         
             if array[i-1] == 0: # it's a shunt
                 tempmatrix[0,0] = 1
                 tempmatrix[0,1] = 0
                 tempmatrix[1,0] = 1/(array[i])
                 tempmatrix[1,1] = 1
                 
             else: # else it's a series impedance
                 
                 tempmatrix[0,0] = 1
                 tempmatrix[0,1] = array[i]
                 tempmatrix[1,0] = 0
                 tempmatrix[1,1] = 1
                 
             matrix2 = matrix2 @ tempmatrix
            
    return matrix2