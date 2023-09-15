import os
from flask import Flask, send_from_directory, render_template, Response, jsonify, abort
import subprocess
import sys
import time
import json
import queue
import threading

app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
   return render_template('index.html')

# Queue to store script output
output_queue = queue.Queue()

def run_script():
    try:
        # Execute fantasy_scraper.py in a separate process
        scraper_process = subprocess.Popen(['python', 'fantasy_scraper.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in scraper_process.stdout:
            print(line.strip())
            output_queue.put(line.strip())  # Store the output in the queue

        scraper_process.wait(timeout=300)  # Wait for a specified timeout

        if scraper_process.returncode != 0:
            output_queue.put(f"Error: {scraper_process.stderr.read()}")
    except subprocess.TimeoutExpired:
        output_queue.put("Error: Timeout expired (4 minutes)")
    except Exception as e:
        output_queue.put(f"An exception occurred: {str(e)}")

# Endpoint to start the script
@app.route('/start_script')
def start_script():
    # Start the script in a separate thread
    script_thread = threading.Thread(target=run_script)
    script_thread.start()
    return "Script started.", 300

# Endpoint to get the script output
@app.route('/get_output')
def get_output():
    output_lines = []
    while not output_queue.empty():
        output_lines.append(output_queue.get())
    return jsonify(output=output_lines)


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
