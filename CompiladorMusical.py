import os
from mido import MidiFile
from dataclasses import dataclass
import json

@dataclass
class Nota:
    nombre: str
    inicio: int
    duracion_ms: int
@dataclass
class Evento:
    tiempo_ms: int
    tecla_pulsada: str
    accion: str


CarpetaMIDI = 'MIDIs'
MIDIs = os.listdir(CarpetaMIDI)
CarpetaInstrumentos = "Instrumentos"
Instrumentos = os.listdir(CarpetaInstrumentos)
Notas = []
Eventos = []



def Convertir_NotaEvento(NotasDisponibles, Nota):

    if Nota in NotasDisponibles:
        # input(f"Nota correcta encontrada, retornando: {NotasDisponibles[Nota]}")
        return NotasDisponibles[Nota]
    else:
        NotaEquivalente = NotaMasCercana(Nota, NotasDisponibles)
        NotaEquivalente = Convertir_NotaEvento(NotasDisponibles, NotaEquivalente)
        # input(f"Nota incorrecta encontrada, retornando: {NotaEquivalente}")
        return NotaEquivalente

def NotaMasCercana(Nota, NotasDisponibles):
    Nota = Convertir_NotaNumero(Nota)
    mejor_nota = None
    menor_distancia = 999999


    for nota_disponible in NotasDisponibles.keys():

        numero = Convertir_NotaNumero(nota_disponible)
        distancia = abs(numero - Nota)

        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_nota = nota_disponible
    return mejor_nota 

