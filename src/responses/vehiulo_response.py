from typing import List, Dict, Any
from datetime import datetime
import json

# class Vehiculo:
#     def __init__(self, datos_redes, marca, modelo, radicacion):
#         self.patente = datos_redes.get('dominio', '')
#         self.marca = marca.get('descripcion', '')
#         self.modelo = modelo.get('descripcion', '')
#         self.año = datos_redes.get('anioVehiculo', '')
#         self.tipo = "SEDAN 2 PUERTAS"
#         self.uso = "PRIVADO"
#         self.numero_motor = None
#         self.numero_chasis = None
#         self.marca_motor = self.marca
#         self.marca_chasis = self.marca
#         self.pais_origen = None
#         self.aduana = None
#         self.pais_fabricacion = "REP. FEDERAL DE ALEMANIA"
#         self.radicacion = radicacion

#     def to_json(self):
#         return {
#             "vehiculo": {
#                 "patente": self.patente,
#                 "marca": self.marca,
#                 "modelo": self.modelo,
#                 "año": self.año,
#                 "tipo": self.tipo,
#                 "uso": self.uso,
#                 "numero_motor": self.numero_motor,
#                 "numero_chasis": self.numero_chasis,
#                 "marca_motor": self.marca_motor,
#                 "marca_chasis": self.marca_chasis,
#                 "pais_origen": self.pais_origen,
#                 "aduana": self.aduana,
#                 "pais_fabricacion": self.pais_fabricacion,
#                 "radicacion": self.radicacion
#             }
#         }
