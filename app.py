from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# CONFIGURACIÓN DE MONGODB
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]
usuarios_col = db["usuarios"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    try:
        # Usamos .get() para que si no existe el campo, no de error
        matricula = request.form.get("matricula")
        nombre = request.form.get("nombre")
        password = request.form.get("password", "12345") # Si no hay pass, pone 12345 por default
        
        datos = {
            "matricula": matricula,
            "nombre": nombre,
            "password": password
        }

        if matricula.startswith("111"):
            datos["rol"] = "maestro"
            datos["materia1"] = request.form.get("materia1")
            datos["materia2"] = request.form.get("materia2")
            datos["semestre"] = request.form.get("semestre_maestro")
        elif matricula.startswith("222"):
            datos["rol"] = "alumno"
            datos["semestre"] = request.form.get("semestre_alumno")
        else:
            return "<h1>⚠️ Matrícula debe iniciar con 111 o 222</h1><a href='/registro'>Volver</a>"

        usuarios_col.insert_one(datos)
        return "<h1>✅ Registro exitoso en SIAGE</h1><a href='/'>Volver al Inicio</a>"
    except Exception as e:
        return f"<h1>❌ Error al guardar: {e}</h1><a href='/registro'>Reintentar</a>"

if __name__ == "__main__":
    # Render necesita el host 0.0.0.0 y el puerto de la variable de entorno
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
