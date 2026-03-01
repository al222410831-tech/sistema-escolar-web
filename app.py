from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# TU CONEXIÓN A MONGODB
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]
usuarios_col = db["usuarios"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    matricula = request.form.get("matricula")
    nombre = request.form.get("nombre")
    password = request.form.get("password")
    
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
        return "<h1>Matrícula inválida</h1><a href='/registro'>Volver</a>"

    usuarios_col.insert_one(datos)
    return "<h1>✅ Registro exitoso en SIAGE</h1><a href='/'>Ir al Inicio</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
