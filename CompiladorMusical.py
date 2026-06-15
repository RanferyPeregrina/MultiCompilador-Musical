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

def Convertir_NotaEvento(Instrumento, Nota):

    Nota = Convertir_NumeroNota(Nota)
    with open(f"Instrumentos/{Instrumento}", "r") as Archivo:
        Instrumento = json.load(Archivo)
        Nota = Instrumento.get(Nota, "")

    return Nota

def Convertir_NumeroNota(num):
    nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if isinstance(num, str): return num
    else:octava = (num // 12) - 1
    return f"{nombres[num % 12]}{octava}"



print('\nLa lista de canciones es: ')
for i, Cancion in enumerate(MIDIs): print(f'{i}.- {Cancion}\n')
Cancion = int(input('Ingrese el número de la canción que va a querer:  '))
Cancion = MIDIs[Cancion]

print('\nLa lista de Instrumentos es: ')
for i, Instrumento in enumerate(Instrumentos): 
    print(f'{i}.- {Instrumento}')
print('\n')
Instrumento = int(input('Ingrese el número de Instrumento con el que vamos a trabajar:  '))
Instrumento = Instrumentos[Instrumento]



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
        notas_activas[msg.note] = tiempo_acumulado
        Eventos.append(Evento(int(tiempo_acumulado * 1000), Convertir_NotaEvento(Instrumento, msg.note), 'Down'))
    
    # Note_off o note_on con velocity 0 = fin de nota
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in notas_activas:
            inicio = notas_activas.pop(msg.note)
            duracion = tiempo_acumulado - inicio
            ms_inicio = int(inicio * 1000)
            ms_duracion = int(duracion * 1000)
            nota = Convertir_NumeroNota(msg.note)
            print(f"{ms_inicio} ms -> {nota} (dura {ms_duracion} ms)")
            Notas.append(Nota(nota, ms_inicio, ms_duracion))
            Eventos.append(Evento(ms_inicio, Convertir_NotaEvento(Instrumento, nota), 'Up'))


# Al final, si quedan notas activas (MIDI mal cerrado)
for note, inicio in notas_activas.items():
    duracion = tiempo_acumulado - inicio
    print(f"{int(inicio*1000)} ms -> {Convertir_NumeroNota(note)} (dura {int(duracion*1000)} ms, nota sin cierre)")

input('Presiona Enter para imprimir las notas desde dataclases en Notas.')
for Nota in Notas:
    print(f'{Nota.nombre}, en {Nota.inicio}, durante {Nota.duracion_ms}')

input('Presiona Enter para imprimir las notas desde dataclases en eventos.')
for Evento in Eventos:
    if Evento.accion == 'Up':
        print(f'En {Evento.tiempo_ms} se pulsa: {Evento.tecla_pulsada} hacia: Arriba ({Evento.accion})')
    else:
        print(f'En {Evento.tiempo_ms} se pulsa: {Evento.tecla_pulsada} hacia: Abajo ({Evento.accion})')

