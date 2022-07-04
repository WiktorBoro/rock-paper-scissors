# save this as app.py
from json import dumps
from flask import Flask, escape, request, render_template, session, make_response
from secrets import token_urlsafe
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from random import randrange
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

r_p_s_game = Flask(__name__)
r_p_s_game.secret_key = "lYBvDRtTtFjZ67rWf5wZ"

conn_db = create_engine('sqlite:///RPS_DB.sqlite', echo=True)
base = declarative_base()


class GameDB(base):
    __tablename__ = 'games statistics'
    user_id = Column(Integer, primary_key=True)
    result = Column(String)
    game_time = Column(DateTime)

    def __init__(self, user_id, result, game_time):
        self.user_id = user_id
        self.result = result
        self.game_time = game_time
base.metadata.create_all(conn_db)


def save_game_result_to_db():
    # print(request.json)
    user_id = 1
    result = 'test'
    game_time = datetime.now()
    base.metadata.create_all(conn_db)
    # if request.method == 'POST':
    #     print(request.json['date_now'])


@r_p_s_game.route('/save-to-db', methods=['POST'])
def get_winner(selected_par, credits):
    if request.method == 'POST':
        option_list = ["Papier", "Kamień", "Nożyce"]
        rng_choice = option_list[randrange(3)]
        result = ""

        if selected_par == rng_choice:
            pass
            # document.getElementById('comment').innerHTML = "Remis!";
        elif selected_par == "Papier":
            if rng_choice == "Kamień":
                result = "win"
            else:
                result = "lose"
        elif selected_par == "Kamień":
            if rng_choice == "Nożyce":
                result = "win"
            else:
                result = "lose"
        elif selected_par == "Nożyce":
            if rng_choice == "Papier":
                result = "win"
            else:
                result = "lose"

        return dumps({"result": result, "rng_choice": rng_choice})


def add_creddits():
    pass


@r_p_s_game.route('/', methods=['GET'])
def game():
    if request.method == 'GET':
        if request.cookies:
            return render_template('index.html')
        else:
            # sprawdzenie unikalności userID
            response = make_response(render_template('index.html'))
            response.set_cookie('userID', token_urlsafe(nbytes=32))
            return response


# if __name__ == '__main__':
# save_game_result_to_db()
r_p_s_game.run(debug=True)
