from typing import List, Dict, Any
from datetime import datetime

class VtvCabaResponseV2:
    def __init__(self, response_data: Dict[str, Any]):
        self.estado_actual = self.calcular_estado_actual(response_data)
        self.inspecciones = self.procesar_inspecciones(response_data)

    def calcular_estado_actual(self, response_data: Dict[str, Any]) -> str:
        try:
            inspecciones = response_data.get("result", [])
            if not inspecciones:
                return "sin datos"

            # Ordenar por fecha de vencimiento descendente
            inspecciones.sort(key=lambda x: datetime.strptime(x['fechaVencimiento'], "%d/%m/%Y"), reverse=True)
            ultima_vencimiento = inspecciones[0]['fechaVencimiento']
            fecha_vencimiento = datetime.strptime(ultima_vencimiento, "%d/%m/%Y")

            if fecha_vencimiento < datetime.now():
                return "vencida"
            else:
                return "vigente"
        except Exception as e:
            return f"error: {str(e)}"

    def procesar_inspecciones(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            inspecciones = response_data.get("result", [])
            inspecciones_procesadas = [
                {
                    "dominio": inspeccion.get("dominio"),
                    "planta": inspeccion.get("planta"),
                    "fecha_inspeccion": inspeccion.get("fechaInspeccion"),
                    "fecha_vencimiento": inspeccion.get("fechaVencimiento"),
                    "oblea": inspeccion.get("oblea") or None,  # Si oblea está vacío, devolver None
                    "resultado_inspeccion": "Apto" if inspeccion.get("resultadoInspeccion") == "A" else "Condicional",
                    "tipo_inspeccion": inspeccion.get("tipoInspeccion"),
                    "vtuID": inspeccion.get("vtuID"),
                    "traTurno": inspeccion.get("traTurno"),
                    "traKilometraje": inspeccion.get("traKilometraje") or None  # Devolver None si está vacío
                }
                for inspeccion in inspecciones
            ]
            return inspecciones_procesadas
        except Exception as e:
            return [{"error": str(e)}]

    def to_dict(self) -> dict:
        return {
            "estado_actual": self.estado_actual,
            "inspecciones": self.inspecciones
        }
