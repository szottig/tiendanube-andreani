from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "andreani-webhook"})

@app.route('/crear_envio', methods=['POST'])
def crear_envio():
    """Endpoint que simula la creación de envío"""
    try:
        data = request.json
        print(f"Recibiendo orden: {data.get('order_id')}")
        
        # SIMULACIÓN - reemplazar con web scraping real después
        tracking_number = f"AN{int(time.time())}{data.get('order_id', '000')[-4:]}"
        
        return jsonify({
            "success": True,
            "tracking_number": tracking_number,
            "etiqueta_pdf": f"https://andreani.com/etiquetas/{tracking_number}.pdf",
            "order_id": data.get('order_id'),
            "message": "Envío simulado - listo para implementar web scraping",
            "nota": "Esta es una simulación. Reemplazar con Selenium/Playwright"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)