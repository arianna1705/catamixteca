from flask import Flask, render_template


app = Flask(__name__)

#carga de apartados en la página

@app.route('/')
def home():
    return render_template("index.html")

#@app.route('/')
#def portafolio():
 #   return render_template("portfolio-details.html")

@app.route('/servicios')
def servicios():
    return render_template("servicios.html")

@app.route('/galeria')
def galeria():
    return render_template("galeria.html")


@app.route('/catalogo')
def catalogo():
    return render_template("catalogo.html")

@app.route('/sesion')
def sesion():
    return render_template("sesion.html")

#@app.route('/')
#def starter():
#    return render_template("starter-page.html")


#apis para agregar, actualizar, eliminar y obtener





if __name__=='__main__':
    app.run(debug=True)