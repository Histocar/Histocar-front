import requests
import asyncio
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper
from responses.vtv_caba_response_v2 import VtvCabaResponseV2

VTV_CABA_SITEKEY = "6LcQ9CgTAAAAAN9DPph8J_NivDazqLdb6PdGYPL7"

async def run(dominio: str):
    pw = PlaywrightWrapper(scraper_name="VTV CABA", url="https://www.suvtv.com.ar/historial-turnos/")
    
    # Resolver CAPTCHA y obtener el token
    captcha_token = await pw.twocaptcha_solve_recaptcha(site_key=VTV_CABA_SITEKEY, direct_resolve=False)
    if not captcha_token:
        logger.error("No se pudo obtener un token válido de 2Captcha.")
        return

    # Configurar headers
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.suvtv.com.ar',
        'Referer': 'https://www.suvtv.com.ar/historial-turnos/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    # Configurar los datos de la solicitud
    data = {
        "controllerName": "EstadisticasController",
        "actionName": "getHistorialVtv",
        "dominio": dominio,
        "verify": captcha_token  # Insertar el token de 2Captcha
    }

    try:
        # Realizar la solicitud POST
        response = requests.post("https://www.suvtv.com.ar/controller/ControllerDispatcher.php", headers=headers, data=data)
        
        # Intentar decodificar como JSON, incluso si el Content-Type es incorrecto
        try:
            json_data = response.json()
            logger.info("DATOS CAPTURADOS!")
            return VtvCabaResponseV2(json_data).to_dict()
        except ValueError:
            # Si falla, loguear y forzar a decodificar manualmente el contenido
            logger.warning("Content-Type incorrecto, forzando decodificación de JSON.")
            json_data = response.text  # Decodificar como JSON a partir del texto
            return VtvCabaResponseV2(eval(json_data)).to_dict()

    except Exception as e:
        logger.error(f"No se pudo realizar la solicitud: {e}")

# # Ejecutar la función con el dominio
# dominio = "OUF887"
# result = asyncio.run(run_vtv_caba(dominio))
# logger.info(f"Resultado: {result}")
