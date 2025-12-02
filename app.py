from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def setup_driver():
    """Configurar Chrome para Render"""
    chrome_options = ChromeOptions()
    
    # Configuración para Render/entornos headless
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent real
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error configurando driver: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servicio está funcionando"""
    return jsonify({
        "status": "healthy",
        "service": "andreani-webhook",
        "timestamp": time.time()
    })


@app.route('/crear_envio', methods=['POST'])
def crear_envio():
    """Endpoint principal para crear envíos en Andreani (simulado)"""
    start_time = time.time()
    
    try:
        # 1. Validar datos JSON recibidos
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No se recibieron datos JSON"
            }), 400

        # Asegurar que order_id siempre es string
        order_id = str(data.get('order_id', 'unknown')).strip()
        logger.info(f"Iniciando creación de envío para orden: {order_id}")

        # 2. Validar campos requeridos
        required_fields = ['destinatario', 'direccion', 'localidad', 'codigo_postal', 'telefono']
        missing_fields = []

        for field in required_fields:
            raw_value = data.get(field)

            # Caso 1: None
            if raw_value is None:
                missing_fields.append(field)
                continue

            # Convertir siempre a string
            value = str(raw_value).strip()

            # Caso 2: vacío o inválido
            if value == "" or value.lower() in ["no informado", "null", "none"]:
                missing_fields.append(field)

        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Campos requeridos faltantes o inválidos: {missing_fields}",
                "order_id": order_id,
                "received_data": {
                    k: (str(v)[:50] + "...") if len(str(v)) > 50 else str(v)
                    for k, v in data.items()
                }
            }), 400

        # 3. Simulación con Selenium
        driver = None
        try:
            driver = setup_driver()
            driver.implicitly_wait(10)

            logger.info("Simulando creación de envío...")

            # Limpiar order_id para generar tracking
            order_id_clean = ''.join(filter(str.isdigit, order_id))
            order_id_suffix = order_id_clean[-6:] if order_id_clean and len(order_id_clean) >= 6 else "000000"

            tracking_number = f"AND{int(time.time())}{order_id_suffix}"

            time.sleep(1)

            datos_recibidos = {
                k: (str(v)[:100] + "...") if len(str(v)) > 100 else str(v)
                for k, v in data.items()
            }

            result = {
                "success": True,
                "tracking_number": tracking_number,
                "etiqueta_pdf": f"https://andreani.com/etiqueta/{tracking_number}.pdf",
                "seguimiento_url": f"https://seguimiento.andreani.com/#/{tracking_number}",
                "order_id": order_id,
                "datos_recibidos": datos_recibidos,
                "message": "Envío simulado creado exitosamente",
                "nota": "Implementar web scraping real para Andreani",
                "tiempo_procesamiento": round(time.time() - start_time, 2)
            }

            logger.info(f"Envío simulado creado: {tracking_number}")
            return jsonify(result)

        except Exception as e:
            logger.error(f"Error durante la creación del envío: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Error en el proceso: {str(e)}",
                "order_id": order_id,
                "tiempo_procesamiento": round(time.time() - start_time, 2)
            }), 500

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    except Exception as e:
        logger.error(f"Error general en el endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
