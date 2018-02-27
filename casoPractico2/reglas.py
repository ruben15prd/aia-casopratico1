import prestamos
import titanic
import votos
import math
import copy
import collections
import sys



class Clasificador:
    def __init__(self,clasificacion,clases,atributos):
        self.clasificacion=clasificacion
        self.clases=clases
        self.atributos=atributos
        self.reglas = None
        self.diccionarioDistribucionClases = None
        
    def entrena(self,entrenamiento,validacion=None,prepoda = 1, listaIndicesAtributos = None):
        
        if listaIndicesAtributos == None:
            self.reglas = aprendeReglasEntrenamiento(entrenamiento,self.atributos,list(range(len(self.atributos))),self.clases,prepoda)  
        else:
            self.reglas = aprendeReglasEntrenamiento(entrenamiento,self.atributos,listaIndicesAtributos,self.clases,prepoda)  
            
        
        self.diccionarioDistribucionClases = diccionarioNumeroElementosClase(entrenamiento,self.clases)
        #print("Reglas antes de la poda:")
        #print( str(self.reglas))
        
        if validacion != None:
            #print("Reglas despues de la pospoda:")
            self.reglas = pospoda(self.reglas,validacion,self.diccionarioDistribucionClases)
           
    def clasifica(self,ejemplo):
        res = clasificaElemento(self.reglas,ejemplo,self.diccionarioDistribucionClases)
        return res
        
    def evalua(self,prueba):
        rendimiento = evaluaAux(self.diccionarioDistribucionClases,self.reglas,prueba)
        return rendimiento 
        
    def imprime(self):
        diccionarioDistribucionClasesCopia = copy.deepcopy(self.diccionarioDistribucionClases)
        contador = 0
        while len(diccionarioDistribucionClasesCopia) > 0:
            claveMinima = obtenClaveMinimaPorValor(diccionarioDistribucionClasesCopia)
            diccionarioDistribucionClasesCopia.pop(claveMinima, None)
            print("Reglas aprendidas para la clase: " +  claveMinima + "\n")
            
            reglasClave = self.reglas[contador]
            for regla in reglasClave:
                print(str(regla))
            print("\n\n")
            contador += 1 



#Una regla es una lista de tuplas ([(indiceAtributo,valor)] ,clasificacion)
def reglaCubreElemento(regla, elemento):
    """Metodo que comprueba si una regla cubre a un elemento"""
    cubre = 1
    
    if len(regla[0]) == 0:
        cubre = 0
        
    else:
    
        for condicion in regla[0]:
        
            indiceAtributo = condicion[0]
            valorAtributo = condicion[1]
        
            if valorAtributo != elemento[indiceAtributo]:
                cubre = 0
            
    return cubre



def reglaCubreCorrectamenteElemento(regla, elemento):
    """Metodo que comprueba si una regla cubre correctamente a un elemento"""
    cubre = 1
    
    if len(regla[0]) == 0:
        cubre = 0
    else:
        for condicion in regla[0]:
            
            indiceAtributo = condicion[0]
            valorAtributo = condicion[1]
            valorClasificacion = regla[1]
            #print("----")
            #print(str(indiceAtributo))
            #print(str(valorAtributo))
            #print(str(valorClasificacion))
            if valorAtributo != elemento[indiceAtributo] or valorClasificacion != elemento[len(elemento) - 1] :
                cubre = 0
    
    return cubre



# Eliminamos los elementos cubiertos por la regla
def numeroElementosCubiertos(regla, elementos): 
    """Metodo que devuelve el numero de elementos cubiertos por una regla"""
    numeroCubiertos = 0
    
    for e in elementos:
        if reglaCubreElemento(regla,e) == 1:
            numeroCubiertos += 1
            
    return numeroCubiertos

def numeroElementosCubiertosCorrectamente(regla, elementos):
    """Metodo que devuelve el numero de elementos cubiertos correctamente por una regla"""
    numeroCubiertosCorrectamente = 0
    
    for e in elementos:
        if reglaCubreCorrectamenteElemento(regla,e) == 1:
            numeroCubiertosCorrectamente += 1
            
    return numeroCubiertosCorrectamente


                
