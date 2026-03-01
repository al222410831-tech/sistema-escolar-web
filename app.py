from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_daniel" # Necesario para mostrar mensajes de error

# TU CONEXIÓN
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]
coleccion = db["usuarios"]

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/validar", methods=["POST"])
def validar():
    usuario = request.form.get("usuario")
    
    if usuario.startswith("111"):
        return redirect(url_for("menu_maestro"))
    elif usuario.startswith("222"):
        return redirect(url_for("menu_alumno"))
    else:
        # Si no empieza con esos números, regresa al login con error
        return "<h1>Error: Prefijo no válido. Usa 111 o 222</h1><a href='/'>Volver</a>"

@app.route("/maestro")
def menu_maestro():
    return "<h1>👨‍🏫 Menú de Maestro</h1><p>Bienvenido, tienes acceso total.</p><a href='/'>Cerrar Sesión</a>"

@app.route("/alumno")
def menu_alumno():
    return "<h1>🎓 Menú de Alumno</h1><p>Bienvenido, aquí puedes ver tus notas.</p><a href='/'>Cerrar Sesión</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
