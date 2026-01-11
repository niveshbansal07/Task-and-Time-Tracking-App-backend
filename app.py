from flask import Flask


app = Flask(__name__)


# test route
@app.route("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)