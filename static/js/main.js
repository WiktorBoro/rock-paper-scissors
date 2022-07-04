function addCredits() {
    var credits = parseInt(document.getElementById('credits').innerHTML)
    if (credits == 0) {
        document.getElementById('credits').innerHTML = 10;
        document.getElementById('addCredits').disabled = true;
        }
}

function starGame(selected_par) {
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

    // save to db
    sendData(credits_before_game, credits, selected_par)
}

function sendData(credits_before_game, credits, selected_par){
    date_now = Date.now();
    player_id = document.cookie.replace('userID=', '');

    $.ajax({
    url: "/save-to-db",
    type: "POST",
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify({
        "credits_before_game": credits_before_game,
        "player_id": player_id,
        "selected_par":selected_par
    }),
    success:  (result)  =>{
        document.getElementById('rng_result').innerHTML = result['rng_choice'];
        document.getElementById('rng_choice').hidden = false;
        if (result['result'] == "win") {
            document.getElementById('credits').innerHTML = credits + credits_after_win
            document.getElementById('comment').innerHTML = "Wygrałeś! Otrzymujesz 4 kredyty"
            }
        else if (result['result'] == "lose") document.getElementById('comment').innerHTML = "Przegrałeś!"
        else if (result['result'] == "draw") document.getElementById('comment').innerHTML = "Remis!"
    },
    error: (data)  =>{
        console.log(data);
    }
    });
 }