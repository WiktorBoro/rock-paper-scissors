function addCredits() {
    var credits = parseInt(document.getElementById('credits').innerHTML)
    if (credits == 0) {
        document.getElementById('credits').innerHTML = 10;
        document.getElementById('addCredits').disabled = true;
        }
}

function starGame(value) {

    var credits_before_game = parseInt(document.getElementById('credits').innerHTML)
    var credits_after_win = 4
    var game_cost = -3

    if (credits == 0) {
        document.getElementById('addCredits').disabled = false;
        return document.getElementById('comment').innerHTML = "Doładuj kredyty!"
        }

    credits = credits_before_game + game_cost

    if (credits < 0) return document.getElementById('comment').innerHTML = "Nie masz wystarczającej ilośći żyć do kolejnej gry"
    document.getElementById('credits').innerHTML = credits

    var option_list = ["Papier", "Kamień", "Nożyce"]
    var rng_choice =  option_list[Math.floor(Math.random() * 3)];
    var result = ""

    document.getElementById('rng_result').innerHTML = rng_choice;
    document.getElementById('rng_choice').hidden = false;

    if (value == rng_choice) document.getElementById('comment').innerHTML = "Remis!";
    else if (value == "Papier") {
        if(rng_choice == "Kamień") result = "win"
        else result = "lose"
        }
    else if (value == "Kamień") {
        if(rng_choice == "Nożyce") result = "win"
        else result = "lose"
        }
    else if (value == "Nożyce") {
        if(rng_choice == "Papier") result = "win"
        else result = "lose"
        }
    if (result == "win") {
        document.getElementById('credits').innerHTML = credits + credits_after_win
        document.getElementById('comment').innerHTML = "Wygrałeś! Otrzymujesz 4 kredyty"
        }
    else if (result == "lose") document.getElementById('comment').innerHTML = "Przegrałeś!"
    // save to db
    var player_id = 1
    sendData(result, credits_before_game)
}

function sendData(result, credits_before_game){
    date_now = Date.now();
    player_id = document.cookie.replace('userID=', '');

    $.ajax({
    url: "/save-to-db",
    type: "POST",
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify({
        "result": result,
        "credits_before_game": credits_before_game,
        "player_id": player_id,
        "date_now": date_now,
    }),
    });
 }