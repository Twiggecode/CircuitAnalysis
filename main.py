# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 20:08:56 2020



While completing this academic project, we were restricted to using ONLY the numpy & sys libraries. Meaning, we could not use libraries such as Pandas to help us format
our output files.

This program is designed to analyse cascade circuits using the ABCD matrix analysis scheme. The program will read an input file of a specific format, 
where the input file specifies an entire cascade circuit, including the number of and types of components, all component values, whether impedances are shunt or series
impedances, the source voltage, source impedance and a range of source frequencies.

My program will process the data from the input file, calculating the ABCD matrix of the circuit, and the ABCD matrix will then be used to calculate the values 
of various quantities of the cascade circuit such as the output power, output voltage, voltage gain and many more quantities. The quantities will be calculated for various 
source frequencies, they will then be formatted and displayed in an output file.

To run the program, you must use a command line argument. The program accepts two formats for the command line argument. The standard format is: python main.py test.net test.out
where main.py is this file, test.net is the input file and test.out is the output file. The extended command line format is:   python main.py -i test -f
This format will also accept an input file of test.net and produce an output file test.out. The '-f' flag represents that the output data will be calculated and displayed in
the frequency domain. Change the flag to '-t' if you want to display the data in the time domain using IFFT.

INPUT FILE FORMAT:
    
Please look at the example input file to see the formatting.    
A '#' in the input file represents that the line is a comment and will be ignored.
n1 and n2 represent the two nodes attatched to a component. If n2=0, this component is a shunt component.
A norton or thevenin source can be specified in the <TERMS> block. The range of frequencies used will also be specificed in the <TERMS> block.
The units of the output quantities can be specified in the <OUTPUT> block. Unit prefixes can be used in ALL parts of the input file. dBV, dBW etc can be used to display a quantity in decibel/phase format.
Prefixes such as K, M, m etc can be used in the input file.
A logarithmic frequency sweep can also be used by changing 'Fstart' and 'Fend' to 'LFstart' and 'LFend' in the <TERMS> block.

