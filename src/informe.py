import os
import time
import json
import threading
import asyncio
from flask import Flask, jsonify, request, Response
from scrappers.caba.vtv_caba_scrapper_v2 import run as run_vtv_caba_v2
from scrappers.caba.patente_caba_scrapper_v2 import run as run_patente_caba_v2
from scrappers.dnrpa_datos_principales_v2 import run_dnrpa_info_principal as run_dnrpa_info_principal_v2
from common.logger import logger
from queue import Queue, Empty

# Set event loop policy for threading
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

app = Flask(__name__)

def measure_time(task_name, func, dominio, output_queue):
    start_time = time.time()
    try:
        # Run the asynchronous function synchronously
        result = asyncio.run(func(dominio))
        output_queue.put((task_name, result))
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Tiempo de ejecución de {task_name}: {duration:.2f} segundos")
    except Exception as e:
        logger.error(f"Error in {task_name}: {e}", exc_info=True)
        output_queue.put((task_name, {"error": str(e)}))
        
def generate_historial(dominio):
    try:
        # Run the asynchronous function synchronously
        dnrpa_info_principal = asyncio.run(run_dnrpa_info_principal_v2(dominio))
        if dnrpa_info_principal:
            yield json.dumps({"InfoGeneral": dnrpa_info_principal}) + "\n"
        else:
            logger.error("dnrpa_info_principal is None")
            yield json.dumps({"error": "No se pudo obtener la información de DNRPA"}) + "\n"
            return

        logger.info("Iniciando tareas para PatenteCaba y VtvCaba")
        output_queue = Queue()

        # Iniciar los hilos para las tareas
        patente_thread = threading.Thread(target=measure_time, args=("PatenteCaba", run_patente_caba_v2, dominio, output_queue))
        vtv_thread = threading.Thread(target=measure_time, args=("VtvCaba", run_vtv_caba_v2, dominio, output_queue))

        patente_thread.start()
        vtv_thread.start()

        # Esperar y obtener resultados
        tasks_completed = 0
        last_data_sent = time.time()

        while tasks_completed < 2:
            try:
                task_name, result = output_queue.get(timeout=1)
                yield json.dumps({task_name: result}) + "\n"
                tasks_completed += 1
                last_data_sent = time.time()
            except Empty:
                current_time = time.time()
                if current_time - last_data_sent >= 10:
                    #Enviamos un keep-alive para mantener la conexion viva
                    yield " \n"
                    last_data_sent = current_time

        patente_thread.join()
        vtv_thread.join()

        logger.info("Todas las tareas completadas, enviando estado: completed")
        yield json.dumps({"status": "completed"}) + "\n"

    except Exception as e:
        logger.error(f"Excepción en generate_historial: {e}", exc_info=True)
        yield json.dumps({"error": f"Excepción en generate_historial: {str(e)}"}) + "\n"

@app.route('/historial-stream', methods=['GET'])
def historial_stream():
    dominio = request.args.get('dominio')
    if not dominio:
        logger.warning("El parámetro 'dominio' es requerido y no fue proporcionado")
        return jsonify({"error": "El parámetro 'dominio' es requerido"}), 400

    return Response(generate_historial(dominio), mimetype='text/plain')

@app.route('/ping', methods=['GET'])
def ping():
    logger.info("PING recibido")
    return jsonify({"status": "success", "message": "PONG"}), 200

if __name__ == "__main__":
    logger.info("Iniciando la aplicación Flask en el puerto 18080")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 18080)), threaded=True)
