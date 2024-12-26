import asyncio
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper

async def handle_response(pw: PlaywrightWrapper, response):
    # logger.info(f"Interceptando respuesta desde {response.url}")

    if "ObtenerVehiculo" in response.url and response.status == 200:
        try:
            json_data = await response.json()
            pw.responses[response.url] = json_data
            logger.info(f"DATOS CAPTURADOS -> {response.url}")
        except Exception as e:
            logger.error(f"No se pudieron obtener datos desde {response.url}: {e}")

async def solve_captcha(pw):
    retries = 0
    max_retries = 3
    while retries < max_retries:
        is_vehicle_details_visible = await pw.page.locator(
            '.form-group.animate-if:has-text("Detalles del Vehículo")'
        ).is_visible()

        if is_vehicle_details_visible:
            logger.info("[DNRPA] CAPTCHA resuelto con éxito. El contenedor de 'Detalles del Vehículo' es visible.")
            break
        else:
            logger.warning("[DNRPA] CAPTCHA visible, intentando resolución.")
            retries += 1
            await asyncio.sleep(3)
            
            # Resuelve el reCAPTCHA con 2Captcha
            captcha_token = await pw.twocaptcha_solve_recaptcha()
            if not captcha_token:
                logger.error("[DNRPA] No se pudo obtener un token válido de 2Captcha.")
                continue

            # Inyecta el token en el reCAPTCHA
            await pw.page.evaluate(f'document.getElementById("g-recaptcha-response").value="{captcha_token}";')
            await asyncio.sleep(2)
            await pw.page.evaluate('''
                (token) => {
                    const recaptchaTokenField = document.getElementById('g-recaptcha-response');
                    recaptchaTokenField.value = token;
                    recaptchaTokenField.dispatchEvent(new Event('change', { bubbles: true }));
                }
            ''', captcha_token)

            # Intenta hacer clic nuevamente después de inyectar el token
            try:
                await pw.page.click("button.btn.btn-primary:has-text('Validar Vehículo')")
                logger.info("[DNRPA] Botón de Validar Vehículo clickeado después de inyectar el token.")
            except Exception as e:
                logger.error(f"[DNRPA] Error al hacer clic en el botón: {e}")
                await pw.page.screenshot(path="debug_screenshot.png")
                logger.info("[DNRPA] Captura de pantalla tomada para análisis.")

            await asyncio.sleep(5)

    else:
        logger.error("[DNRPA] No se pudo resolver el CAPTCHA después de múltiples intentos.")

async def run(dominio: str):
    numero_documento = "23400111359"

    logger.info(f"DNRPA: Obteniendo información para [{dominio}]")
    pw = PlaywrightWrapper(scraper_name="DNRPA")

    data_captured = False  # Variable de control para salir del loop

    try:
        await pw.start_browser(handle_response)
        await pw.navigate_to("https://www2.jus.gov.ar/dnrpa-site/#!/solicitante")
        await pw.page.click("a.panel-icon:has-text('Informes online')")
        await pw.fill_input("#numeroDocumento", numero_documento)
        await pw.page.click("button.btn.btn-primary:has-text('Buscar Solicitante')")
        await pw.page.click("button.btn.btn-success:has-text('Continuar')")
        await pw.fill_input("#dominio", dominio)

        await pw.page.click("button.btn.btn-primary:has-text('Validar Vehículo')")
        logger.info("[DNRPA] Botón de Validar Vehículo clickeado.")

       # await solve_captcha(pw)
        await pw.solve_recaptcha()

        for attempt in range(10):
            if any("ObtenerVehiculo" in url for url in pw.responses):
                logger.info("Respuesta de ObtenerVehiculo encontrada, saliendo del bucle.")
                data_captured = True
                break
            logger.info("Esperando respuesta del endpoint ObtenerVehiculo...")
            await asyncio.sleep(2 ** attempt)

        if not data_captured:
            logger.error("No se pudo encontrar la respuesta esperada dentro del límite de intentos.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await pw.close_browser()
        return pw.responses

# asyncio.run(run("ouf887"))