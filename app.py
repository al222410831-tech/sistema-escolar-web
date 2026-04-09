from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# CONEXIÓN MONGODB ATLAS
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]

# COLECCIONES SEPARADAS
usuarios_col = db["usuarios"]
calif_col = db["calificaciones"]
reportes_col = db["reportes"]
horarios_col = db["horarios"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route('/validar', methods=['POST'])
def validar():
    matricula = request.form.get('matricula')
    password = request.form.get('password')
    
    # Buscamos al usuario en la base de datos
    user = usuarios_col.find_one({'matricula': matricula, 'password': password})

    if user:
        # --- BLOQUE DE AUTOMATIZACIÓN PARA SPARK ---
        import datetime
        log_login = {
            "matricula": user.get('matricula'),
            "nombre": user.get('nombre'),
            "rol": user.get('rol'),
            "evento": "Inicio de Sesión",
            "gateway": "200.0.0.1",
            "status": "Online",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Guardamos en la colección que vigila el monitor_iot.py
        db["logs_asistencia"].insert_one(log_login)
        # --------------------------------------------

        # Lógica para redireccionar según el rol
        if user.get("rol") == "maestro":
            semestre_n = user.get("semestre", "N/A")
            alumnos = list(usuarios_col.find({"rol": "alumno", "semestre": semestre_n}))
            return render_template("menu_maestro.html", user=user, alumnos=alumnos, horarios_col=horarios_col)
        
        elif user.get("rol") == "alumno":
            notas = list(calif_col.find({"matricula": matricula}))
            reps = list(reportes_col.find({"matricula": matricula}))
            return render_template("menu_alumno.html", user=user, notas=notas, reportes=reps, horarios_col=horarios_col)
        
        else:
            # Por si tienes algún otro rol como admin
            return render_template("menu_alumno.html", user=user)

    # Si los datos son incorrectos
    return '<h1>❌ Datos incorrectos</h1><p>Matrícula o contraseña no válidos.</p><a href="/login">Volver a intentar</a>'def validar():

    matricula = request.form.get("usuario")
    password = request.form.get("password")
    user = usuarios_col.find_one({"matricula": matricula, "password": password})
    
    if user:
import datetime
        log_login = {
            "nombre": user.get('nombre', 'Usuario'),
            "rol": user.get('rol', 'Alumno/Maestro'),
            "evento": "Inicio de Sesión",
            "gateway": "200.0.0.1",
            "status": "Online",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db["logs_asistencia"].insert_one(log_login)
        if user.get("rol") == "maestro":
            semestre_m = user.get("semestre", "N/A")
            alumnos = list(usuarios_col.find({"rol": "alumno", "semestre": semestre_m}))
            # FIX: Pasamos horarios_col al maestro para evitar Error 500
            return render_template("menu_maestro.html", user=user, alumnos=alumnos, horarios_col=horarios_col)
        else:
            notas = list(calif_col.find({"matricula": matricula}))
            reps = list(reportes_col.find({"matricula": matricula}))
            # Pasamos horarios_col al alumno para que vea su tabla
            return render_template("menu_alumno.html", user=user, notas=notas, reportes=reps, horarios_col=horarios_col)
    
    return "<h1>❌ Datos incorrectos</h1><a href='/login'>Volver</a>"

@app.route("/guardar_materia", methods=["POST"])
def guardar_materia():
    matri = request.form.get("matricula")
    materia = request.form.get("materia_nombre")
    try:
        n1, n2, n3, n4 = float(request.form.get("n1", 0)), float(request.form.get("n2", 0)), float(request.form.get("n3", 0)), float(request.form.get("n4", 0))
        promedio = round((n1 + n2 + n3 + n4) / 4, 2)
        calif_col.update_one({"matricula": matri, "materia": materia}, {"$set": {"n1": n1, "n2": n2, "n3": n3, "n4": n4, "promedio": promedio}}, upsert=True)
        
        rep_txt = request.form.get("reporte")
        if rep_txt:
            reportes_col.update_one({"matricula": matri, "materia": materia}, {"$set": {"texto": rep_txt}}, upsert=True)
        return render_template("exito.html", mensaje="Datos de alumno guardados", destino="panel")
    except:
        return "<h1>❌ Error en los datos</h1><a href='/'>Volver</a>"

@app.route("/guardar_horario", methods=["POST"])
def guardar_horario():
    cuatri = request.form.get("cuatrimestre")
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
    for dia in dias:
        bloques = {}
        for i in range(1, 18):
            valor = request.form.get(f"{dia}_bloque_{i}")
            if valor:
                bloques[f"bloque_{i}"] = valor
        if bloques:
            update_fields = {f"bloques.{k}": v for k, v in bloques.items()}
            horarios_col.update_one({"cuatrimestre": cuatri, "dia": dia}, {"$set": update_fields}, upsert=True)
    return render_template("exito.html", mensaje="Horario semanal actualizado", destino="panel")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    matricula = request.form.get("matricula")
    datos = {"matricula": matricula, "nombre": request.form.get("nombre"), "password": request.form.get("password")}
    if matricula.startswith("111"):
        datos.update({"rol": "maestro", "materia1": request.form.get("materia1"), "materia2": request.form.get("materia2"), "semestre": request.form.get("semestre_maestro")})
    else:
        datos.update({"rol": "alumno", "semestre": request.form.get("semestre_alumno")})
    usuarios_col.insert_one(datos)
# --- RASTREO PARA SPARK (NUEVO REGISTRO) ---
    import datetime
    log_registro = {
        "nombre": datos.get('nombre'),
        "rol": datos.get('rol'),
        "evento": "Nuevo Registro",
        "gateway": "200.0.0.1",
        "status": "Online",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["logs_asistencia"].insert_one(log_registro)
    # ------------------------------------------
    return render_template("exito.html", mensaje="Registro exitoso", destino="inicio")
@app.route("/api/sensor/<matricula>")
def api_sensor(matricula):
    import datetime
    # Guardamos el rastro en la colección logs_asistencia
    dato_iot = {
        "matricula": matricula,
        "evento": "Captura_RFID_Edge",
        "gateway": "200.0.0.1",
        "protocolo": "SSL/TLS",
        "status": "Persistido_Atlas",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["logs_asistencia"].insert_one(dato_iot)
    return f"<h1>🛰️ Capa Edge Activada</h1><p>Dato de {matricula} enviado a la nube.</p>"

@app.route("/mandar_reporte", methods=["POST"])
def mandar_reporte():
    matricula = request.form.get("matricula")
    descripcion = request.form.get("descripcion")
    if matricula and descripcion:
        nuevo_reporte = {
            "matricula": matricula,
            "descripcion": descripcion,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        reportes_col.insert_one(nuevo_reporte)
    return '<h1>✅ Reporte enviado</h1><a href="/login">Volver al inicio</a>'

@app.route("/dashboard")
def dashboard():
    total_accesos = db["logs_asistencia"].count_documents({})
    total_reportes = reportes_col.count_documents({})
    return render_template("dashboard.html", accesos=total_accesos, reportes=total_reportes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
