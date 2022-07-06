from flask import Flask, request, render_template, make_response, jsonify
from random import randrange
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os.path import exists
from database_models import UsersDB, GameDB, create_db
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from flask_swagger_ui import get_swaggerui_blueprint
from os import environ

r_p_s_game = Flask(__name__)
r_p_s_game.secret_key = "lYBvDRtTtFjZ67rWf5wZ"

if not exists('RPS_DB.sqlite'):
    create_db()

db_session = sessionmaker(bind=create_engine('sqlite:///RPS_DB.sqlite?check_same_thread=False'))
db_session = db_session()

# swagger specific
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Rock Paper Scissors"
    }
)
r_p_s_game.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
# end swagger specific


@r_p_s_game.route('/', methods=['GET'])
def game():
    user_cred = \
        db_session.query(UsersDB.credits_).filter(UsersDB.user_id == request.cookies.get(key="user_id")).first()
    # if we don't have "user_id" cookies we need to create new user
    if user_cred:
        return render_template('index.html', data={'user_cred': user_cred[0]})
    else:
        new_user = create_new_user().get_json(force=True)
        user_id = new_user['user_id']
        user_cred = new_user['start_credits']
        response = make_response(render_template('index.html', data={'user_cred': user_cred}))
        response.set_cookie('user_id', str(user_id))
        return response


@r_p_s_game.route('/api/play-game', methods=['POST'])
def play_game():
    credits_after_win = 4
    game_cost = -3
    request_json = request.get_json(force=True)

    user_id = request_json['user_id']

    # Error for a non-existent player
    try:
        credits_before_game = db_session.query(UsersDB.credits_).filter(UsersDB.user_id == user_id).first()[0]
    except TypeError:
        return make_response(jsonify({"Error": "The player doesn't exist!"}), 400)

    credits_after_game = credits_before_game + game_cost

    if credits_before_game == 0:
        return make_response(jsonify({"Error": "Top up your credits!"}), 400)

    elif credits_after_game < 0:
        return make_response(jsonify({"Error": "You don't have enough credits for the next game!"}), 400)

    players_choice = request_json['players_choice']

    game_result_and_rng_choice = get_winner(players_choice)

    if game_result_and_rng_choice['result'] == "win":
        credits_after_game += credits_after_win

    save_game_result_to_db(user_id=user_id,
                           game_result=game_result_and_rng_choice['result'],
                           credits_before_game=credits_before_game,
                           credits_after_game=credits_after_game)
    return make_response(jsonify(game_result_and_rng_choice \
                                 | {'credits_before_game': credits_before_game} \
                                 | {'credits_after_game': credits_after_game}), 200)


def get_winner(players_choice):
    if request.method == 'POST':
        option_list = ["Paper", "Rock", "Scissors"]

        # if someone sent an invalid string
        if players_choice not in option_list:
            return make_response(jsonify({"Error": "You can only choose \"Rock\" \"Paper\" \"Scissors\"!"}), 400)

        rng_choice = option_list[randrange(3)]
        result = ""

        if players_choice == rng_choice:
            result = "draw"
        elif players_choice == "Paper":
            if rng_choice == "Rock":
                result = "win"
            else:
                result = "lose"
        elif players_choice == "Rock":
            if rng_choice == "Scissors":
                result = "win"
            else:
                result = "lose"
        elif players_choice == "Scissors":
            if rng_choice == "Paper":
                result = "win"
            else:
                result = "lose"

        return {"result": result, "rng_choice": rng_choice}


def save_game_result_to_db(user_id, game_result, credits_before_game, credits_after_game):
    add_data = GameDB(user=user_id,
                      result=game_result,
                      credits_before_game=credits_before_game)

    db_session.query(UsersDB).filter(UsersDB.user_id == user_id).update({'credits_': credits_after_game})

    db_session.add(add_data)
    db_session.commit()


@r_p_s_game.route('/api/get-user-stat', methods=['GET'])
def get_user_list():
    user_dict = dict()

    for user, cred in db_session.query(UsersDB.user_id, UsersDB.credits_).all():
        user_dict.update({f"user_{user}": {"id": user, "credits": cred}})

        for result in db_session.query(GameDB.result).filter(GameDB.user == user).all():
            result = result[0]
            if result not in user_dict[f'user_{user}']:
                user_dict[f'user_{user}'].update({result: 1})
            else:
                user_dict[f'user_{user}'][result] += 1

    if user_dict:
        return make_response(jsonify(user_dict), 200)
    else:
        return make_response(jsonify({"Error": "No users in database!"}), 400)


@r_p_s_game.route('/api/create-new-user', methods=['POST'])
def create_new_user():
    # we use max to take the last user
    new_user = db_session.query(func.max(UsersDB.user_id)).first()[0]
    if not new_user:
        # if we don't have user we start from beginning
        new_user = 1
    else:
        new_user = int(new_user) + 1

    start_credits = 10

    # save new user do db
    add_user = UsersDB(user_id=new_user,
                       credits_=start_credits)
    db_session.add(add_user)
    db_session.commit()
    return make_response(jsonify({"user_id": new_user, "start_credits": start_credits}), 200)


@r_p_s_game.route('/api/get-result-from-day/<path:date>', methods=['GET'])
def get_result_from_day(date):
    timedelta_ = timedelta(days=1)
    date = datetime.strptime(date, '%Y-%m-%d')

    result_from_day = {f"game_{game_id}": {"user_id": user,
                                           "result": result,
                                           "credits_before_game": credits_before_game,
                                           "game_time": str(game_time)} for
                       game_id, user, result, credits_before_game, game_time
                       in db_session.query(GameDB.id,
                                           GameDB.user,
                                           GameDB.result,
                                           GameDB.credits_before_game,
                                           GameDB.game_time).filter(date < GameDB.game_time,
                                                                    date + timedelta_ > GameDB.game_time).all()}
    if result_from_day:
        return make_response(jsonify(result_from_day), 200)
    else:
        return make_response(jsonify({"Error": "There were no games that day!"}), 400)


@r_p_s_game.route('/api/add-credits-to-user', methods=['POST'])
def add_credits_to_user():
    user_id = request.get_json(force=True)['user_id']

    if db_session.query(UsersDB.credits_).filter(UsersDB.user_id == user_id).first()[0] == 0:
        db_session.query(UsersDB).filter(UsersDB.user_id == user_id).update({'credits_': 10})
        db_session.commit()
        return make_response(jsonify({"Message": "Success!", "User id": user_id, "Credits": 10}), 200)
    else:
        return make_response(jsonify({"Error": "Only 0 credits users can add new credits!"}), 400)


if __name__ == "__main__":
    port = environ.get("PORT", 5000)
    r_p_s_game.run(debug=False, host='0.0.0.0', port=port)
