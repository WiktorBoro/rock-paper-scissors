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
    add_data = GameDB(user=user_id,
                      result=game_result,
                      credits_before_game=credits_before_game)

    db_session.query(UsersDB).filter(UsersDB.user_id == user_id).update({'credits_': credits_after_game})

    db_session.add(add_data)
    db_session.commit()


@r_p_s_game.route('/api/play-game', methods=['POST'])
def play_game():
    credits_after_win = 4
    game_cost = -3
    user_id = request.json['user_id']
    credits_before_game = db_session.query(UsersDB.credits_).filter(UsersDB.user_id == user_id).first()[0]

    if credits_before_game == 0:
        return {"Error": "Top up your credits!"}

    credits_after_game = credits_before_game + game_cost

    if credits_after_game < 0:
        return {"Error": "You don't have enough credits for the next game!"}

    players_choice = request.json['players_choice']

    game_result_and_rng_choice = get_winner(players_choice)

    if game_result_and_rng_choice['result'] == "win":
        credits_after_game += credits_after_win

    save_game_result_to_db(user_id=user_id,
                           game_result=game_result_and_rng_choice['result'],
                           credits_before_game=credits_before_game,
                           credits_after_game=credits_after_game)
    return game_result_and_rng_choice \
           | {'credits_before_game': credits_before_game} \
           | {'credits_after_game': credits_after_game}


@r_p_s_game.route('/api/get-user-list', methods=['GET'])
def get_user_list():
    user_dict = {user: cred for user, cred in db_session.query(UsersDB.user_id, UsersDB.credits_).all()}
    return user_dict


@r_p_s_game.route('/api/create-new-user', methods=['POST'])
def create_new_user():
    new_user = db_session.query(func.max(UsersDB.user_id)).all()[0][0]
    if not new_user:
        new_user = 1
    else:
        new_user = int(new_user) + 1

    start_credits = 10
    add_user = UsersDB(user_id=new_user,
                       credits_=start_credits)
    db_session.add(add_user)
    db_session.commit()
    return {"User number": new_user, "Start credits": start_credits}


@r_p_s_game.route('/api/get-result-from-day', methods=['GET'])
def get_result_from_day():
    date = request.json['user_id']
    return True


@r_p_s_game.route('/api/add-credits-to-user', methods=['POST'])
def add_credits_to_user():
    user_id = request.json['user_id']

    if db_session.query(UsersDB.credits_).filter(UsersDB.user_id == user_id).first()[0] == 0:
        db_session.query(UsersDB).filter(UsersDB.user_id == user_id).update({'credits_': 10})
        db_session.commit()
        return {"Message": "Success!", "User id": user_id, "Credits": 10}
    else:
        return {"Error": "Only 0 credits users can add new credits!"}


def get_winner(players_choice):
    if request.method == 'POST':
        option_list = ["Papier", "Kamień", "Nożyce"]
        rng_choice = option_list[randrange(3)]
        result = ""

        if players_choice == rng_choice:
            result = "draw"
        elif players_choice == "Papier":
            if rng_choice == "Kamień":
                result = "win"
            else:
                result = "lose"
        elif players_choice == "Kamień":
            if rng_choice == "Nożyce":
                result = "win"
            else:
                result = "lose"
        elif players_choice == "Nożyce":
            if rng_choice == "Papier":
                result = "win"
            else:
                result = "lose"

        return {"result": result, "rng_choice": rng_choice}


@r_p_s_game.route('/', methods=['GET'])
def game():
    if all([request.cookies, request.cookies.get(key="userID")]):
        user_cred = \
            db_session.query(UsersDB.credits_).filter(UsersDB.user_id == request.cookies.get(key="userID")).first()[0]
        return render_template('index.html', data={'user_cred': user_cred})
    else:
        new_user = create_new_user()['User number']
        user_cred = db_session.query(UsersDB.credits_).filter(UsersDB.user_id == new_user).first()[0]
        response = make_response(render_template('index.html', data={'user_cred': user_cred}))
        response.set_cookie('userID', str(new_user))
        return response


r_p_s_game.run(debug=True)
