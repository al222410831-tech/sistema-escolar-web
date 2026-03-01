from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "<h1>Sistema Integral Escolar funcionando en internet</h1>"

if __name__ == "__main__":
    app.run()
