import requests
import asyncio
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper
from responses.dnrpa_datos_principales_response import DnrpaDatosPrincipalesResponse

DNRPA_SITEKEY = "6Ld5ZjUUAAAAAJ7zlNNbYOQ9REJyT9LeFH13N-We"

async def run_dnrpa_info_principal(dominio: str):
    pw = PlaywrightWrapper(scraper_name="DNRPA", url="https://www2.jus.gov.ar/dnrpa-site/#!/solicitante")
    
    captcha_token = await pw.twocaptcha_solve_recaptcha(site_key=DNRPA_SITEKEY, direct_resolve=False)
    if not captcha_token:
        logger.error("No se pudo obtener un token válido de 2Captcha.")
        return

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': '_ga=GA1.1.1416281915.1730818842; _ga_J6SKH403RR=GS1.1.1730818841.1.0.1730818847.0.0.0; IDNODO=.cluster3',
        'Origin': 'https://www2.jus.gov.ar',
        'Referer': 'https://www2.jus.gov.ar/dnrpa-site/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    data = {
        "Dominio": dominio,
        "CodigoTramite": None,
        "ObtenerTurnosDelRegistro": False,
        "ObtenerTiposTramitesTipoDespachoRecibirEmail": True,
        "EsMandatario": False,
        "RecaptchaResponse": captcha_token
    }

    try:
        response = requests.post("https://www2.jus.gov.ar/dnrpa-site/api/site/ObtenerVehiculo", headers=headers, json=data)
        response.raise_for_status()
        
        if response.status_code == 200:
            json_data = response.json()
            logger.info("DATOS CAPTURADOS ->", json_data)
            return DnrpaDatosPrincipalesResponse(json_data).to_dict()
        else:
            logger.error(f"Error en la solicitud: {response.status_code}")
    except Exception as e:
        logger.error(f"No se pudo realizar la solicitud: {e}")
