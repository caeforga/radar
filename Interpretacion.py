import numpy as np
import csv
import time

def main():
    tiempoInicial=time.time()
    archivo="output/Lecturas RADAR/31_03_2025_2.csv"
    
    tiempo, niveles = carga_archivo(archivo)
    
    #periodo=0.000001
    
    #tolerancia= 0.25
    
    #decoded_bits=decodificacion(tiempo, niveles, periodo, tolerancia)
    
    angles=angulos(niveles,tiempo)
    print('Tiempo de ejecucion de la interpretacion: ' + str(time.time()-tiempoInicial))
    return angles



def carga_archivo(archivo):
    
    tiempo=[]
    nivel=[]
    
    reader=csv.reader(open(archivo,"r"))
   
    for i, row in enumerate(reader):
        if i==0:
            try:
                float(row[0]),float(row[1])
            except ValueError:
                
                continue
        #if(float(row[0])>=0):
        tiempo.append(float(row[0]))
        nivel.append(int(row[1]))
        
    return tiempo, nivel   


# def decodificacion(tiempo, cambios, periodo, tolerancia):
    
#     clock_min= periodo*(1-tolerancia)
#     clock_max= periodo*(1+tolerancia)
    
#     deltaT=[]
#     decoded_bits =[]
    
#     for e in range (1,len(tiempo)):
        
#         deltaT.append(tiempo[e]-tiempo[e-1])

#     o=0;
    
#     while o<=len(deltaT)-1:
#         if (deltaT[o]>=clock_min*3/2 and deltaT[o]<=clock_max*3/2) and (cambios[o]==1 and cambios[o+1]==0):
#             if (deltaT[o+1]>=clock_min*2 and deltaT[o+1]<=clock_max*2) and (cambios[o+2]==1):
#                 decoded_bits.append(0);
#                 index=o+2;
#                 long_bits=0;
#                 flag=0;
#                 while long_bits<1599:
#                     if (deltaT[index]+deltaT[index+1])>=clock_min and (deltaT[index]+deltaT[index+1])<=clock_max:
#                         if cambios[index+2]==1:
#                             decoded_bits.append(0)
#                         else: 
#                             decoded_bits.append(1)
#                         long_bits=long_bits+1
#                         index=index+2
#                         flag=0
                    
#                     elif deltaT[index]>=clock_min and deltaT[index]<=clock_max:
#                         if cambios[index+1]==1:
#                            decoded_bits.append(0)
#                         else:
#                            decoded_bits.append(1)
                           
#                         long_bits=long_bits+1;
#                         index=index+1;
#                         flag=1;
#                     else:
#                         print("Fallo de lectura")
#                         indice=len(decoded_bits)
#                         trama=int(len(decoded_bits)/1600)
#                         sobrantes=len(decoded_bits)%1600
#                         break
                        
                
#                 if flag==0:
#                     index=index+4
#                 else:
#                     index=index+2
                
#                 o=index
                
#         else:
#             o=o+1
    
#     return decoded_bits


