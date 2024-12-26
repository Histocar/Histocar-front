from typing import List, Dict, Any
from datetime import datetime
import json

class VtvCabaResponse:
    def __init__(self, response_data: Dict[str, Any]):
        self.estado_actual = self.calcular_estado_actual(response_data)
        self.inspecciones = self.procesar_inspecciones(response_data)

    def calcular_estado_actual(self, response_data: Dict[str, Any]) -> str:
        try:
            inspecciones = response_data.get("VtvCaba", {}).get("https://www.suvtv.com.ar/controller/ControllerDispatcher.php", {}).get("result", [])
            if not inspecciones:
                return "sin datos"

            inspecciones.sort(key=lambda x: datetime.strptime(x['fechaVencimiento'], "%d/%m/%Y"), reverse=True)
            ultima_vencimiento = inspecciones[0]['fechaVencimiento']
            fecha_vencimiento = datetime.strptime(ultima_vencimiento, "%d/%m/%Y")

            if fecha_vencimiento < datetime.now():
                return "vencida"
            else:
                return "vigente"
        except Exception as e:
            return f"error: {str(e)}"

    def procesar_inspecciones(self, response_data: Dict[str, Any]) -> List[Dict[str, str]]:
        try:
            inspecciones = response_data.get("VtvCaba", {}).get("https://www.suvtv.com.ar/controller/ControllerDispatcher.php", {}).get("result", [])
            inspecciones_procesadas = [
                {
                    "fecha_inspeccion": inspeccion.get("fechaInspeccion"),
                    "fecha_vencimiento": inspeccion.get("fechaVencimiento"),
                    "oblea": inspeccion.get("oblea"),
                    "planta": inspeccion.get("planta"),
                    "resultado_inspeccion": "Apto" if inspeccion.get("resultadoInspeccion") == "A" else "Condicional",
                    "tipo_inspeccion": inspeccion.get("tipoInspeccion")
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


response_data = {
"VtvCaba": {
      "https://www.suvtv.com.ar/controller/ControllerDispatcher.php": {
        "result": [
          {
            "dominio": "OUF887",
            "fechaInspeccion": "26/09/2023",
            "fechaVencimiento": "01/07/2024",
            "oblea": "4068766",
            "planta": "9 de Julio Sur",
            "resultadoInspeccion": "A",
            "tipoInspeccion": "Verificacion",
            "traKilometraje": "",
            "traTurno": "5531064",
            "vtuID": "5531064"
          },
          {
            "dominio": "OUF887",
            "fechaInspeccion": "12/01/2023",
            "fechaVencimiento": "01/07/2023",
            "oblea": "3609470",
            "planta": "9 de Julio Sur",
            "resultadoInspeccion": "A",
            "tipoInspeccion": "Verificacion",
            "traKilometraje": "",
            "traTurno": "4868762",
            "vtuID": "4868762"
          },
          {
            "dominio": "OUF887",
            "fechaInspeccion": "09/02/2021",
            "fechaVencimiento": "04/05/2021",
            "oblea": "",
            "planta": "9 de Julio Sur",
            "resultadoInspeccion": "C",
            "tipoInspeccion": "Verificacion",
            "traKilometraje": "",
            "traTurno": "3052176",
            "vtuID": "3052176"
          },
          {
            "dominio": "OUF887",
            "fechaInspeccion": "09/02/2021",
            "fechaVencimiento": "01/07/2021",
            "oblea": "2193749",
            "planta": "9 de Julio Sur",
            "resultadoInspeccion": "A",
            "tipoInspeccion": "Reverificacion",
            "traKilometraje": "",
            "traTurno": "3109671",
            "vtuID": "3109671"
          },
          {
            "dominio": "OUF887",
            "fechaInspeccion": "31/07/2019",
            "fechaVencimiento": "31/12/2020",
            "oblea": "1485260",
            "planta": "9 de Julio Sur",
            "resultadoInspeccion": "A",
            "tipoInspeccion": "Verificacion",
            "traKilometraje": "",
            "traTurno": "1966917",
            "vtuID": "1966917"
          },
          {
            "dominio": "OUF887",
            "fechaInspeccion": "14/11/2018",
            "fechaVencimiento": "14/07/2019",
            "oblea": "1082700",
            "planta": "Velez Sarsfield",
            "resultadoInspeccion": "A",
            "tipoInspeccion": "Verificacion",
            "traKilometraje": "",
            "traTurno": "1420763",
            "vtuID": "1420763"
          }
        ]
      }
    }
}

# vtv_response = VtvCabaResponse(response_data)
