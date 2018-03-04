# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 11:23:54 2018

@author: Ruben
"""

# -*- coding: utf-8 -*-
import votos
import random
import copy
from random import shuffle
import random
import math

class clasificador:
    def __init__(self,clases,norm=False): # norm = valor_columna_ejemplo-media_columna/desv. tipica
        self.clases = clases
        self.norm = norm
        self.pesosFinales = None
    
    def entrena(self,entr,clas_entr,n_epochs,rateInicial=0.1,pesos_iniciales=None,rate_decay=False):
        pesosW = []
        
        if pesos_iniciales == None:
            pesosW = generaListaPesosAleatoriosW(len(entr[0]) +1,-1.0,1.0)
        else:
            pesosW = pesos_iniciales
            
        pesosW = entrenaAux(pesosW,entr,clas_entr,n_epochs,rateInicial,self.clases,rate_decay)
        
        
        self.pesosFinales = pesosW
        
        print("Los pesos obtenidos son: " + str(self.pesosFinales))
        return pesosW
    
    # Devuelve la probabilidad de pertenecer a la clase 1. No se usa en el perceptrón.
    def clasifica_prob(self,ej):
        pass
    
    def clasifica(self,ej):
        clasificacion = clasificaAux(self.pesosFinales,ej,self.clases)
        
        print("El valor de clasificacion es: " + str(clasificacion))
        
        return clasificacion
    
    def evalua(self,prueba,clasesPrueba):
        rendimiento = evaluaAux(self.pesosFinales,prueba,self.clases,clasesPrueba)
        return rendimiento 

def evaluaAux(pesos,prueba,diccionarioMapeoClases,clasesEntrenamiento):
    """Metodo para evaluar un conjunto de prueba"""
    aciertos = 0
    numTotal = len(prueba)
    contadorEjemplo = 0
    for p in prueba:
        #print("p: " + str(p))
        clasificacion = clasificaAux(pesos,p,diccionarioMapeoClases)
        #print("clase predecida: " + str(clasificacion))
        #print("clase original: " + str(clasesEntrenamiento[contadorEjemplo]))
        if clasificacion == clasesEntrenamiento[contadorEjemplo]:
            aciertos = aciertos + 1
        contadorEjemplo += 1
    rendimiento = aciertos/numTotal
    print("El rendimiento es: " + str(rendimiento) + "\n" + "\n")
    return rendimiento
    
       
def clasificaAux(pesosFinales,ejemplo,clases):
    """Funcion de clasificacion auxiliar"""
    suma = 0
    # Añadimos X0 = 1 al ejemplo
    ejemploCopia = [1] + ejemplo
    contador = 0
    while contador < len(pesosFinales):
        wi = pesosFinales[contador]
        xi = ejemploCopia[contador]
        suma = suma + (wi*xi)
        
        contador += 1
        
    res = sigma(suma)
    
    
    if res < 0.5:
        clasificacion = clases[0]
        
    else:
        clasificacion = clases[1]
        
    return clasificacion

def entrenaAux(pesosW,entr,clas_entr,n_epochs,rate,clases,rateDecay):
    """Funcion de entrenamiento"""
    
    #print("len:"  +str(len(entr)))
    indicesRestantes = list(range(len(entr)))
    #print(str(indicesRestantes))
    rateActual = rate
    contadorNumEpochs = 0
    while contadorNumEpochs < n_epochs:
        
        while len(indicesRestantes) > 0:
            indice = random.choice(indicesRestantes)
            #print("random:" + str(indice))
            # Añadimos X0 = 1 al ejemplo
            ejemploAdd = [1] + entr[indice]
                
            pesosW = actualizaPesosEjemplo(pesosW,ejemploAdd,rateActual,clases,clas_entr,indice)
            
            indicesRestantes.remove(indice)
        contadorNumEpochs += 1
        
        #Disminuimos el rate si nos indican rateDecay = 1
        if rateDecay == True:
            rateActual = rate + (2/(calculaRaiz(contadorNumEpochs**2,3)))
        
    return pesosW

    
def sigma(x):
    """Funcion umbral"""
    resultado = 1/(1 + math.exp(-x))
        
    return resultado

def generaListaPesosAleatoriosW(longitudAGenerar,limiteInferior,limiteSuperior):
    """Genera la lista W de pesos aleatorios entre 2 limites"""
    W = []
    
    while longitudAGenerar > 0:
        aleatorio = random.uniform(limiteInferior, limiteSuperior)
        
        W.append(aleatorio)
        longitudAGenerar -= 1
    return W


def actualizaPesosEjemplo(listaPesosW,ejemplo,rate,clases,listaClasesEntrenamiento,indiceEjemplo):
    """Actualiza la lista de pesos W, dado un ejemplo(recordar que este ejemplo tiene que incorporar X0)"""
    '''wi = wi + η*(xi(y-o)*o*(1-o))'''
    pesosActualizados=[]
    
    
    
    longitudEjemplo = len(ejemplo)
    
    contador = 0
    while contador < longitudEjemplo:
        Xi = ejemplo[contador]
        Wi = listaPesosW[contador]
            
        clasificacionEjemplo = listaClasesEntrenamiento[indiceEjemplo]
        #y = diccionarioClases[clasificacionEjemplo]
        y = clases.index(clasificacionEjemplo)
        WixXi = Xi * Wi
        #print(str(WixXi))
        o = sigma(WixXi)
        
        WiFinal = Wi + ((rate*Xi)*(y - o)*o*(1 - o))
        pesosActualizados.append(WiFinal)
            
        contador += 1
        
    return pesosActualizados

def calculaRaiz(x,raiz):
    result = x**(1.0/float(raiz))
    
    return result

clasificador1 = clasificador(votos.votos_clases)
clasificador1.entrena(votos.votos_entr,votos.votos_entr_clas,1000,rateInicial=0.1,pesos_iniciales=None,rate_decay=True)
clasificador1.clasifica([-1,1,-1,1,1,1,-1,-1,-1,-1,-1,1,1,1,-1,0])
clasificador1.evalua(votos.votos_test,votos.votos_test_clas)

'''
ejemplo = [-1,1,-1,1,1,1,-1,-1,-1,1,0,1,1,1,-1,1]
print("ejemplo a pelo: "  + str(ejemplo))
ejemploAdd = generaListaElementoX(ejemplo)
print("ejemplo add: "  + str(ejemploAdd))
print("len ejemplo add: "  + str(len(ejemploAdd)))

listaPesosAleatoria = generaListaPesosAleatoriosW(len(ejemploAdd))
print("listaPesosAleatoria: "  + str(listaPesosAleatoria))
print("len lista pesos aleatoria: "  + str(len(listaPesosAleatoria)))


res = actualizaPesosEjemplo(listaPesosAleatoria,ejemploAdd,0.1,votos.votos_clases,votos.votos_entr_clas,1)
print("resutlado : " + str(res))
'''