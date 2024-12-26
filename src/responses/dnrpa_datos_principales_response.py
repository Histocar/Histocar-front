from typing import Dict, Any

class DnrpaDatosPrincipalesResponse:
    def __init__(self, response_data: Dict[str, Any]):
        self.dominio = response_data.get("dominio", "")
        self.codigo_vehiculo = response_data.get("codigoVehiculo", "")
        self.es_placa_mercosur = response_data.get("esPlacaMercosur", False)
        self.marca = response_data.get("marca", "")
        self.modelo = response_data.get("modelo", "")
        self.anio = response_data.get("anio", 0)
        self.codigo_registro_seccional = response_data.get("codigoRegistroSeccional", 0)
        self.registro_denominacion = response_data.get("registroDenominacion", "")
        self.registro_localidad = response_data.get("registroLocalidad", "")
        self.registro_direccion = response_data.get("registroDireccion", "")
        self.registro_provincia = response_data.get("registroProvincia", "")
        self.turnos = response_data.get("turnos")
        self.titulares = response_data.get("titulares")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominio": self.dominio,
            "codigo_vehiculo": self.codigo_vehiculo,
            "es_placa_mercosur": self.es_placa_mercosur,
            "marca": self.marca,
            "modelo": self.modelo,
            "anio": self.anio,
            "codigo_registro_seccional": self.codigo_registro_seccional,
            "registro_denominacion": self.registro_denominacion,
            "registro_localidad": self.registro_localidad,
            "registro_direccion": self.registro_direccion,
            "registro_provincia": self.registro_provincia,
            "turnos": self.turnos,
            "titulares": self.titulares
        }