"""


import numpy as np
import sys
import circuitsort
import ABCDmatrixcalc
import prefixcalc
import prefixcalcinv
import math

timeflag=0 # timeflag = 0 implies frequency response, timeflag = 1 implies time response

if sys.argv[2]=='-i': # extended command line format detected
    
    
    
    f = open(sys.argv[3]+'.net',"r")
    f1 =f.readlines()
    f.close()
    
    try:
        if sys.argv[4]=='-t':
            timeflag=1 # set timeflag = 1 to tell program that the output is a time response
            
    except:
        pass


else: # else standard command line format
    

    f = open(sys.argv[2],"r")

    f1 =f.readlines() #f1 is a list containing entire input file, each line is a string

    f.close()




commentflag=0 # flag used to indicate that the current line of the input file is a comment, and to not import that line into the progam
arraypointer=0 # counter used to point at the required array indexes
logflag=0 # flag used to represent whether frequencies are logarithmic or linear
indcounter=-1 # counts how many inductors are in the circuit
capcounter=-1  # counts how many capacitors are in the circuit

indices=np.zeros((1,6), dtype = int) # array to store indices corresponding to each block in the input file


for i in range (0,len(f1)): #for loop to create indices corresponding to the start and end of each block, <CIRCUIT>, <TERMS> etc
     if int ('<CIRCUIT>' in f1[i]) == 1:
        indices[0,0]=i
          
        
        
        
     if int ('</CIRCUIT>' in f1[i]) == 1:
        indices[0,1]=i          




     if int ('<TERMS>' in f1[i]) == 1:
        indices[0,2]=i   



     if int ('</TERMS>' in f1[i]) == 1:
        indices[0,3]=i  
        
        
       
        
        
     if int ('<OUTPUT>' in f1[i]) == 1:
        indices[0,4]=i 
        
        
        
        
     if int ('</OUTPUT>' in f1[i]) == 1:
        indices[0,5]=i 
        
        
circuit=np.zeros((0,0), dtype = complex)
terms=np.zeros((0,0), dtype = float)          # create empty array for each block
output=np.zeros((0,0), dtype = object)


capindices=np.zeros((0,0), dtype = int)
inductindices=np.zeros((0,0), dtype = int) # arrays to store the indices corresponding to location of capacitors and inductors within the circuit array


units=np.zeros((0,0), dtype = object) # stores output data type and units from <OUTPUT> block
variables=np.zeros((0,0), dtype = object)


arraypointer=-1

for i in range (indices[0,0]+1,indices[0,1]):  # for loop to fill the circuit array
    
    commentflag=0 # needs to be 0 by default
    
    if int('#' in f1[i]) == 1: # detects '#' substring to prevent comments being imported into array
        commentflag=1 # commentflag = 1 skips importing data for 1 loop iteration
        
    
    
    if commentflag!=1: 
        
       arraypointer+=1 # increment this every iteration to point at next locations in array to store data
       
       
       p=f1[i]
       tempslice=p[3:p.find(' ')]
       tempslice = tempslice.strip()
       
       
       
       try:
          
           p=int(tempslice)
           
       except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
           
           
       circuit=np.insert(circuit,3*arraypointer,p) # inserts the n1 values into circuit array
       
       
     
       p=f1[i]
       tempslice=p[(p.find('n2')+3):p.rfind(' ')]
       tempslice = tempslice.strip()
       
       try:
           
           p=int(tempslice)
           
       except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
           
       circuit=np.insert(circuit,(3*arraypointer)+1,p) # insert the n2 values into circuit array



       #extract whether it's a resistor, capacitor, inductor or conductor  
       p=f1[i]
       tempslice=p[(p.rfind(' ')+1):p.rfind('=')]
       tempslice = tempslice.strip()

       if tempslice == 'R': # if it's a resistor, get the resistance and plug it straight in the array
           
           tempslice = p[(p.rfind('=')+1):(len(p)-1)]
           
           tempslice = tempslice.strip()
           
           
                       
           
           
           try:
               
               p = prefixcalc.prefixcalc(tempslice) # convert if there are any prefixes
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
               
               
           circuit = np.insert(circuit,(3*arraypointer)+2,p)







       elif tempslice == 'G':  # if it's a conductor, invert the conductance to get resistance and store it
           
           tempslice = p[(p.rfind('=')+1):(len(p)-1)]
           
           tempslice = tempslice.strip()
           
           try: 
               p = prefixcalc.prefixcalc(tempslice)
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
               
           
           
        
               
           p=1/p
       
           circuit = np.insert(circuit,(3*arraypointer)+2,p)
           
                             


                                    
           
       
       elif tempslice == 'L': # if it's an inductor, store the impedance for freq of 1 Hz
           
           tempslice = p[(p.rfind('=')+1):(len(p)-1)]
           
           tempslice = tempslice.strip()
           
           try:
           
               p = prefixcalc.prefixcalc(tempslice) # convert if there are any prefixes
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
           
           
                                                                    
           p=complex(0,(2*math.pi*p))
           
           circuit = np.insert(circuit,(3*arraypointer)+2,p)
           
           indcounter += 1
           
           inductindices = np.insert(inductindices,indcounter,(3*arraypointer)+2) # save the indices of where the inductor impedances are stored in the circuit array, needed later
           
           
             
                      
           
           
           
       elif tempslice == 'C':     # else it must be a capacitor, store the impedance for a freq of 1 Hz
                 
           
           tempslice = p[(p.rfind('=')+1):(len(p)-1)]
           
           tempslice = tempslice.strip()
           
           try:
                               
               p = prefixcalc.prefixcalc(tempslice) 
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
               
               
                                                                              
           p=complex(0,(-1)/(2*math.pi*p))
           
           circuit = np.insert(circuit,(3*arraypointer)+2,p)
           
           capcounter+= 1
           
           capindices = np.insert(capindices,capcounter,(3*arraypointer)+2)


       else: # invalid circuit component
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
           

arraypointer=-1


for i in range (indices[0,2]+1,indices[0,3]): # for loop to fill the terms array
    
    commentflag=0 # commentflag is 0 by default

    if int('#' in f1[i]) == 1: # if a '#' is detected it's a comment in the input file, so skip this line
        commentflag=1
        
        
    if commentflag!=1: 
        
              
        arraypointer+=1 # increment to point at next location in array


        p=f1[i]
        
        if int('VT' in f1[i]) == 1: # stores both VT and RS in terms array as floats
            
            tempslice = p[p.find('=')+1:p.find(' ')]
            
            tempslice = tempslice.strip()
            
            try:
            
                p = prefixcalc.prefixcalc(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
                                                                             
            terms = np.insert(terms,0,p) # store VT
            
            p=f1[i]
            
            tempslice = p[p.rfind('=')+1:len(p)-1]
            
            tempslice = tempslice.strip()
            
            try:
            
                p = prefixcalc.prefixcalc(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
            
            if int('GS' in f1[i]) == 1: # convert to resistance if a conductance is detected
                
                p = 1/p
            
            
            
            terms = np.insert(terms,1,p)
            
            
            
        if int('IN' in f1[i]) == 1: # norton source detected, convert to thevenin source for ease of calculation
            
            tempslice = p[p.find('=')+1:p.find(' ')]
            
            tempslice = tempslice.strip()
            
            try:
            
                p = prefixcalc.prefixcalc(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
            
            tempslice = f1[i][f1[i].rfind('=')+1:len(f1[i])-1]
            
            tempslice = tempslice.strip()
            
            try:
            
                tempslice = prefixcalc.prefixcalc(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
            
            if int('GS' in f1[i]) == 1: # convert conductance to resistance
                
                tempslice = 1/tempslice
            
            p = p * tempslice
            
            terms = np.insert(terms,0,p)
            
            terms = np.insert(terms,1,tempslice)
        
        
        
        
        if int('RL' in f1[i]) == 1: # stores RL in terms array as float
                              
           p=f1[i]
        
           tempslice = p[p.find('=')+1:len(p)-1]
           
           tempslice = tempslice.strip()
           
           try:
           
               p = prefixcalc.prefixcalc(tempslice)
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
           
           terms = np.insert(terms,2,p)
        
        if int('GL' in f1[i]) == 1: # convert GL to RL and store in terms array
             
           p=f1[i]
        
           tempslice = p[p.find('=')+1:len(p)-1]
           
           tempslice = tempslice.strip()
           
           try:
           
               p = prefixcalc.prefixcalc(tempslice)
               
           except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
           
           p = 1/p
           
           terms = np.insert(terms,2,p)
             
             
             
        
        
        if int('Nfreqs' in f1[i]) == 1: # stores frequency data in terms array as floats
            
            p=f1[i]
            
            tempslice = p[p.find('=')+1:p.find(' ')]
            
            tempslice = tempslice.strip()
            
            freqprefix = tempslice[len(tempslice)-1:len(tempslice)]
            
            try:
            
                p = prefixcalc.prefixcalc(tempslice)  
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
            
            terms = np.insert(terms,3,p)
            
            p=f1[i]
            
            tempslice = p[(p.index('=',p.find(' '),p.rfind(' '))) +1:p.rfind(' ')]
            
            tempslice = tempslice.strip()
            
            try:
            
                p = prefixcalc.prefixcalc(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
            
            terms = np.insert(terms,4,p)
            
            p=f1[i]
            
            tempslice = p[p.rfind('=')+1:len(p)-1]
            
            tempslice = tempslice.strip()
            
            try:
            
                p=int(tempslice)
                
            except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
                
            
            terms = np.insert(terms,5,p)
            
            if int('LFend' in f1[i]) == 1: # set logflag = 1 if logarithmic frequencies detected, logflag is used later when calculating the frequencies
                
                logflag = 1
            
            
   



arraypointer=-1








for i in range (indices[0,4]+1,indices[0,5]): # for loop to fill the output, variables and units arrays
    
    
    
     commentflag=0 # commentflag is 0 by default


     if int('#' in f1[i]) == 1: # if a '#' is detected it's a comment in the input file, so skip this line
         commentflag=1



     if commentflag!=1: 

         arraypointer+=1 # increment to point at next location in array
        
         output = np.insert(output,arraypointer,f1[i])
                                                                                                                                            
         p = output[arraypointer]   
         
         
         
         if arraypointer==8 or arraypointer==9: # deal with units for gains Av and Ai
             
             if int('dB' in output[arraypointer]) == 1:
                 
                 units=np.insert(units,arraypointer,'dB')
                 
                 tempslice = p[0:p.find(' ')]
                 
                 tempslice = tempslice.strip()
                 
                 variables = np.insert(variables,arraypointer,tempslice)
                 
             else:
                 
                 units=np.insert(units,arraypointer,'L')
                 
                 tempslice = p[0:p.find(' ')]
                 
                 tempslice = tempslice.strip()
                 
                 variables = np.insert(variables,arraypointer,tempslice)
         
            
         
         else: 
            
                 tempslice = p[0:p.find(' ')]
                 
                 tempslice = tempslice.lstrip()
                 
                 tempslice = tempslice.rstrip()
         
                 variables = np.insert(variables,arraypointer,tempslice)
         
                 tempslice = p[p.find(' ')+1:len(output[arraypointer])-1]
                 
                 tempslice = tempslice.strip()
                         
                 units = np.insert(units,arraypointer,tempslice)
         
         
        

         
         
         
         

data = np.zeros((0,0), dtype = object) # stores all the numerical output data as strings in format of output file

dataorig = np.zeros((0,0), dtype = complex) # stores all numercial output data as complex numbers with no formatting


indcounter = -11 # arraypointereeps tracarraypointer of what loop iteration program is on


nfreq = int(terms[5]) # the number of frequency points in the output file


increment = (terms[4]-terms[3])/(terms[5]-1) # the incremental frequency increase between frequency points in the output file



circuit2 = np.copy(circuit)   # store a copy of the original circuit array, needed later


   
for i in range (1,nfreq+1): # loops over all frequencies, creating and storing output data
    
    indcounter += 11
    
    if logflag ==1: # calculate the logarithmic frequencies
        
        end = np.log10(terms[4])
        
        start = np.log10(terms[3])
        
        increment = (end-start)/(terms[5]-1)
        
        currentfreq = 10**(start + ((i-1)*increment))
        
    else: # calculate the linear frequencies
    
        currentfreq = terms[3] + ((i-1)*increment)
    
    
    
    # re calculate the circuit array for the currentfreq
    
    
    
    circuit = np.copy(circuit2) # return circuit array to original unsorted form, as can only update the impedances with the original unsorted circuit array
    
    
    for j in range (0,len(inductindices)): # update the inductor impedances to match the current frequency
          
          circuit[inductindices[j]] = circuit2[inductindices[j]]*currentfreq
    
    
    
    
    
    for j in range (0,len(capindices)): # update the capacitor impedances to match the current frequency
        
         circuit[capindices[j]] = circuit2[capindices[j]]/currentfreq
    
    
        
    circuit = circuitsort.circuitsort(circuit)   # sort the new circuit array so that component data is stored in the order that it appears in the circuit
     
    ABCDmatrix = ABCDmatrixcalc.ABCDmatrixcalc(circuit) # get the ABCD matrix corresponding to this frequency
    
    
    
    
    # calculate all the output data , considering prefixes  
        
    
    Zin = (((ABCDmatrix[0,0]*terms[2]) + ABCDmatrix[0,1])/((ABCDmatrix[1,0]*terms[2]) + ABCDmatrix[1,1]))
    
    Zinstore = Zin
    
    tempslice = units[7][0:1]
    
    try:
    
        Zin = prefixcalcinv.prefixcalcinv(tempslice,Zin)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
        
        
    Zout = (((ABCDmatrix[1,1]*terms[1]) + ABCDmatrix[0,1])/((ABCDmatrix[1,0]*terms[1]) + ABCDmatrix[0,0]))
    
    tempslice = units[5][0:1]
    
    try:
        
        Zout = prefixcalcinv.prefixcalcinv(tempslice,Zout)
       
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Iin = terms[0]/(terms[1]+Zinstore)
    
    Iinstore = Iin
    
    tempslice = units[2][0:1]
    
    try:
    
        Iin = prefixcalcinv.prefixcalcinv(tempslice,Iin)
    
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Vin = Zinstore * Iinstore
    
    Vinstore = Vin
    
    tempslice = units[0][0:1]
    
    try:
    
        Vin = prefixcalcinv.prefixcalcinv(tempslice,Vin)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Av = (1/(ABCDmatrix[0,0] + (ABCDmatrix[0,1]/terms[2])))
    
    Avstore = Av
    
    tempslice = units[8][0:1]
    
    try:
    
        Av = prefixcalcinv.prefixcalcinv(tempslice,Av)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Ai = (1/(ABCDmatrix[1,1] + (ABCDmatrix[1,0]*terms[2])))
    
    Aistore = Ai
    
    tempslice = units[9][0:1]
    
    try:
    
        Ai = prefixcalcinv.prefixcalcinv(tempslice,Ai)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Pin = Vinstore * np.conj(Iinstore)
    
    Pinstore = Pin

    tempslice = units[4][0:1]
    
    try:

        Pin = prefixcalcinv.prefixcalcinv(tempslice,Pin) 
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
        
    Vout = ((ABCDmatrix[1,1]*Vinstore) - (ABCDmatrix[0,1]*Iinstore))/((ABCDmatrix[0,0]*ABCDmatrix[1,1]) - (ABCDmatrix[0,1]*ABCDmatrix[1,0]))
    
    tempslice = units[1][0:1]
    
    try:
    
        Vout = prefixcalcinv.prefixcalcinv(tempslice,Vout)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Iout = ((ABCDmatrix[0,0]*Iinstore) - (ABCDmatrix[1,0]*Vinstore))/((ABCDmatrix[0,0]*ABCDmatrix[1,1]) - (ABCDmatrix[0,1]*ABCDmatrix[1,0]))
    
    tempslice = units[3][0:1]
    
    try:
    
        Iout = prefixcalcinv.prefixcalcinv(tempslice,Iout)
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    Pout = Pinstore*Avstore*np.conj(Aistore)
    
    tempslice = units[6][0:1]
    
    try:
    
        Pout = prefixcalcinv.prefixcalcinv(tempslice,Pout)
    
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    
       
    
    # store frequency in original and output file format
             
    try:
    
        currentfreq = prefixcalcinv.prefixcalcinv(freqprefix,currentfreq) # adjust frequency values to match any prefix it may have
        
    except: # error detected
           
               if sys.argv[2] == '-i': # detect extended command line format
               
                   f = open(sys.argv[3]+'.out',"w+") # write blank file
                   
               else:  # else it's the standard command line format
                   
                   f = open(sys.argv[3],"w+") # write blank file
          
           
               f.close()
           
               sys.exit()
    
    finalstr = ' ' + "{:.3e}".format(currentfreq) + ' '
    
    data = np.insert(data,indcounter,finalstr)
    
    dataorig = np.insert(dataorig,indcounter,currentfreq)
    
    
    
    
    # store Vin in original and output file format
    
    
    
    rl1 = float(np.real(Vin)) # stores real and imag components with their sign
    im1 = float(np.imag(Vin))
    
    rl = "{:.3e}".format(abs(np.real(Vin))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Vin)))
    
    dataorig=np.insert(dataorig,indcounter+1,Vin)
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+1,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+1,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+1,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+1,finalstr)
        
        
        
        
     # store Vout in original and output file format
        
    dataorig=np.insert(dataorig,indcounter+2,Vout)
    
    rl1 = float(np.real(Vout)) # stores real and imag components with their sign
    im1 = float(np.imag(Vout))
    
    rl = "{:.3e}".format(abs(np.real(Vout))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Vout)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+2,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+2,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+2,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+2,finalstr)
        
        
        
    
    
    # store Iin
        
    dataorig=np.insert(dataorig,indcounter+3,Iin)
        
    rl1 = float(np.real(Iin)) # stores real and imag components with their sign
    im1 = float(np.imag(Iin))
    
    rl = "{:.3e}".format(abs(np.real(Iin))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Iin)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+3,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+3,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+3,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+3,finalstr)
        
    




    # store Iout
        
    dataorig=np.insert(dataorig,indcounter+4,Iout)
        
    rl1 = float(np.real(Iout)) # stores real and imag components with their sign
    im1 = float(np.imag(Iout))
    
    rl = "{:.3e}".format(abs(np.real(Iout))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Iout)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+4,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+4,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+4,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+4,finalstr)
        
        
        
    # store Pin
        
    dataorig=np.insert(dataorig,indcounter+5,Pin)
        
    rl1 = float(np.real(Pin)) # stores real and imag components with their sign
    im1 = float(np.imag(Pin))
    
    rl = "{:.3e}".format(abs(np.real(Pin))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Pin)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+5,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+5,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+5,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+5,finalstr)
        
        
        
        
        
    # store Zout
        
    dataorig=np.insert(dataorig,indcounter+6,Zout)
        
    rl1 = float(np.real(Zout)) # stores real and imag components with their sign
    im1 = float(np.imag(Zout))
    
    rl = "{:.3e}".format(abs(np.real(Zout))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Zout)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+6,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+6,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+6,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+6,finalstr)
        
        
        
    # store Pout
        
    dataorig=np.insert(dataorig,indcounter+7,Pout)
        
    rl1 = float(np.real(Pout)) # stores real and imag components with their sign
    im1 = float(np.imag(Pout))
    
    rl = "{:.3e}".format(abs(np.real(Pout))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Pout)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+7,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+7,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+7,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+7,finalstr)
        
        
        
    # store Zin
        
    dataorig=np.insert(dataorig,indcounter+8,Zin)
        
    rl1 = float(np.real(Zin)) # stores real and imag components with their sign
    im1 = float(np.imag(Zin))
    
    rl = "{:.3e}".format(abs(np.real(Zin))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Zin)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+8,finalstr)
        
        
        
    elif im1 >= 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+8,finalstr)
        
        
        
    elif im1 < 0 and rl1 >= 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+8,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+8,finalstr)
        
        
        
    # store Av
        
    dataorig=np.insert(dataorig,indcounter+9,Av)
        
    rl1 = float(np.real(Av)) # stores real and imag components with their sign
    im1 = float(np.imag(Av))
    
    rl = "{:.3e}".format(abs(np.real(Av))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Av)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+9,finalstr)
        
        
        
    elif im1 > 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+9,finalstr)
        
        
        
    elif im1 < 0 and rl1 > 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+9,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        finalstr = '-' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+9,finalstr)
        
        
        
        
        
    # store Ai
        
    dataorig=np.insert(dataorig,indcounter+10,Ai)
        
    rl1 = float(np.real(Ai)) # stores real and imag components with their sign
    im1 = float(np.imag(Ai))
    
    rl = "{:.3e}".format(abs(np.real(Ai))) # scientific format with no sign
    im = "{:.3e}".format(abs(np.imag(Ai)))
    
    if im1 >= 0 and rl1 >= 0:
        
        
        finalstr = ' ' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+10,finalstr)
        
        
        
    elif im1 > 0 and rl1 < 0:
        
        finalstr = '-' + rl + '+j ' + im + ' '
        data=np.insert(data,indcounter+10,finalstr)
        
        
        
    elif im1 < 0 and rl1 > 0:
        
        finalstr = ' ' + rl + '+j-' + im + ' '
        data=np.insert(data,indcounter+10,finalstr)
        
        

    else:   # else both rl1 and im1 are negative
        
        if im1 == 0:
            
            finalstr = '-' + rl + '+j ' + im + ' '
            data=np.insert(data,indcounter+10,finalstr)
        
        elif rl1 == 0:
            
            finalstr = ' ' + rl + '+j-' + im + ' '
            data=np.insert(data,indcounter+10,finalstr)
            
        else:
            
        
            finalstr = '-' + rl + '+j-' + im + ' '
            data=np.insert(data,indcounter+10,finalstr)
        







# code to convert data into decibel and phase format if the units are in dB



for i in range(0,len(units)): # loop over unit array checking for dB and converting when needed
    
    
    if int('dB' in units[i]) == 1: # a unit is in terms of dB
        
        if int('dBV' in units[i]) == 1 and int('Vin' in variables[i]) == 1: # if Vin in terms of dBV, convert to dB/phase format and return to data array
            
            
            for j in range(0,len(data)-1,11): # calculate magnitude in dB, and phase
                
                                          
                magnitude = abs(dataorig[j+1])
                
                magnitude = 20*np.log10(magnitude)
                
                phase = np.angle(dataorig[j+1])
                
                magnitude1 = "{:.3e}".format(magnitude)
                
                phase1 = "{:.3e}".format(phase)
                
                if magnitude >= 0 and phase >= 0: # if elif else statements for writing the converted string back into data array in correct format
                    
            
                    
                    finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                    
                    data[j+1]=finalstr
                    
                    
                    
                elif magnitude >= 0 and phase < 0:
                    
                    
                    finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                    
                    data[j+1]=finalstr
                    
                    
                elif magnitude < 0 and phase >= 0:
                    
                    
                    finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                    
                    data[j+1]=finalstr
                    
                    
                else: # else both are negative
                                               
                    finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                    data[j+1]=finalstr
                    
                    
        if int('dB' in units[i]) == 1 and int('Ai' in variables[i]) == 1: # dB conversion for Ai
                  
                
                for j in range(0,len(data)-1,11):
                                     
                
                    magnitude = abs(dataorig[j+10])
                
                    magnitude = 20*np.log10(magnitude)                                       
                
                    phase = np.angle(dataorig[j+10])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+10]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+10]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+10]=finalstr
                        
                        
                    else: # both must be negative
                                                   
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+10]=finalstr
                            
                
        if int('dBV' in units[i]) == 1 and int('Vout' in variables[i]) == 1: # dB conversion for Vout
            
            for j in range(0,len(data)-1,11):
                                      
                
                    magnitude = abs(dataorig[j+2])
                
                    magnitude = 20*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+2])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+2]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+2]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+2]=finalstr
                        
                        
                    else: # both must be negative
                                                                          
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+2]=finalstr
            
            
            
            
            
            
        if int('dBA' in units[i]) == 1 and int('Iin' in variables[i]) == 1: # dB conversion for Iin
            
            for j in range(0,len(data)-1,11):
                                                        
                    magnitude = abs(dataorig[j+3])
                
                    magnitude = 20*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+3])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+3]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+3]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+3]=finalstr
                        
                        
                    else: # both must be negative
                                                                         
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+3]=finalstr
            
            
            
            
            
        if int('dBA' in units[i]) == 1 and int('Iout' in variables[i]) == 1: # dB conversion for Iout
            
                for j in range(0,len(data)-1,11):
                                                        
                    magnitude = abs(dataorig[j+4])
                
                    magnitude = 20*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+4])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+4]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+4]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+4]=finalstr
                        
                        
                    else: # both must be negative
                                                                          
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+4]=finalstr
            
            
            
            
        if int('dBW' in units[i]) == 1 and int('Pin' in variables[i]) == 1: # dB conversion for Pin
            
                for j in range(0,len(data)-1,11):
                                      
                
                    magnitude = abs(dataorig[j+5])
                
                    magnitude = 10*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+5])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+5]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+5]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+5]=finalstr
                        
                        
                    else: # both must be negative
                                                                          
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+5]=finalstr
            
            
            
        if int('dB' in units[i]) == 1 and int('Zout' in variables[i]) == 1: # dB conversion for Zout
            
            for j in range(0,len(data)-1,11):
            
                magnitude = abs(dataorig[j+6])
                
                magnitude = 10*np.log10(magnitude)
                
                phase = np.angle(dataorig[j+6])
                
                magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                phase1 = "{:.3e}".format(abs(phase))
                
                
                
                if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+6]=finalstr
                        
                
                elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+6]=finalstr
                        
                        
                elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+6]=finalstr
                        
                        
                        
                else: # both must be negative
                                                                         
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+6]=finalstr
                
            
            
            
        if int('dBW' in units[i]) == 1 and int('Pout' in variables[i]) == 1: # dB conversion for Pout
            
                for j in range(0,len(data)-1,11):
                                      
                
                    magnitude = abs(dataorig[j+7])
                
                    magnitude = 10*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+7])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+7]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+7]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+7]=finalstr
                        
                        
                    else: # both must be negative
                                                                         
                         finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                         data[j+7]=finalstr
                            
                            
        if int('dB' in units[i]) == 1 and int('Zin' in variables[i]) == 1: # dB conversion for Zin
            
            for j in range(0,len(data)-1,11):
                                      
                
                    magnitude = abs(dataorig[j+8])
                
                    magnitude = 10*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+8])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))

                    
                    
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+8]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+8]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+8]=finalstr
                        
                        
                    else: # both must be negative
                                                                       
                            finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                            data[j+8]=finalstr
            
            
            
            
        if int('dB' in units[i]) == 1 and int('Av' in variables[i]) == 1: # dB conversion for Av
            
                for j in range(0,len(data)-1,11):
                                                    
                    magnitude = abs(dataorig[j+9])
                
                    magnitude = 10*np.log10(magnitude)
                
                    phase = np.angle(dataorig[j+9])
                
                    magnitude1 = "{:.3e}".format(abs(magnitude))
                    
                    phase1 = "{:.3e}".format(abs(phase))
                
                
                    if magnitude >= 0 and phase >= 0:
                        
                        finalstr = ' ' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+9]=finalstr
                        
                
                    elif magnitude >= 0 and phase < 0:
                        
                        finalstr = ' ' + magnitude1 + '/_-' + phase1 + ' '
                        
                        data[j+9]=finalstr
                        
                        
                    elif magnitude < 0 and phase >= 0:
                        
                        finalstr = '-' + magnitude1 + '/_ ' + phase1 + ' '
                        
                        data[j+9]=finalstr
                        
                        
                    else: # both must be negative
                                                                                             
                        finalstr = '-' + magnitude1 + '/_-' + phase1 + ' '
                            
                        data[j+8]=finalstr
            
            
            




 # start writing the output file








indcounter=0

 
if sys.argv[2]=='-i': # extended command line format detected
    
    f = open(sys.argv[3]+'.out',"w+")
    
    
    if timeflag==1: # calculate time response
    
        increment = 1/(2*terms[4]) # 1/2Fs
        dataifft = np.zeros((10,int(terms[5])), dtype = complex) # initialise matrix to contain data ready to be passed through ifft
    
    
    
        for i in range (0,len(dataorig)-1,11): # loop through data array which contains frequencies and output data, creating array containing only output data to be passed through the ifft function
            
            dataifft[0,indcounter] = dataorig[i+1]
            dataifft[1,indcounter] = dataorig[i+2]
            dataifft[2,indcounter] = dataorig[i+3]
            dataifft[3,indcounter] = dataorig[i+4]
            dataifft[4,indcounter] = dataorig[i+5]
            dataifft[5,indcounter] = dataorig[i+6]
            dataifft[6,indcounter] = dataorig[i+7]
            dataifft[7,indcounter] = dataorig[i+8]
            dataifft[8,indcounter] = dataorig[i+9]
            dataifft[9,indcounter] = dataorig[i+10]
            
            indcounter += 1
            
        dataifft = np.fft.ifft(dataifft) # pass data through the ifft function, converting from frequency domain to time domain
        indcounter=0
        
        
        for i in range (0,len(data)-1,11): # return the ifft data and time values to dataorig array
            dataorig[i] = indcounter*increment
            dataorig[i+1] = dataifft[0,indcounter]
            dataorig[i+2] = dataifft[1,indcounter]
            dataorig[i+3] = dataifft[2,indcounter]
            dataorig[i+4] = dataifft[3,indcounter]
            dataorig[i+5] = dataifft[4,indcounter]
            dataorig[i+6] = dataifft[5,indcounter]
            dataorig[i+7] = dataifft[6,indcounter]
            dataorig[i+8] = dataifft[7,indcounter]
            dataorig[i+9] = dataifft[8,indcounter]
            dataorig[i+10] = dataifft[9,indcounter]
            
            indcounter += 1
            
        indcounter=0
        
        for i in range (0,len(data)-1): # convert data into output file format
            
            if indcounter==0: # it's a time value
                finalstr = ' ' + "{:.3e}".format(np.real(dataorig[i])) + ' '
                data[i] = finalstr
                indcounter += 1
                
            else: # it's a piece of output data
               
               rl1 = float(np.real(dataorig[i]))
               im1 = float(np.imag(dataorig[i]))
               rl = "{:.3e}".format(abs(rl1))
               im = "{:.3e}".format(abs(im1))
               
               if im1 >= 0 and rl1 >= 0:
           
                   finalstr = ' ' + rl + '+j ' + im + ' '
                   data[i] = finalstr
                
               elif im1 >= 0 and rl1 < 0:
        
                   finalstr = '-' + rl + '+j ' + im + ' '
                   data[i] = finalstr
                        
               elif im1 < 0 and rl1 >= 0:
        
                  finalstr = ' ' + rl + '+j-' + im + ' '
                  data[i] = finalstr
                
               elif im1 < 0 and rl1 < 0:
                   
                   finalstr = '-' + rl + '+j-' + im + ' '
                   data[i] = finalstr
                   
                   
               indcounter += 1
               
               if indcounter == 11: # reset counter
                   
                   indcounter = 0
                   
               
            
                                                                                                                            
            
            

else: # standard command line format detected

    f = open(sys.argv[3],"w+")




# write the first line of output file
    
    
if timeflag ==0: # frequency response detected

    f.write("%s%s%s%s%s%s%s%s" % ('      ','Freq','           ',variables[0],'                   ',variables[1],'                    ',variables[2]))

    f.write("%s%s%s%s%s%s%s%s" % ('                   ',variables[3],'                    ',variables[4],'                   ',variables[5],'                   ',variables[6]))

    f.write("%s%s%s%s%s%s%s" % ('                    ',variables[7],'                     ',variables[8],'                     ',variables[9],'          \n'))


else: # time response detected
    
    f.write("%s%s%s%s%s%s%s%s" % ('      ','Time','           ',variables[0],'                   ',variables[1],'                    ',variables[2]))

    f.write("%s%s%s%s%s%s%s%s" % ('                   ',variables[3],'                    ',variables[4],'                   ',variables[5],'                   ',variables[6]))

    f.write("%s%s%s%s%s%s%s" % ('                    ',variables[7],'                     ',variables[8],'                     ',variables[9],'          \n'))
    





# start writing the second line


if timeflag==0: # frequency response detected


    if freqprefix == 'arraypointer' or freqprefix == 'M' or freqprefix == 'G' or freqprefix == 'm' or freqprefix == 'u'  or freqprefix == 'n' or freqprefix == 'p': # prefix detected


        f.write("%s%s%s" % ('       ',freqprefix,'Hz'))

    else:


        f.write("%s%s" % ('        ','Hz'))


else: # time response detected
    
    f.write("%s%s" % ('       ','Sec'))






for i in range (0,len(units)):
    
    if i==0: # checking Vin units
        
        if int('dBV' in units[i]) == 1: # units in dBV
        
            f.write("%s%s" % ('           ',units[0]))
        
        elif len(units[i]) == 1:  # units in V
            
            f.write("%s%s" % ('             ',units[0]))
            
        else: # else units in volts with a prefix
            
            f.write("%s%s" % ('            ',units[0]))
            
            
    elif i==1: # checking Vout units
        
        if int('dBV' in units[i]) == 1: # units in dBV
            
            f.write("%s%s" % ('                    ',units[1]))
        
        elif len(units[i]) ==1: # units in V
            
            f.write("%s%s" % ('                      ',units[1]))
            
        else: # else units in volts with a prefix
            
            f.write("%s%s" % ('                     ',units[1]))
            
            
            
    elif i==2: # checking Iin units
        
        if int('dBA' in units[i]) == 1: # units in dBA
            
            f.write("%s%s" % ('                    ',units[2]))
            
        elif len(units[i])==1: # units in A
            
            f.write("%s%s" % ('                      ',units[2]))
            
        else: # else units in amps with a prefix 
            
            f.write("%s%s" % ('                     ',units[2]))
            
            
                                 
            
    elif i==3: # checking Iout units
        
        if int('dBA' in units[i]) == 1: # units in dBA
            
            f.write("%s%s" % ('                    ',units[3]))
            
        elif len(units[i])==1: # units in A
            
            f.write("%s%s" % ('                      ',units[3]))
            
        else: # else units in amps with a prefix 
            
            f.write("%s%s" % ('                     ',units[3]))
            
            
            
            
            
    elif i==4: # checking Pin units
        
        if int('dBW' in units[i]) == 1: # units in dBW
            
            f.write("%s%s" % ('                    ',units[4]))
            
        elif len(units[i])==1: # units in W
            
            f.write("%s%s" % ('                      ',units[4]))
            
        else: # units in W with a prefix
            
            f.write("%s%s" % ('                     ',units[4]))
            
            
            
            
            
    elif i==5: # checking Zout units
        
        if int('dB' in units[i]) == 1: # units in dB
            
            f.write("%s%s" % ('                     ',units[5]))
        
        elif len(units[i])==4: # units in ohms
        
            f.write("%s%s" % ('                   ',units[5]))
            
        else: # else it's ohms with a prefix
            
            f.write("%s%s" % ('                  ',units[5]))
            
            
            
        
    elif i==6: # checking Pout units
        
        if int('dBW' in units[i]) == 1: # units in dBW
            
            f.write("%s%s" % ('                    ',units[6]))
            
        elif len(units[i])==1: # units in W
            
            f.write("%s%s" % ('                      ',units[6]))
            
        else: # else it's watts with a prefix
            
            f.write("%s%s" % ('                     ',units[6]))
            
            
            
            
    elif i==7: # checking Zin units
        
        if int('dB' in units[i]) == 1: # units in dB
            
            f.write("%s%s" % ('                     ',units[7]))
        
        elif len(units[i])==4: # units in ohms
        
            f.write("%s%s" % ('                   ',units[7]))
            
        else: # else it's in ohms with a prefix
            
            f.write("%s%s" % ('                  ',units[7]))
        
    elif i==8: # checking Av units
        
        if int('dB' in units[i]) == 1: # units in dB
            
            f.write("%s%s" % ('                     ',units[8]))
            
        else: # no units (L)
            
            f.write("%s%s" % ('                      ',units[8]))
            
    else: # else i must be 9, check units for Ai
        
        if int('dB' in units[i]) == 1: # units in dB
            
            f.write("%s%s%s" % ('                     ',units[9],'          \n'))
            
        else: # no units (L)
            
            f.write("%s%s%s" % ('                      ',units[9],'          \n'))
                
                
        
        


for i in range (0,len(data),11): # write all the data to the output file
    
    
    
       f.write("%s%s%s%s%s%s%s%s" % (data[i],data[i+1],data[i+2],data[i+3],data[i+4],data[i+5],data[i+6],data[i+7],))

       f.write("%s%s%s%s" % (data[i+8],data[i+9],data[i+10],'\n'))      
            
            
f.close()







       
        
