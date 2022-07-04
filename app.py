# save this as app.py
from flask import Flask, escape, request, render_template, session, make_response
from secrets import token_urlsafe

app = Flask(__name__)
app.secret_key = "lYBvDRtTtFjZ67rWf5wZ"


@app.route('/save-to-db', methods=['POST'])
def save_game_result_to_db():
    print(request.json)
    if request.method == 'POST':
        print(request.json['data'])
        return True
    return False


@app.route('/', methods=['GET'])
def game():
    if request.method == 'GET':
        if request.cookies:
            return render_template('index.html')
        else:
            # sprawdzenie unikalności userID
            response = make_response(render_template('index.html'))
            response.set_cookie('userID', token_urlsafe(nbytes=32))
            return response


if __name__ == '__main__':
    app.run(debug=True)
