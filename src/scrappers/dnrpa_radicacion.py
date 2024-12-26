import os
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper

load_dotenv()
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')

def get_captcha_base64():
    url = 'https://www.dnrpa.gov.ar/portal_dnrpa/radicacion2.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    captcha_img = soup.find('img', {'src': lambda x: x and 'data:image/png;base64,' in x})
    if captcha_img:
        captcha_src = captcha_img['src']
        base64_data = captcha_src.split(',')[1]
        return base64_data
    else:
        print('No se encontró la imagen del CAPTCHA.')
        return None
async def solve_captcha_with_2captcha(base64_image):
    url = "http://2captcha.com/in.php"
    data = {
        'key': TWOCAPTCHA_API_KEY,
        'method': 'base64',
        'body': base64_image,
        'json': 1
    }
    
    response = requests.post(url, data=data)
    response_data = response.json()

    # captcha_id = response_data.get('request')
    # pw = PlaywrightWrapper(scraper_name="DNRPA RAD.")
    # await pw.capsolver_solve_recaptcha()
    
    if response_data.get('status') == 1:
        captcha_id = response_data.get('request')
        logger.info(f"Resolviendo CAPTCHA [ID REQ: {captcha_id}]")
        
        url_result = f"http://2captcha.com/res.php?key={TWOCAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1"
        for _ in range(60):
            result_response = requests.get(url_result)
            result_data = result_response.json()
            
            if result_data.get('status') == 1:
                captcha_text = result_data.get('request')
                logger.info(f"CAPTCHA resuelto!")
                return captcha_text
            elif result_data.get('request') == 'CAPCHA_NOT_READY':
                time.sleep(0.5)
            else:
                logger.error(f"Error al resolver el CAPTCHA: {result_data.get('request')}")
                return None
    else:
        logger.error(f"Error al enviar CAPTCHA a 2Captcha: {response_data.get('request')}")
        return None


def obtener_radicacion_data(dominio, captcha_text):
    url = 'https://www.dnrpa.gov.ar/portal_dnrpa/radicacion/consinve_amq.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    data = {
        'dominio': dominio,
        'verificador': captcha_text
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer el tipo de vehículo de manera más robusta
    tipo_vehiculo_tag = soup.find('b', string=lambda x: x and 'Tipo de Vehículo' in x)
    if tipo_vehiculo_tag:
        tipo_vehiculo = tipo_vehiculo_tag.find_next('font').text.strip()
    else:
        tipo_vehiculo = 'No encontrado'

    localidad_tag = soup.find('font', string=lambda x: x and 'Localidad' in x)
    if localidad_tag:
        localidad = localidad_tag.find_next('font').text.strip()
    else:
        localidad = 'No encontrada'

    provincia_tag = soup.find('font', string=lambda x: x and 'Provincia' in x)
    if provincia_tag:
        provincia = provincia_tag.find_next('font').text.strip()
    else:
        provincia = 'No encontrada'

    return {
        'tipo_vehiculo': tipo_vehiculo,
        'localidad': localidad,
        'provincia': provincia
    }


async def get_info_radicacion(dominio):
    base64_image = get_captcha_base64()
    if base64_image:
        captcha_text = await solve_captcha_with_2captcha(base64_image)
        if captcha_text:
            vehicle_details = obtener_radicacion_data(dominio, captcha_text)
            print(f'RADICACIÓN: {dominio}:', vehicle_details)
            return vehicle_details
        else:
            logger.error("Error al obtener info de radicacion")
    else:
        logger.error("Error al obtener info de radicacion")