def angulos(decoded_bits,tiempo):
    

    barrido=0
    i=0
    comprobacion="".join(map(str,decoded_bits[i:i+8]))
    while comprobacion!="00101101" and comprobacion!="01111001":
        i=i+1
        comprobacion="".join(map(str,decoded_bits[i:i+8]))
    
    
      
    

    decoded_bits=decoded_bits[i:-1]
    tiempos_reales=tiempo[i:-1] 
    angles=[]


    if comprobacion=="00101101":
        u=0
        malas= 0
        while u<len(decoded_bits):
            
            if u<len(decoded_bits)-1599:

                deltaT=tiempos_reales[u+1599]-tiempos_reales[u]
                
                if deltaT>0.0015985 and deltaT<0.0015995:
                    print("Trama re valida")
                    current=decoded_bits[u:u+1600]
                    current_processed=[]
                    
                    #Etiqueta -- bits 1-8 -- Casillas 0-7
                    
                    etiqueta = "".join(map(str,current[0:8]))
                    current_processed.append(etiqueta)
                    
                    #Aceptacion -- bits 9-10 -- Casillas 8-9
                    
                    if current[8]==0 and current[9]==0:
                        aceptacion=1 #Fallo de acepacion
                    elif current[8]==1 and current[9]==0:
                        aceptacion=2 #Aceptacion de control 1
                    elif current[8]==0 and current[9]==1:
                        aceptacion=3 #Aceptacion de control 2
                    else:
                        aceptacion=4 #Aceptacion de ambos controles
                    
                    current_processed.append(aceptacion)
                    
                    #Anuncio de modo -- bits 14-18 -- Casillas 13-17
                    anuncio=[]
                    
                    for b in range(0,4):
                        if current[13+b]==1:
                            anuncio.append(b)
                    
                    current_processed.append(anuncio)
                    
                    #Fallos -- bits 19-25 -- Casillas 18-24
                    
                    fallos=[]
                    
                    for x in range(0,7):
                        if current[18+x]==1:
                            fallos.append(x)
                    current_processed.append(fallos)
                    
                    #Operacion -- bits 27-29 -- Casillas 26-28
                    
                    if (current[26]==0 and current[27]==0 and current[28]==0):
                        modo = 0 # STBY
                    elif (current[26]==1 and current[27]==0 and current[28]==0):
                        modo = 1 # Clima
                    elif (current[26]==0 and current[27]==1 and current[28]==0):
                        modo = 2 # Mapa
                    elif (current[26]==1 and current[27]==1 and current[28]==0):
                        modo = 3 # Contorno
                    elif (current[26]==0 and current[27]==0 and current[28]==1):
                        modo = 4 # TEST
                    elif (current[26]==1 and current[27]==0 and current[28]==1):
                        modo = 5 # Turbulencia
                    elif (current[26]==0 and current[27]==1 and current[28]==1):
                        modo = 6 # Clima y turbulencia
                    else:
                        modo = 7 #Calibracion
                        
                    current_processed.append(modo)
                    
                    #Inclinacion -- bits 30-36 -- Casillas 29-35
                    
                    inclinacion = 0
                    
                    if current[35]==1:
                        inclinacion = inclinacion - 16
                    if current[34]==1:
                        inclinacion = inclinacion + 8
                    if current[33]==1:
                        inclinacion = inclinacion + 4
                    if current[32]==1:
                        inclinacion = inclinacion + 2
                    if current[31]==1:
                        inclinacion = inclinacion + 1
                    if current[30]==1:
                        inclinacion = inclinacion + 0.5
                    if current[29]==1:
                        inclinacion = inclinacion + 0.25
                        
                    current_processed.append(inclinacion)
                    
                    #Ganancia -- bits 37-42 -- Casillas 36-41
                
                    gain= -(current[36]*0.5+current[37]*1+current[38]*2+current[39]*4+current[40]*8+current[41]*16)
                    
                    current_processed.append(gain)
                    
                    #Rango -- bits 43-48 -- Casillas 42-47
                    
                    if (current[42]==1):
                        rango= 5
                    elif (current[43]==1):
                        rango= 10
                    elif (current[44]==1):
                        rango= 20
                    elif (current[45]==1):
                        rango= 40
                    elif (current[46]==1):
                        if (current[47]==1):
                            rango= 240
                        else:
                            rango=80
                    elif (current[47]==1):
                        rango=160
                        
                    current_processed.append(rango)
                    
                    #Barrido -- bits 52-63 -- casillas 51-62
                    
                    barrido=0
                    
                    if (current[62]==1):
                        barrido=barrido-180
                    if (current[61]==1):
                        barrido=barrido+90
                    if (current[60]==1):
                        barrido=barrido+45
                    if (current[59]==1):
                        barrido=barrido+22.5
                    if (current[58]==1):
                        barrido=barrido+11.25
                    if (current[57]==1):
                        barrido=barrido+5.625
                    if (current[56]==1):
                        barrido=barrido+2.8125
                    if (current[55]==1):
                        barrido=barrido+1.40625
                    if (current[54]==1):
                        barrido=barrido+0.703125
                    if (current[53]==1):
                        barrido=barrido+0.3515625
                        
                    current_processed.append(barrido)
                    
                    #Datos -- bits 65-1600  -- Casillas 64-1559 
                    datos=[]
                    
                    for y in range(0,512):
                        if (current[64+3*y]==0 and current[65+3*y]==0 and current[66+3*y]==0):
                            datos.append(0) #0 para negro
                        elif (current[64+3*y]==1 and current[65+3*y]==0 and current[66+3*y]==0):
                            datos.append(1) #1 para verde
                        elif (current[64+3*y]==0 and current[65+3*y]==1 and current[66+3*y]==0):
                            datos.append(2) #2 para amarillo
                        elif (current[64+3*y]==1 and current[65+3*y]==1 and current[66+3*y]==0):
                            datos.append(3) #3 para rojo
                        elif (current[64+3*y]==0 and current[65+3*y]==0 and current[66+3*y]==1):
                            datos.append(4) #4 para magenta
                        elif (current[64+3*y]==1 and current[65+3*y]==0 and current[66+3*y]==1):
                            datos.append(5) #5 para fuera de rango
                        elif (current[64+3*y]==0 and current[65+3*y]==1 and current[66+3*y]==1):
                            datos.append(6) #6 para turbulencia media
                        else:
                            datos.append(7) #7 para turbulencia fuerte
                            
                    current_processed.append(datos)
                    angles.append(current_processed) 
                    u=u+1600
                else:
                    print("Trama no valida")
                    c=u+1
                    malas=malas+1
                    while c<len(decoded_bits):
                        deltica=tiempos_reales[c]-tiempos_reales[u]
                        if deltica> 0.013605 and deltica<0.014555:
                            u=c
                            break
                        else:
                            c=c+1
            else:
                break
    elif  comprobacion=="01111001":
        u=0
        malas= 0
        while u<len(decoded_bits):
            
            if u<len(decoded_bits)-1599:

                deltaT=tiempos_reales[u+1599]-tiempos_reales[u]
                
                if deltaT>0.0015985 and deltaT<0.0015995:
                    print("Trama re valida")
                    current=decoded_bits[u:u+1600]
                    current_processed=[]
                    
                    #Etiqueta -- bits 1-8 -- Casillas 0-7
                    
                    etiqueta = "".join(map(str,current[0:8]))
                    current_processed.append(etiqueta)
                    
                    #Aceptacion -- bits 9-10 -- Casillas 8-9
                    
                    if current[8]==0 and current[9]==0:
                        aceptacion=1 #Fallo de acepacion
                    elif current[8]==1 and current[9]==0:
                        aceptacion=2 #Aceptacion de control 1
                    elif current[8]==0 and current[9]==1:
                        aceptacion=3 #Aceptacion de control 2
                    else:
                        aceptacion=4 #Aceptacion de ambos controles
                    
                    current_processed.append(aceptacion)
                    
                    #Anuncio de modo -- bits 14-18 -- Casillas 13-17
                    anuncio=[]
                    
                    for b in range(0,4):
                        if current[13+b]==1:
                            anuncio.append(b)
                    
                    current_processed.append(anuncio)
                    
                    #Fallos -- bits 19-25 -- Casillas 18-24
                    
                    fallos=[]
                    
                    for x in range(0,7):
                        if current[18+x]==1:
                            fallos.append(x)
                    current_processed.append(fallos)
                    
                    #Operacion -- bits 27-29 -- Casillas 26-28
                    
                    if (current[26]==0 and current[27]==0 and current[28]==0):
                        modo = 0 # STBY
                    elif (current[26]==1 and current[27]==0 and current[28]==0):
                        modo = 1 # Clima
                    elif (current[26]==0 and current[27]==1 and current[28]==0):
                        modo = 2 # Mapa
                    elif (current[26]==1 and current[27]==1 and current[28]==0):
                        modo = 3 # Contorno
                    elif (current[26]==0 and current[27]==0 and current[28]==1):
                        modo = 4 # TEST
                    elif (current[26]==1 and current[27]==0 and current[28]==1):
                        modo = 5 # Turbulencia
                    elif (current[26]==0 and current[27]==1 and current[28]==1):
                        modo = 6 # Clima y turbulencia
                    else:
                        modo = 7 #Calibracion
                        
                    current_processed.append(modo)
                    
                    #Inclinacion -- bits 30-36 -- Casillas 29-35
                    
                    inclinacion = 0
                        
                    current_processed.append(inclinacion)
                    
                    #Ganancia -- bits 37-42 -- Casillas 36-41
                
                    gain= -(current[36]*0.5+current[37]*1+current[38]*2+current[39]*4+current[40]*8+current[41]*16)
                    
                    current_processed.append(gain)
                    
                    #Rango -- bits 43-48 -- Casillas 42-47
                    
                    if (current[42]==1):
                        rango= 5
                    elif (current[43]==1):
                        rango= 10
                    elif (current[44]==1):
                        rango= 20
                    elif (current[45]==1):
                        rango= 40
                    elif (current[46]==1):
                        if (current[47]==1):
                            rango= 240
                        else:
                            rango=80
                    elif (current[47]==1):
                        rango=160
                        
                    current_processed.append(rango)
                    
                    #Barrido -- bits 52-63 -- casillas 51-62
                    
                    barrido=0
                    
                    if (current[62]==1):
                        barrido=barrido-180
                    if (current[61]==1):
                        barrido=barrido+90
                    if (current[60]==1):
                        barrido=barrido+45
                    if (current[59]==1):
                        barrido=barrido+22.5
                    if (current[58]==1):
                        barrido=barrido+11.25
                    if (current[57]==1):
                        barrido=barrido+5.625
                    if (current[56]==1):
                        barrido=barrido+2.8125
                    if (current[55]==1):
                        barrido=barrido+1.40625
                    if (current[54]==1):
                        barrido=barrido+0.703125
                    if (current[53]==1):
                        barrido=barrido+0.3515625

                    if barrido>30:
                        barrido=-30
                    elif barrido<-30:
                        barrido=30
                    current_processed.append(barrido)
                    
                    #Datos -- bits 65-1600  -- Casillas 64-1559 
                    datos=[]
                    
                    for y in range(0,512):
                        if (current[64+3*y]==0 and current[65+3*y]==0 and current[66+3*y]==0):
                            datos.append(0) #0 para negro
                        elif (current[64+3*y]==1 and current[65+3*y]==0 and current[66+3*y]==0):
                            datos.append(1) #1 para verde
                        elif (current[64+3*y]==0 and current[65+3*y]==1 and current[66+3*y]==0):
                            datos.append(2) #2 para amarillo
                        elif (current[64+3*y]==1 and current[65+3*y]==1 and current[66+3*y]==0):
                            datos.append(3) #3 para rojo
                        elif (current[64+3*y]==0 and current[65+3*y]==0 and current[66+3*y]==1):
                            datos.append(4) #4 para magenta
                        elif (current[64+3*y]==1 and current[65+3*y]==0 and current[66+3*y]==1):
                            datos.append(5) #5 para fuera de rango
                        elif (current[64+3*y]==0 and current[65+3*y]==1 and current[66+3*y]==1):
                            datos.append(6) #6 para turbulencia media
                        else:
                            datos.append(7) #7 para turbulencia fuerte
                            
                    current_processed.append(datos)
                    angles.append(current_processed) 
                    u=u+1600
                else:
                    print("Trama no valida")
                    c=u+1
                    malas=malas+1
                    while c<len(decoded_bits):
                        deltica=tiempos_reales[c]-tiempos_reales[u]
                        if deltica> 0.013605 and deltica<0.014555:
                            u=c
                            break
                        else:
                            c=c+1
            else:
                break



    print('fallos: '+ str(malas))
    return angles
        
if __name__=="__main__":
    main()
