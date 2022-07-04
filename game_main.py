# save this as game_main.py
from json import dumps
from flask import Flask, escape, request, render_template, session, make_response
from secrets import token_urlsafe
from random import randrange
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os.path import exists
import database_models
from sqlalchemy.sql import func


r_p_s_game = Flask(__name__)
r_p_s_game.secret_key = "lYBvDRtTtFjZ67rWf5wZ"

if not exists('RPS_DB.sqlite'):
    database_models.create_db()

db_session = sessionmaker(bind=create_engine('sqlite:///RPS_DB.sqlite', echo=True))
db_session = db_session()


@r_p_s_game.route('/save-to-db', methods=['POST'])
def save_game_result_to_db():
    if request.method == 'POST':
        print(request.json['selected_par'])
        result = get_winner(request.json['selected_par'])
        print(f"Result {result}")
        print(f"Result {result['result']}")
        add_data = database_models.GameDB(user_id=request.json['player_id'],
                                          result=result['result'],
                                          start_credits=request.json['credits_before_game'])
        db_session.add(add_data)
        db_session.commit()
        return result


def get_user_info():
    return True


def create_new_user():
    # try:
    new_user = db_session.query(func.max('user_id')).last()
    print(new_user)
    # except TypeError:
    #     new_user = 0
    return new_user


def get_date_result(date):
    return True


def add_credits_to_user():
    user_credits = ""
    if user_credits == 0:
        return True
    else:
        return False


def get_winner(selected_par):
    if request.method == 'POST':
        option_list = ["Papier", "Kamień", "Nożyce"]
        rng_choice = option_list[randrange(3)]
        result = ""

        if selected_par == rng_choice:
            result = "draw"
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

        return {"result": result, "rng_choice": rng_choice}


@r_p_s_game.route('/', methods=['GET'])
def game():
    if request.method == 'GET':
        if request.cookies:
            return render_template('index.html')
        else:
            # sprawdzenie unikalności userID
            new_user = create_new_user()
            response = make_response(render_template('index.html'))
            response.set_cookie('userID', new_user)
            print(new_user)
            return response


r_p_s_game.run(debug=True)
