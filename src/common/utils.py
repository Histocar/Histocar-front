import asyncio
from functools import wraps
import time
from common.logger import logger

def retry(retries=3, retry_delay=2, pre_delay=0, timeout=60, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    logger.info(f"[{self.scraper_name}] Ejecutando acción '{func.__name__}'")
                    if timeout:
                        await asyncio.sleep(pre_delay)
                        return await asyncio.wait_for(func(self, *args, **kwargs), timeout=timeout)
                    else:
                        return await func(self, *args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"[{self.scraper_name}] Intento {attempt} fallido para la acción '{func.__name__}'. Error: {e}"
                    )
                    if attempt == retries:
                        logger.error(f"[{self.scraper_name}] La acción '{func.__name__}' ha fallado luego de {retries} intentos.")
                        raise
                    await asyncio.sleep(retry_delay)
                except asyncio.TimeoutError:
                    logger.warning(
                        f"[{self.scraper_name}] La acción '{func.__name__}' superó el tiempo de espera de {timeout} segundos en el intento {attempt}."
                    )
                    if attempt == retries:
                        logger.error(f"[{self.scraper_name}] La acción '{func.__name__}' ha fallado luego de {retries} intentos debido a timeout.")
                        raise

        # @wraps(func)
        # def sync_wrapper(self, *args, **kwargs):
        #     for attempt in range(1, retries + 1):
        #         try:
        #             logger.info(f"[{self.scraper_name}] Ejecutando acción '{func.__name__}'")
        #             return func(self, *args, **kwargs)
        #         except exceptions as e:
        #             logger.warning(
        #                 f"[{self.scraper_name}] Intento {attempt} fallido para la acción '{func.__name__}'. Error: {e}"
        #             )
        #             if attempt == retries:
        #                 logger.error(f"[{self.scraper_name}] La acción '{func.__name__}' ha fallado luego de {retries} intentos.")
        #                 raise
        #             time.sleep(delay)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        # else:
        #     return sync_wrapper

    return decorator
