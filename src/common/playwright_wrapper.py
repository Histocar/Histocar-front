import asyncio
import aiohttp
import requests
import time
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright_recaptcha import recaptchav2
from undetected_playwright import stealth_async
from common.logger import logger
from common.utils import retry

load_dotenv()
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')
CAPSOLVER_API_KEY = os.getenv('CAPSOLVER_API_KEY')

class PlaywrightWrapper:
    def __init__(self, url=None, scraper_name=""):
        self.playwright_context = None
        self.headless = False
        self.browser = None
        self.context = None
        self.page = None
        self.url = url
        self.responses = {}
        self.scraper_name = scraper_name

    async def start_browser(self, handle_response=None):
        self.playwright_context = await async_playwright().start()
        self.browser = await self.playwright_context.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await stealth_async(self.page)

        if handle_response:
            async def on_response(response):
                await handle_response(self, response)

            self.page.on("response", on_response)

    @retry(retries=3, retry_delay=2, pre_delay=3)
    async def solve_recaptcha(self):
        logger.info(f"[{self.scraper_name}] Resolviendo reCAPTCHA")
        solver = recaptchav2.AsyncSolver(self.page)
        await solver.__aenter__()
        try:
            await solver.solve_recaptcha()
            logger.info(f"[{self.scraper_name}] reCAPTCHA Resuelto!")
        finally:
            await solver.__aexit__(None, None, None)

    async def get_site_key(self):
        """Obtiene el sitekey del reCAPTCHA presente en la página."""
        try:
            site_key = await self.page.get_attribute("div.g-recaptcha", "data-sitekey")
            if site_key:
                logger.info(f"[{self.scraper_name}] Site key obtenido: {site_key}")
                return site_key
            else:
                logger.error(f"[{self.scraper_name}] No se pudo obtener el site key.")
                return None
        except Exception as e:
            logger.error(f"[{self.scraper_name}] Error al obtener el sitekey: {e}")
            return None    

    @retry(retries=2, retry_delay=5, pre_delay=0)
    async def twocaptcha_solve_recaptcha(self, site_key=None, direct_resolve=True):
        try:
            logger.warning(f"[{self.scraper_name}] Resolviendo reCAPTCHA (2Captcha)")
            
            if site_key is None:
                site_key = await self.get_site_key()
            
            if not site_key:
                logger.error(f"[{self.scraper_name}] No se puede proceder sin el site key")
                return None

            async with aiohttp.ClientSession() as session:
                async with session.post("http://2captcha.com/in.php", data={
                    'key': TWOCAPTCHA_API_KEY,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': getattr(self.page, 'url', self.url) if hasattr(self, 'page') and self.page else self.url
                }) as response:
                    text_response = await response.text()
                    
                    if "OK" not in text_response:
                        logger.error(f"[{self.scraper_name}] Error en la respuesta de 2Captcha: {text_response}")
                        return None

                    try:
                        captcha_id = text_response.split('|')[1]
                    except IndexError:
                        logger.error(f"[{self.scraper_name}] Respuesta inesperada: {text_response}")
                        return None

                while True:
                    async with session.get(f"http://2captcha.com/res.php?key={TWOCAPTCHA_API_KEY}&action=get&id={captcha_id}") as response:
                        text_response = await response.text()

                        if 'CAPCHA_NOT_READY' in text_response:
                            continue

                        if 'OK' in text_response:
                            captcha_token = text_response.split('|')[1]
                            break

                        logger.error(f"[{self.scraper_name}] Error en la respuesta del token de CAPTCHA: {text_response}")
                        return None
                if direct_resolve:
                    await self.page.evaluate(f'document.getElementById("g-recaptcha-response").value="{captcha_token}";')
                    await asyncio.sleep(2)

                    await self.page.evaluate('''
                        (token) => {
                            const recaptchaTokenField = document.getElementById('g-recaptcha-response');
                            recaptchaTokenField.value = token;
                            recaptchaTokenField.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    ''', captcha_token)

                    logger.info(f"[{self.scraper_name}] CAPTCHA Resuelto! (2Captcha)")
                    return None
                else:
                    return captcha_token

        except Exception as e:
            logger.error(f"[{self.scraper_name}] Error al resolver CAPTCHA: {str(e)}")

    @retry(retries=2, retry_delay=5, pre_delay=5)
    async def capsolver_solve_recaptcha(self, site_key=None):
        try:
            logger.warning(f"[{self.scraper_name}] Resolviendo reCAPTCHA (CAPSOLVER)")

            if site_key is None:
                site_key = await self.get_site_key()

            if not site_key:
                logger.error(f"[{self.scraper_name}] No se puede proceder sin el site key")
                return None

            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.capsolver.com/createTask", json={
                    'clientKey': CAPSOLVER_API_KEY,
                    'task': {
                        'type': 'RecaptchaV2TaskProxyless',
                        'websiteURL': self.page.url,
                        'websiteKey': site_key
                    }
                }) as response:
                    if response.headers.get("Content-Type") != "application/json":
                        logger.error(f"[{self.scraper_name}] Respuesta inesperada de CAPSOLVER: {await response.text()}")
                        return None
                    
                    json_response = await response.json()

                    if json_response.get("errorId") != 0:
                        logger.error(f"[{self.scraper_name}] Error en la respuesta de CAPSOLVER: {json_response}")
                        return None

                    captcha_id = json_response.get("taskId")

                while True:
                    async with session.post("https://api.capsolver.com/getTaskResult", json={
                        'clientKey': CAPSOLVER_API_KEY,
                        'taskId': captcha_id
                    }) as response:
                        # Verificar si la respuesta tiene el formato JSON
                        if response.headers.get("Content-Type") != "application/json":
                            logger.error(f"[{self.scraper_name}] Respuesta inesperada de CAPSOLVER: {await response.text()}")
                            return None

                        json_response = await response.json()

                        if json_response.get("status") == "idle":
                            logger.info(f"[{self.scraper_name}] Tarea en estado 'idle'. Esperando para reintentar...")
                            await asyncio.sleep(5)
                            continue

                        if json_response.get("status") == "processing":
                            await asyncio.sleep(5)
                            continue

                        if json_response.get("status") == "ready":
                            captcha_token = json_response["solution"]["gRecaptchaResponse"]
                            break

                        logger.error(f"[{self.scraper_name}] Error en la respuesta del token de CAPTCHA: {json_response}")
                        return None

                await self.page.evaluate(f'document.getElementById("g-recaptcha-response").value="{captcha_token}";')
                await asyncio.sleep(2)

                await self.page.evaluate('''
                    (token) => {
                        const recaptchaTokenField = document.getElementById('g-recaptcha-response');
                        recaptchaTokenField.value = token;
                        recaptchaTokenField.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                ''', captcha_token)

                logger.info(f"[{self.scraper_name}] CAPTCHA Resuelto! (CAPSOLVER)")

        except Exception as e:
            logger.error(f"[{self.scraper_name}] Error al resolver CAPTCHA: {str(e)}")

    @retry(retries=3, retry_delay=10) 
    async def check_site_availability(self, url, timeout=5):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        logger.info(f"[{url}] está accesible.")
                        return True
                    else:
                        logger.warning(f"[{url}] no está accesible. Estado: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error al verificar la disponibilidad de [{url}]: {e}")
            return False
        
    @retry(retries=3, retry_delay=15)
    async def navigate_to(self, url):
        logger.info(f"[{self.scraper_name}] Navegando a {url}")
        await self.page.goto(url)

    async def navigate_with_check(self, url):
        if await self.check_site_availability(url):
            await self.navigate_to(url)
        else:
            logger.error(f"No se pudo navegar a {url} porque no está accesible después de varios intentos.")

    @retry(retries=3, retry_delay=2)
    async def fill_input(self, selector, value):
        try:
            await self.page.wait_for_selector(selector, state='visible')
            logger.info(f"[{self.scraper_name}] Llenando input {selector} con el valor: {value}")
            await self.page.fill(selector, value)
            logger.info(f"[{self.scraper_name}] Input {selector} llenado exitosamente.")
        except Exception as e:
            logger.error(f"[{self.scraper_name}] Error al llenar el input {selector}: {e}")
            raise

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
        if self.playwright_context:
            await self.playwright_context.stop()