def frecuenciaRelativa(regla,entrenamiento):
    """Metodo que calcula la frecuencia relativa de una regla en el conjunto de entrenamiento"""
    
    '''
    FR(S,R) = p/t p= numero de ejemplos cubiertos por R de S, t = numero de ejemplos cubiertos correctamente por R de S
    ''' 
    t = numeroElementosCubiertos(regla,entrenamiento)
    p = numeroElementosCubiertosCorrectamente(regla,entrenamiento)
    
    #print("numerosCubiertosCorrectamente: " + str(p))
    #print("numerosCubiertos: " + str(t))
    
    if t != 0:
        frecuenciaRelativa = p/t
    else:
        frecuenciaRelativa = 0
    
    return frecuenciaRelativa



def aprendeConjuntoReglasClase(entrenamiento,atributos,indicesAtributos,clase, umbralPrepoda):
    """Metodo que aprende un conjunto de reglas para una clase"""
    entrenamientoCopia = copy.deepcopy(entrenamiento)
    atributosCopia = copy.deepcopy(atributos)
    reglas = []
    
    longitudElementosClase = len(filtraEntrenamientoPorClase(entrenamientoCopia,clase))
    
    #while frecuenciaRelativaReglaTotal < umbralPrepoda and longitudElementosClase > 1:
    
    
    while longitudElementosClase > 0:
        #print("longitud:" + str(longitudElementosClase))
        #print("-------------------")
        #print("longitudElementosClase :" + str(longitudElementosClase))
        #print("-----------------------------------")
        resultado = aprendeRegla(entrenamientoCopia,atributosCopia,indicesAtributos,clase, umbralPrepoda)
        #print(str(resultado[1]))
        #print("regla :" + str(resultado[1]))
        entrenamientoCopia = copy.deepcopy(resultado[0])
        #atributosCopia = copy.deepcopy(resultado[1])
        #print(str(resultado[1][0]))
        if len(resultado[1][0]) > 0: 
            reglas.append(resultado[1])
        #print(str(resultado[1]))
        longitudElementosClase = len(filtraEntrenamientoPorClase(entrenamientoCopia,clase))
        #print("entro :" + str(longitudElementosClase))
        #print("entro :" + str(len(entrenamientoCopia)))
    #print(str(reglas))
    return reglas



def aprendeReglasEntrenamiento(entrenamiento,atributos,indicesAtributos,clases, umbralPrepoda):
    """Metodo que aprende las reglas para el conjunto de entrenamiento"""
    diccionarioDistribucionClases = diccionarioNumeroElementosClase(entrenamiento,clases)
    reglasClases = []
    
    while len(diccionarioDistribucionClases) > 0:
        
        claveMinima = obtenClaveMinimaPorValor(diccionarioDistribucionClases)
        diccionarioDistribucionClases.pop(claveMinima, None)
        resultado = aprendeConjuntoReglasClase(entrenamiento,atributos,indicesAtributos,claveMinima, umbralPrepoda)
        reglasClases.append(resultado)
        #print(str(reglasClases))
    #print(str(reglasClases))
    return reglasClases



def obtenClaveMinimaPorValor(diccionarioDistribucionClases):
    """Metodo que obtiene el valor de clasificacion de la clase que menos aparece"""
    min_value = 9223372036854775807
    for key in diccionarioDistribucionClases:
        if min_value is None or min_value > diccionarioDistribucionClases[key]:
            min_value = diccionarioDistribucionClases[key]
            min_key = key  
            
    return min_key



def diccionarioNumeroElementosClase(entrenamiento,clases):
    """Metodo que devuelve el numero de elementos de cada clase"""
    frecuenciaClasificacionClases = {}
    for clase in clases:
        frecuenciaClasificacionClases[clase] = 0
        #print(str(clase))
    for elem in entrenamiento:
        claseElemento = elem[len(elem) -1]
        frecuenciaClasificacionClases[claseElemento] += 1
    
    return frecuenciaClasificacionClases



def elementosPorCubrirRegla(regla,elementos):
    """Metodo que devuelve el numero de elementos que faltan por cubrir dado una regla"""
    elementosPorCubrir = []
    
    for e in elementos:
        if reglaCubreElemento(regla,e) == 0:
            elementosPorCubrir.append(e)    
            
    return elementosPorCubrir




def filtraEntrenamientoPorClase(entrenamiento,clase):
    """Metodo que devuelve las filas de ejemplos que pertecen a una clase"""
    filtrado = []
    
    for e in entrenamiento:
        if e[len(e) - 1] == clase:
            filtrado.append(e)
            
    return filtrado