def Convertir_NumeroNota(num):
    nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if isinstance(num, str): 
        return num
    else:
        octava = (num // 12) - 1
        return f"{nombres[num % 12]}{octava}"

def Convertir_NotaNumero(Nota):

    # input(f"La nota que se quiere convertir a número es: {Nota}")

    nombres = {"C":0,"C#":1,"D":2,"D#":3,"E":4,"F":5,"F#":6,"G":7,"G#":8,"A":9,"A#":10,"B":11}
    if isinstance(Nota, int): return Nota


    if "#" in Nota:
        nombre = Nota[:2]
        octava = int(Nota[2:])
    else:
        nombre = Nota[0]
        octava = int(Nota[1:])

    return nombres[nombre] + (octava + 1) * 12

def Convertir_EventoAutoHotKey(Eventos):
    with open(f"{Instrumento.replace(".json", "")}_{Cancion.replace(".mid", "")}_Partitura.ahk", "w", encoding="utf-8") as Archivo:
        TiempoInicial = 0

        # Establecemos una salida de emergencia 
        Archivo.write("Esc::ExitApp\n")
        # Establecemos una tecla para activar todo
        Archivo.write("PgDn::\n")

        #Ordenamos cronológicamente
        Eventos.sort(key=lambda e: (e.tiempo_ms, 0 if e.accion == 'Up' else 1))
        EstadoTeclas = {}

        for Evento in Eventos:
            tecla = Evento.tecla_pulsada
            if not tecla: continue 
            
            if tecla not in EstadoTeclas:
                EstadoTeclas[tecla] = 0

            escribir_evento = False

            # Lógica estricta de hardware
            if Evento.accion == 'Down': 
                if EstadoTeclas[tecla] == 0:
                    escribir_evento = True
                EstadoTeclas[tecla] += 1
                
            elif Evento.accion == 'Up':
                if EstadoTeclas[tecla] > 0:
                    EstadoTeclas[tecla] -= 1
                if EstadoTeclas[tecla] == 0:
                    escribir_evento = True

           # Escritura en AHK
            if escribir_evento:
                if Evento.tiempo_ms > TiempoInicial: 
                    Archivo.write(f"Sleep, {Evento.tiempo_ms - TiempoInicial}\n")
                    TiempoInicial = Evento.tiempo_ms
                
                # Si el tiempo es exacto al actual, se escribe sin Sleep (simultáneo)
                Archivo.write(f"Send, {{{tecla} {Evento.accion}}}\n")

# Aquí voy a poner la interfaz de selección inicial ----------------------------------------------------------------

print('\nLa lista de canciones es: ')
for i, Cancion in enumerate(MIDIs): print(f'{i}.- {Cancion}')
Cancion = int(input('Ingrese el número de la canción que va a querer:  '))
Cancion = MIDIs[Cancion]

print('\nLa lista de Instrumentos es: ')
for i, Instrumento in enumerate(Instrumentos): 
    print(f'{i}.- {Instrumento}')
print('\n')
Instrumento = int(input('Ingrese el número de Instrumento con el que vamos a trabajar:  '))
Instrumento = Instrumentos[Instrumento]

print("\nLa lista de velocidades disponibles: ")
print("1.- Normal")
print("2.- 1.5")
print("3.- 2")
FactorVelocidad = float(input("Respuesta:  "))

# -------------------------------------------------------------------------------------------------------------------
NotasDisponibles = {}
with open(f"Instrumentos/{Instrumento}", "r", encoding="utf-8") as Archivo:
    NotasDisponibles = json.load(Archivo);

mid = MidiFile(f'MIDIs/{Cancion}')

tiempo_acumulado = 0.0
notas_activas = {}  # diccionario: {note_number: tiempo_inicio}

print(f"Canción: {mid.filename}")
print("Formato: tiempo_inicio_ms -> nota (duración_ms)")
print()

for msg in mid:
    tiempo_acumulado += msg.time
    
    # Note_on con velocity > 0 = inicio de nota
    if msg.type == 'note_on' and msg.velocity > 0:
        # MANDAMOS EL DOWN INMEDIATAMENTE
        Eventos.append(Evento(int(tiempo_acumulado * 1000 * FactorVelocidad), Convertir_NotaEvento(NotasDisponibles, msg.note), 'Down'))
        
        # Usamos listas en el diccionario para guardar superposiciones sin sobrescribir
        if msg.note not in notas_activas:
            notas_activas[msg.note] = []
        notas_activas[msg.note].append(tiempo_acumulado)
    
    # Note_off o note_on con velocity 0 = fin de nota
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        # MANDAMOS EL UP SIEMPRE (Esto arregla los Sleeps masivos)
        tiempo_fin_ms = int(tiempo_acumulado * 1000 * FactorVelocidad)
        Eventos.append(Evento(tiempo_fin_ms, Convertir_NotaEvento(NotasDisponibles, msg.note), 'Up'))
        
        # Calculamos la duración solo para imprimir en consola
        if msg.note in notas_activas and len(notas_activas[msg.note]) > 0:
            inicio = notas_activas[msg.note].pop(0) # Sacamos el tiempo más antiguo
            duracion = tiempo_acumulado - inicio
            ms_inicio = int(inicio * 1000 * FactorVelocidad)
            ms_duracion = int(duracion * 1000 * FactorVelocidad)
            nota = Convertir_NumeroNota(msg.note)
            Notas.append(Nota(nota, ms_inicio, ms_duracion))
            print(f"{ms_inicio} ms -> {nota} (dura {ms_duracion} ms)")



input('Presiona Enter para imprimir las notas desde dataclases en Notas.')
for Nota in Notas:
    print(f'{Nota.nombre}, en {Nota.inicio}, durante {Nota.duracion_ms}')

input('Presiona Enter para imprimir las notas desde dataclases en eventos.')
for Evento in Eventos:
    if Evento.accion == 'Up':
        print(f'En {Evento.tiempo_ms} se pulsa: {Evento.tecla_pulsada} hacia: Arriba ({Evento.accion})')
    else:
        print(f'En {Evento.tiempo_ms} se pulsa: {Evento.tecla_pulsada} hacia: Abajo ({Evento.accion})')

input()
Convertir_EventoAutoHotKey(Eventos) 

