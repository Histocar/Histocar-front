import asyncio
from common.logger import logger
from common.playwright_wrapper import PlaywrightWrapper

async def run():
    logger.info(f"CAPTCHA TEST STARTED")
    pw = PlaywrightWrapper(scraper_name="CAPTCHA TEST")

    try:
        await pw.start_browser()
        await pw.navigate_to("https://www.google.com/recaptcha/api2/demo")
        await pw.solve_recaptcha()
        await pw.page.click("recaptcha-demo-submit")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await pw.close_browser()
        return pw.responses 

asyncio.run(run())
