import asyncio
from responses.vtv_caba_response import VtvCabaResponse
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper

async def handle_response(pw: PlaywrightWrapper, response):
    if "https://www.suvtv.com.ar/controller/ControllerDispatcher.php" in response.url and response.status == 200:
        try:
            json_data = await response.json()
            pw.responses[response.url] = json_data
            logger.info(f"DATOS CAPTURADOS -> {response.url}")
        except Exception as e:
            logger.error(f"No se pudieron obtener datos desde {response.url}: {e}")
        
async def run(dominio: str) -> VtvCabaResponse:
    logger.info(f"CABA: Obteniendo información sobre VTV [{dominio}]")
    pw = PlaywrightWrapper(scraper_name="VTV CABA")

    try:
        await pw.start_browser(handle_response)
        await pw.navigate_to("https://www.suvtv.com.ar/historial-turnos/")
        await pw.fill_input("#dominio", dominio)
        await pw.twocaptcha_solve_recaptcha()
        await pw.page.click("a.btnBuscarHistorial")

        for _ in range(10):
            if any("ControllerDispatcher.php" in url for url in pw.responses):
                logger.info("Respuesta encontrada, saliendo del bucle.")
                break
            logger.info("Esperando respuesta del endpoint...")
            await asyncio.sleep(1)
        else:
            logger.error("No se pudo encontrar la respuesta esperada dentro del límite de intentos.")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await pw.close_browser()
        response_data = {
            "VtvCaba": pw.responses
        }
        return VtvCabaResponse(response_data).to_dict() 