import os
from flask import Flask, send_from_directory, render_template, Response, jsonify, abort
import subprocess
import sys
import time
import json
import fantasy_scraper

app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/start_script')
def start_script():
    def run_script():
        fantasy_scraper.main(True, fantasy_scraper.TOTAL_JUGADORES)

    return Response(run_script(), content_type='text/plain')


@app.route('/<path:path>/<path:filename>')
def serve_player_data_file(path, filename):
    return serve_json_file(path, filename)



def serve_json_file(path, filename):
    # Construye la ruta completa al archivo JSON
    full_path = os.path.join(path, filename)

    try:
        # Abre el archivo JSON y carga su contenido
        with open(full_path, 'r') as file:
            data = json.load(file)

        # Devuelve el contenido del archivo JSON como una respuesta JSON
        return jsonify(data)
    except FileNotFoundError:
        # Maneja el error si el archivo no se encuentra
        abort(404)
    except Exception as e:
        # Maneja otros errores, como problemas de lectura del archivo
        return f"Error: {str(e)}", 500
    

if __name__ == "__main__":
    app.run(debug=True)
