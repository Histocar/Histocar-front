from typing import Dict, Any

class PatenteCabaResponseV2:
    def __init__(self, response_data: Dict[str, Any]):
        self.deuda_acumulada = self.calcular_deuda_acumulada(response_data)
        self.marca = self.extraer_marca(response_data)
        self.modelo = self.extraer_modelo(response_data)
        self.año = self.extraer_año(response_data)
        self.fecha_patentamiento_inicial = self.extraer_fecha_patentamiento(response_data)
        self.tipo_uso = self.extraer_tipo_uso(response_data)
        self.primer_uso = self.calcular_primer_uso(response_data)
        self.empresa = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {}).get("nombreRazon", "")

    def calcular_deuda_acumulada(self, response_data: Dict[str, Any]) -> float:
        deudas = response_data.get("GetPosicionesImpagas", {}).get("result", {}).get("deudas", [])
        return sum(deuda.get('importeActualizado', 0) for deuda in deudas)

    def extraer_marca(self, response_data: Dict[str, Any]) -> str:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        return cabecera.get('tipoFabrica', {}).get('descripcion', '')

    def extraer_modelo(self, response_data: Dict[str, Any]) -> str:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        modelo = cabecera.get('tipoModeloFabrica', {}).get('descripcion', '')
        marca = cabecera.get('tipoMarca', {}).get('descripcion', '')
        return f"{modelo} {marca}"

    def extraer_año(self, response_data: Dict[str, Any]) -> int:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        return cabecera.get('anioVehiculo', 0)

    def extraer_fecha_patentamiento(self, response_data: Dict[str, Any]) -> str:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        return cabecera.get('fechaAlta', '')

    def extraer_tipo_uso(self, response_data: Dict[str, Any]) -> str:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        return cabecera.get('tipoCodUso', {}).get('descripcion', '')

    def calcular_primer_uso(self, response_data: Dict[str, Any]) -> bool:
        cabecera = response_data.get("GetDatos", {}).get("result", {}).get("cabecera", {})
        anio_vehiculo = cabecera.get('anioVehiculo', 0)
        fecha_alta = cabecera.get('fechaAlta', '')
        anio_patentamiento = int(fecha_alta.split('-')[2]) if fecha_alta else 0
        return anio_vehiculo == anio_patentamiento

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deuda_acumulada": self.deuda_acumulada,
            "marca": self.marca,
            "modelo": self.modelo,
            "año": self.año,
            "fecha_patentamiento_inicial": self.fecha_patentamiento_inicial,
            "tipo_uso": self.tipo_uso,
            "primer_uso": self.primer_uso,
            "empresa": self.empresa
        }