def aprendeRegla(entrenamiento,atributos,indicesAtributos,clase, umbralPrepoda):
    """Metodo que aprende una regla para una clase"""
    regla = ([],clase)
    #print("longitud entrenamiento: " + str(entrenamiento))
    #print("longitud entrenamiento: " + str(len(entrenamiento)))
    #print("atributos: " + str(atributos))
    entrenamientoCopia = copy.deepcopy(entrenamiento)
    atributosCopia = copy.deepcopy(atributos)
    indicesAtributosCopia = copy.deepcopy(indicesAtributos)
   
    #regla = ([(0,"jubilado")],"estudiar")
    
    #['jubilado','ninguno','ninguna','uno','soltero','altos','estudiar']
    frecuenciaRelativaReglaTotal = 0
    #print("atr: " + str(atributos))
    #print("indices antes: " + str(indicesAtributosCopia))
    
    #Añadir la condicion que cuando se quede sin atributos devolver la regla
    while frecuenciaRelativaReglaTotal < umbralPrepoda and len(indicesAtributosCopia) > 0:
        #print("frecuencia Relativa :" + str(frecuenciaRelativaReglaTotal))
        frecuenciaRelativaReglaActual = 0
         # Esta variable nos almacena la regla que mejor frecuencia relativa tiene
        #en cada iteracion
        #Iteramos los atributos 
        regla_max = ([],clase)
        #print("indicesAtr: " + str(indicesAtributosCopia))
        
        #print("--------------------------------------------------------------------------------------")
        #print("regla: " + str(regla))
        for indiceAtributo in indicesAtributosCopia:
            #print("----------------------------------------")
            #print("regla : " + str(regla))
            atr = atributosCopia[indiceAtributo][1]
            #print(str(atr))
            #print("-----------------------------------------------")
            #print("indices: " + str(indicesAtributosCopia))
            # Iteramos los atributos restantes  
            #print("-----------------------------------------------")
            for valorAtributo in atr:
                #print(str(valorAtributo))
                regla_aux = copy.deepcopy(regla)
                regla_aux[0].append((indiceAtributo,valorAtributo))
                #print("aux: "+str(regla_aux))
                #print("--------------")
                #print("frecuencia regla total:" + str(frecuenciaRelativaReglaTotal))
                #print("regla temporal:" + str(regla_aux))
                frecuenciaRelativaReglaMax = frecuenciaRelativa(regla_aux,entrenamientoCopia)
                #print("frecuencia regla actual: "+str(frecuenciaRelativaReglaMax))
                #print("frecuencia regla maxima: " + str(frecuenciaRelativaReglaActual))
                if frecuenciaRelativaReglaMax >= frecuenciaRelativaReglaActual:
                    #Copiamos el valor de la regla_aux a regla_max
                    #print("Se cambia la regla:" + str(regla_max))
                    regla_max = copy.deepcopy(regla_aux)
                    frecuenciaRelativaReglaActual = frecuenciaRelativaReglaMax
            #print("frecuencia regla total del atributo " + str(indiceAtributo) + ": " + str(frecuenciaRelativaReglaTotal))
            #print("-----------------------------------------------")
        #print("*******************")
        #Si la reglaMax era mejor que la regla actual se sustituye su valor por la regla con 
        #nuevas condiciones
        #print(str(regla_max))
        
        if frecuenciaRelativaReglaActual > frecuenciaRelativaReglaTotal:
            #Guardamos en nuestra regla actual la regla con maxima frecuencia
            regla = copy.deepcopy(regla_max)
            ultimaReglaAñadida = regla[0][-1]
            indiceUltimaReglaAñadida = ultimaReglaAñadida[0]
            valorUltimaReglaAñadida = ultimaReglaAñadida[1]
            atributosCopia[indiceUltimaReglaAñadida][1].remove(valorUltimaReglaAñadida)
            indicesAtributosCopia.remove(indiceUltimaReglaAñadida)
            frecRegla =  frecuenciaRelativa(regla,entrenamientoCopia)
            #print("tmp: " + str(frecRegla))
            #Actualizamos la frecuencia relativa total
            frecuenciaRelativaReglaTotal = frecRegla
            
        elif frecuenciaRelativaReglaActual == frecuenciaRelativaReglaTotal:
            indicesAtributosCopia.remove(indiceAtributo)
            
            #print("regla ultima: " + str(ultimaReglaAñadida))    
            #print("atributosCopia: " + str(atributosCopia))
            
    #Nos quedamos con los elementos no cubiertos correctamente
    #print("len: " + str(len(regla[0])))
    if len(regla[0]) >= 1:
        entrenamientoCopia = elementosPorCubrirRegla(regla,entrenamientoCopia)
    '''
    print("regla: " + str(regla))
    
    print("")
    print("entrenamientoCopia: " + str(entrenamientoCopia))
    print("")
    print("longitud entrenamiento: " + str(len(entrenamiento)))
    print("")
    print("longitud entrenamientoCopia: " + str(len(entrenamientoCopia)))
    print("")
    print("regla: " + str(regla))
    print("----------------------")
    '''
    return (entrenamientoCopia,regla)



