from flask import Flask, redirect

app = Flask(__name__)

@app.route("/")
def redirect_homepage():
    return redirect('https://walkwithmeapp.co.uk')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug = False)