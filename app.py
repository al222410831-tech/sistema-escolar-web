from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Esta es la pantalla principal igual a tu captura
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/validar", methods=["POST"])
def validar():
    usuario = request.form.get("usuario")
    if usuario.startswith("111"):
        return redirect(url_for("menu_maestro"))
    elif usuario.startswith("222"):
        return redirect(url_for("menu_alumno"))
    else:
        return "<h1>Error: Prefijo no válido (Usa 111 o 222)</h1><a href='/login'>Volver</a>"

@app.route("/maestro")
def menu_maestro():
    return render_template("menu_maestro.html")

@app.route("/alumno")
def menu_alumno():
    return render_template("menu_alumno.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