def pospoda(reglas,validacion,diccionarioDistribucionClases):
    """Metodo de poda de reglas"""
    reglasCopia = copy.deepcopy(reglas)
    
    reglasFinales = podaReglasConjunto(reglasCopia, validacion, diccionarioDistribucionClases)
    
    
    
    return reglasFinales 



def podaReglasConjunto(reglas, validacion, diccionarioDistribucionClases):
    """Metodo que elimina reglas o la ultima condicion de la misma de un conjunto de reglas"""
    
    reglasFinales = copy.deepcopy(reglas)
    rendimientoFinal = evaluaPoda(diccionarioDistribucionClases, reglasFinales, validacion) # Evalua el rendimiento antes de la poda
    #print("REGLAS FINALES : " + str(reglasFinales))
    # Eliminar una condicion 
    reglaModificada = None
    for conjuntoReglas in reglasFinales:
        
        for regla in conjuntoReglas:
            
            reglaModificada = copy.deepcopy(regla)
            longitud = len(reglaModificada[0]) # Longitud de las condiciones
            if longitud > 1:
                #print("--------------------------")
                #print("regla antes: "+ str(reglaModificada))
                reglaModificada = eliminaCondicion(reglaModificada) 
                #print("regla despues: "+ str(reglaModificada))
                #print("CONJUNTO ANTES:\n"+ str(conjuntoReglas))
                nuevoConjuntoReglas = reemplazaRegla(reglasFinales,regla, reglaModificada)
                #print("CONJUNTO DESPUES:\n"+ str(nuevoConjuntoReglas))
                rendimiento = evaluaPoda(diccionarioDistribucionClases,nuevoConjuntoReglas,validacion)
                #print("rendimiento Antes: "+ str(rendimientoFinal))
                #print("rendimiento despues: "+ str(rendimiento))
                if rendimiento > rendimientoFinal:
                    reglasFinales = nuevoConjuntoReglas
                    rendimientoFinal = rendimiento
                        
                       
    #Eliminar una regla
    for conjuntoReglas in reglasFinales:
        
        for regla in conjuntoReglas:
            #print("CONJUNTO ANTES:\n"+ str(conjuntoReglas))
            nuevoConjuntoReglas = eliminaRegla(reglasFinales,regla)
            #print("CONJUNTO DESPUES:\n"+ str(nuevoConjuntoReglas))
            
            rendimiento = evaluaPoda(diccionarioDistribucionClases,nuevoConjuntoReglas,validacion)
            #print("rendimiento Antes: "+ str(rendimientoFinal))
            
            if rendimiento > rendimientoFinal:
                reglasFinales = nuevoConjuntoReglas
                rendimientoFinal = rendimiento   
         
    
    #print("rendimiento despues: "+ str(rendimientoFinal))
    
    
    return reglasFinales


def reemplazaRegla(reglas,reglaOriginal, reglaSustitucion):
    """"Metodo que devuelve el conjunto de reglas sustituyendo la reglaOriginal por la reglaSustitucion"""
    copiaReglas = copy.deepcopy(reglas)
    reglasFinal = []
    
    # Se recorre la lista que contiene las listas de reglas de cada clase
    for conjuntoReglasClase in copiaReglas:
        cReglasClase = []
        for regla in conjuntoReglasClase:
        
            #print("regla: " +str(regla))
            if compruebaReglasIguales(regla,reglaOriginal) == 1:
                #print("entro en el if")
                cReglasClase.append(reglaSustitucion)
                
            else:
                #print("entro en el else")
                cReglasClase.append(regla)
        reglasFinal.append(cReglasClase)
    
    return reglasFinal



