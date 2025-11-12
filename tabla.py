import Interpretacion as intp
import csv
import numpy as np


with open('tablaDatos.csv','w',newline='') as file:
    writer=csv.writer(file)
    barrido=intp.main()
    
    writer.writerow(["Fecha:"])
    writer.writerow(["Hora:"])


    if barrido[0][0]=="00101101": writer.writerow(["Tipo de barrido:","Horizontal"])
    elif  barrido[0][0]=="01111001": writer.writerow(["Tipo de barrido:","Vertical"])

    inclinacion=barrido[0][5]
    writer.writerow(["Inclinacion:",str(inclinacion)])

    ganancia=barrido[0][6]
    writer.writerow(["Ganancia:",str(ganancia)])

    rango=barrido[0][7]
    writer.writerow(["Rango:",str(rango)])

    writer.writerow(["Angulo"]+[str(num) for num in np.linspace(0,rango,513)][0:512])



    mapeo_colores = {
        0: 'negro',
        1: 'verde',
        2: 'amarillo',
        3: 'rojo',
        4: 'magenta'
    }

    for radio in barrido:
        angulo=radio[8]
        datos=radio[9]
  
        resultado = []
        for numero in datos:
            if numero in mapeo_colores:
                resultado.append(mapeo_colores[numero])
            else:
                resultado.append('desconocido')  # Para números no mapeados
        writer.writerow([str(angulo)]+resultado)
        



