import asyncio
import aiohttp
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper
from responses.patente_caba_response_v2 import PatenteCabaResponseV2
from scrappers.caba.patente_dv_generator import dv_patentes
import json

# Definir el sitekey correcto para el reCAPTCHA
CABA_SITEKEY = "6Lex5EkUAAAAAIGTKhHNPHpn7G6l4CHdTuhyidrP"

async def run(dominio: str):
    pw = PlaywrightWrapper(scraper_name="Patente CABA", url="https://lb.agip.gob.ar/ConsultaPat/")
    dv_calculator = dv_patentes()
    dv = dv_calculator["get_dv"](dominio)
    
    # Resolver CAPTCHA y obtener el token
    captcha_token = await pw.twocaptcha_solve_recaptcha(site_key=CABA_SITEKEY, direct_resolve=False)
    if not captcha_token:
        logger.error("No se pudo obtener un token válido de 2Captcha.")
        return

    # Configurar headers comunes
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://lb.agip.gob.ar',
        'Referer': 'https://lb.agip.gob.ar/ConsultaPat/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Realizar la primera solicitud a GetDatos
        data_get_datos = {
            "dominio": dominio,
            "dv": dv,
            "recaptcha_response_field": captcha_token
        }
        try:
            async with session.post("https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos", data=data_get_datos) as response_datos:
                response_datos.raise_for_status()
                json_data_datos = await response_datos.json(content_type=None)
                logger.info("DATOS CAPTURADOS -> GetDatos")
        except Exception as e:
            logger.error(f"Error en la solicitud GetDatos: {e}")
            return

        # Realizar la segunda solicitud a GetPosicionesImpagas
        data_get_posiciones = {
            "codImpuesto": "8",
            "anioInicio": "2023",
            "dominioI": dominio,
            "dv": dv
        }
        try:
            async with session.post("https://lb.agip.gob.ar/Empadronados/json/GetPosicionesImpagas", data=data_get_posiciones) as response_posiciones:
                response_posiciones.raise_for_status()
                json_data_posiciones = await response_posiciones.json(content_type=None)
                logger.info("DATOS CAPTURADOS -> GetPosicionesImpagas")
        except Exception as e:
            logger.error(f"Error en la solicitud GetPosicionesImpagas: {e}")
            return

    # Combinar los resultados y devolver la respuesta estructurada
    combined_data = {
        "GetDatos": json_data_datos,
        "GetPosicionesImpagas": json_data_posiciones
    }
    return PatenteCabaResponseV2(combined_data).to_dict()

# Ejemplo de uso
if __name__ == "__main__":
    # Ejecutar la función principal
    dominio = "ABC123"
    asyncio.run(run(dominio))