def eliminaRegla(reglas,reglaAEliminar):
    """Elimina una regla del conjunto de reglas"""
    copiaReglas = copy.deepcopy(reglas)
    reglasFinal = []
    
    
    # Se recorre la lista que contiene las listas de reglas de cada clase
    for conjuntoReglasClase in copiaReglas:
        cReglasClase = []
        
        for regla in conjuntoReglasClase:
            
            if compruebaReglasIguales(regla,reglaAEliminar) == 0:
                cReglasClase.append(regla)
            
        reglasFinal.append(cReglasClase)     
               
    return reglasFinal



def compruebaReglasIguales(regla1,regla2):
    """Comprueba si dos reglas son iguales"""
    contador = 0 
    
    igual = 1
    while contador <= 1:
        if regla1[contador] != regla2[contador]:
            igual = 0
        contador = contador + 1
    
    return igual
    
    

def eliminaCondicion(regla):
    """Elimina una condicion de una regla"""
    reglaModificada = ([],regla[1])
    
    reglaCopia = copy.deepcopy(regla)
    
    
    condiciones = reglaCopia[0]
    condiciones.pop()
    
    for condicion in condiciones:
        reglaModificada[0].append(condicion)
    
    return reglaModificada



def clasificaElemento(reglas,ejemplo,diccionarioDistribucionClases):
    """Metodo que clasifica un ejemplo dado"""
    diccionarioDistribucionClasesCopia = copy.deepcopy(diccionarioDistribucionClases)
    #print("reglas: " + str(reglas))
    
    res = 0
    contador = 0
    while len(diccionarioDistribucionClasesCopia) > 0:
        claveMinima = obtenClaveMinimaPorValor(diccionarioDistribucionClasesCopia)
        #print(claveMaxima)
        diccionarioDistribucionClasesCopia.pop(claveMinima, None)
            
        reglasClave = reglas[contador]
            
            
        for regla in reglasClave:
            clasifica = 1
            #print("clasifica: " + str(clasifica))
            #print("regla: " + str(regla))
            #print("regla de 0: " + str(regla[0]))
                
            for condicion in regla[0]:
                #print("condicion: " + str(condicion))
                indice = condicion[0]
                valorRegla = condicion[1]
                #print("indice: " + str(condicion[0]) + "valor: " + str(condicion[1]))
                #print("ejmplo:"  + str(ejemplo))
                if ejemplo[indice] != valorRegla:
                    clasifica = 0
                    
            if clasifica == 1:
                #Se obtiene el valor de clasificacion
                res = 1
                return regla[1]
                    
            
        contador += 1 
        
    if res == 0:
        #Se asigna el valor de clasificacion dominante
        return reglas[len(reglas)-1][-1][1]



def evaluaAux(diccionarioDistribucionClases,reglas,prueba):
    """Metodo para evaluar un conjunto de prueba"""
    aciertos = 0
    numTotal = len(prueba)
    for p in prueba:
        clasificacionArbol = clasificaElemento(reglas,p,diccionarioDistribucionClases)
        if clasificacionArbol == p[len(p) - 1]:
            aciertos = aciertos + 1
        
    rendimiento = aciertos/numTotal
    print("El rendimiento es: " + str(rendimiento) + "\n" + "\n")
    return rendimiento



def evaluaPoda(diccionarioDistribucionClases,reglas,prueba):
    """Metodo para evaluar desde el metodo de la pospoda"""
    aciertos = 0
    numTotal = len(prueba)
        
    for p in prueba:
        #print("p: " + str(p[0:len(p)- 1]))
        #print("reglas: " + str(reglas))
        #print("elemento a evaluar: " + str(p[0:len(p)- 1]))
        clasificacionArbol = clasificaElemento(reglas,p[0:len(p)- 1],diccionarioDistribucionClases)
        
        
        if clasificacionArbol == p[len(p) - 1]:
            aciertos = aciertos + 1
        
    rendimiento = aciertos/numTotal
    #print("El rendimiento es: " + str(rendimiento))
    return rendimiento


#res = clasificador1.clasifica(['laboral','dos o más','una','uno','soltero','bajos'])
#print("El valor de clasificacion para el ejemplo es: " + str(res))

#clasificador1.evalua(prestamos.prueba)



#Funciones:
#Aprende una regla para un conjunto de entrenamiento
#Aprende varias reglas para un conjunto de entrenamiento
#Aprende varias reglas para varios conjuntos de entrenamiento

