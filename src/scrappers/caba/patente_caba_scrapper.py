import asyncio
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper
from scrappers.caba.patente_dv_generator import dv_patentes
from responses.patente_caba_response import PatenteCabaResponse

async def handle_response(pw: PlaywrightWrapper, response):
    urls_to_listen = [
        "https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos",
        "https://lb.agip.gob.ar/Empadronados/json/GetPosicionesImpagas",
        "/getKeyC",
        "/getKey.php"
    ]
    
    if any(url in response.url for url in urls_to_listen) and response.status == 200:
        try:
            json_data = await response.json()

            if "getKeyC" in response.url or "getKey.php" in response.url:
                site_key = json_data.get("result")
                if site_key:
                    pw.responses["site_key"] = site_key
                    logger.info(f"[Patente AGIP CABA] Site key capturado desde {response.url}: {site_key}")
                else:
                    logger.error(f"No se pudo obtener el site key desde {response.url}")

            else:
                pw.responses[response.url] = json_data
                logger.info(f"DATOS CAPTURADOS -> {response.url}")

        except Exception as e:
            logger.error(f"Error al procesar la respuesta de {response.url}: {e}")

async def run(dominio: str) -> PatenteCabaResponse:
    logger.info(f"Obteniendo información para el dominio [{dominio}]")
    pw = PlaywrightWrapper(scraper_name="Patente AGIP CABA")

    try:
        await pw.start_browser(handle_response)
        await pw.navigate_to("https://lb.agip.gob.ar/ConsultaPat/")
        await pw.fill_input("#fldDominio", dominio)
        await pw.page.check("#chkDigitoVerificador")

        # Cálculo del dígito verificador
        dv_calculator = dv_patentes()
        dv = dv_calculator["get_dv"](dominio)
        await pw.fill_input("#fldDigitoVerificador", dv)

        # Resolución del reCAPTCHA utilizando 2Captcha
        await pw.capsolver_solve_recaptcha(pw.responses.get("site_key"))
        await pw.page.click("#btnConsultar")
        
        for _ in range(10):  
            if all(url in pw.responses for url in [
                "https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos",
                "https://lb.agip.gob.ar/Empadronados/json/GetPosicionesImpagas"
            ]):
                logger.info("Respuestas encontradas, saliendo del bucle.")
                break
            logger.info("Esperando respuestas de los endpoints...")
            await asyncio.sleep(1)
        else:
            logger.error("No se pudieron encontrar todas las respuestas esperadas dentro del límite de intentos.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await pw.close_browser()

        # Generar el JSON final usando la clase PatenteCabaResponse
        response_data = {
            "PatenteCaba": {
                "https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos": pw.responses.get("https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos"),
                "https://lb.agip.gob.ar/Empadronados/json/GetPosicionesImpagas": pw.responses.get("https://lb.agip.gob.ar/Empadronados/json/GetPosicionesImpagas")
            }
        }
        return PatenteCabaResponse(response_data).to_dict() 
        
