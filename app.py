from flask import Flask, request, render_template, make_response
from random import randrange
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy import create_engine, select, text, insert
from os.path import exists
from database_models import UsersDB, GameDB, create_db
from sqlalchemy.sql import func


r_p_s_game = Flask(__name__)
r_p_s_game.secret_key = "lYBvDRtTtFjZ67rWf5wZ"

if not exists('RPS_DB.sqlite'):
    create_db()

# conn_db = create_engine('sqlite:///RPS_DB.sqlite', check_same_thread=False)
db_session = sessionmaker(bind=create_engine('sqlite:///RPS_DB.sqlite?check_same_thread=False'))
db_session = db_session()
# db_session = create_engine('sqlite:///RPS_DB.sqlite', echo=True)


def save_game_result_to_db(user_id, game_result, credits_before_game, credits_after_game):
    print(db_session.query(UsersDB.user_id).filter(UsersDB.user_id == user_id).first()[0])
    add_data = GameDB(user_id=user_id,
                      result=game_result,
                      credits_before_game=credits_before_game)

    db_session.query(UsersDB).filter(UsersDB.user_id == user_id).update({'credits_': credits_after_game})

    db_session.add(add_data)
    db_session.commit()


@r_p_s_game.route('/api/play-game', methods=['POST'])
def play_game():
    if request.method == 'POST':
        credits_after_win = 4
        game_cost = -3
        credits_before_game = request.json['credits_before_game']

        credits_after_game = credits_before_game + game_cost
        game_result_and_rng_choice = get_winner(request.json['selected_par'])

        if game_result_and_rng_choice['result'] == "win":
            credits_after_game += credits_after_win

        save_game_result_to_db(user_id=request.json['player_id'],
                               game_result=game_result_and_rng_choice['result'],
                               credits_before_game=credits_before_game,
                               credits_after_game=credits_after_game)
        return game_result_and_rng_choice


@r_p_s_game.route('/api/get-user-list', methods=['GET'])
def get_user_list():
    if request.method == 'GET':
        user_dict = {user: cred for user, cred in db_session.query(UsersDB.user_id, UsersDB.credits_).all()}
        return user_dict
    else:
        return {"Error": "Bad method used! Use GET method."}


def create_new_user():

    new_user = db_session.query(func.max(UsersDB.user_id)).all()[0][0]
    if not new_user:
        new_user = 1
    else:
        new_user = int(new_user)+1

    start_credits = 10
    add_user = UsersDB(user_id=new_user,
                       credits_=start_credits)
    db_session.add(add_user)
    db_session.commit()
    return new_user


def get_date_result(date):
    return True


@r_p_s_game.route('/api/add-credits-to-user', methods=['POST'])
def add_credits_to_user(user_id):
    if request.method == "POST":
        user_credits = db_session.query(UsersDB).filter(UsersDB.user_id == user_id)
        if user_credits.first()[0] == 0:
            user_credits.update({'credits_': 10})
            return {"Message": "Success!", user_id: 10}
        else:
            return {"Error": "Only 0 credits users can add new credits!"}
    else:
        return {"Error": "Bad method used! Use POST method."}

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
        if all([request.cookies, request.cookies.get(key="userID")]):
            user_cred = db_session.query(UsersDB.credits_).filter(UsersDB.user_id == request.cookies.get(key="userID")).first()[0]
            return render_template('index.html', data={'user_cred': user_cred})
        else:
            new_user = create_new_user()
            user_cred = db_session.query(UsersDB.credits_).filter(UsersDB.user_id == new_user).first()[0]
            response = make_response(render_template('index.html', data={'user_cred': user_cred}))
            response.set_cookie('userID', str(new_user))
            return response


r_p_s_game.run(debug=True)