# En primer caso hay que ver que los elementos que cubra la regla sean cubiertos correctamente
# En el segundo caso hay que ver que que cubra correctamente todos los elementos de la clase 
# En el tercer caso habria que llamar al segundo caso para cada una de las posibles clases

# Si agotamos los atributos estamos poniendo un ejemplo
# Para la poda se puede o bien eliminar una regla o eliminar una condicion de la regla, habra que ir calculando
# todas las posibles combinaciones y quedarnos con aquellos que clasifiquen mejor el conjunto de prueba
# Si hay un empate en el numero de elementos que recubren varias reglas nos quedamos con aquella que cubra mas ejemplos   
'''
g = numeroElementosCubiertos(([(0, 'parado'),(5, 'bajos')], 'conceder'),prestamos.entrenamiento1)
l = numeroElementosCubiertosCorrectamente(([(0, 'parado'),(5, 'bajos')], 'conceder'),prestamos.entrenamiento1)
print("g: " + str(g))
print("l: " + str(l))
woo = elementosPorCubrirRegla(([(0, 'parado'),(5, 'bajos')], 'conceder'),prestamos.entrenamiento1)
print("lol: " + str(woo))
print("len entrenamiento: " + str(len(woo)))
'''


#res =  aprendeRegla(prestamos.entrenamiento1,prestamos.atributos,[0,1,2,3,4,5],"conceder", 1)
#res2 = aprendeConjuntoReglasClase(prestamos.entrenamiento1,prestamos.atributos,[0,1,2,3,4,5],"conceder", 1)
#print("res: " + str(res))

#res = aprendeConjuntoReglasClase(prestamos.entrenamiento1,prestamos.atributos,[0,1,2,3,4,5],"conceder", 1)
#print("resultado: " + str(res))


#res = compruebaReglasIguales(([(0, 'parado'),(5, 'bajos')], 'conceder'),([(1, 'uno'),(5, 'bajos')], 'conceder'))

#res = eliminaCondicion(([(0, 'parado')], 'conceder'))  

#print(str(res))


#res = compruebaReglasIguales(([(0, 'parado'),(5, 'bajos')], 'conceder'),([(0, 'parado')], 'conceder'))
#print(str(res))


#Prestamos
print("*********************************************************")
print("*-*-*-*-*-*-*-*-*- REGLAS DE PRESTAMOS -*-*-*-*-*-*-*-*-*")
print("*********************************************************")
clasificador3 = Clasificador("",prestamos.clases,prestamos.atributos)
clasificador3.entrena(prestamos.entrenamiento,prestamos.validacion,1)
clasificador3.imprime()
res = clasificador3.clasifica(['jubilado','ninguno','ninguna','uno','soltero','altos'])
print("El valor de clasificacion para el ejemplo es: " + str(res))
clasificador3.evalua(prestamos.prueba)



#Votos
print("*********************************************************")
print("*-*-*-*-*-*-*-*-*-*- REGLAS DE VOTOS -*-*-*-*-*-*-*-*-*-*")
print("*********************************************************")
clasificador2 = Clasificador("",votos.clases,votos.atributos)
clasificador2.entrena(votos.entrenamiento,votos.validacion,1)
clasificador2.imprime()
res = clasificador2.clasifica(['n','s','n','s','s','s','n','n','n','s','?','s','s','s','n','s'])
print("El valor de clasificacion para el ejemplo es: " + str(res))
clasificador2.evalua(votos.prueba)



#Titanic
print("*********************************************************")
print("*-*-*-*-*-*-*-*-*-* REGLAS DE TITANIC *-*-*-*-*-*-*-*-*-*")
print("*********************************************************")
indicesAtributosTitanicSeleccionados =  [1,3,9]
atributosSeleccionados = [titanic.atributos[i] for i in indicesAtributosTitanicSeleccionados]

clasificador1 = Clasificador("",titanic.clases,titanic.atributos)
clasificador1.entrena(titanic.entrenamiento,titanic.validacion,1,[1,3,9])
clasificador1.imprime()
res = clasificador1.clasifica(["1","1st","Cardeza, Mrs James Warburton Martinez (Charlotte Wardle Drake)","adulto","Cherbourg","Germantown, Philadelphia, PA","B-51/3/5","17755 L512 6s","3","female"])
print("El valor de clasificacion para el ejemplo es: " + str(res))
clasificador1.evalua(titanic.prueba)












 