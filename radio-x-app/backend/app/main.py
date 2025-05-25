from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running!"})

# Point d'entrée principal pour l'exécution directe (optionnel avec flask run)
if __name__ == '__main__':
    # Note: 'flask run' est généralement préféré pour le développement
    # et gunicorn/waitress pour la production.
    # Le host='0.0.0.0' est important pour Docker.
    app.run(host='0.0.0.0', port=5000, debug=True)

