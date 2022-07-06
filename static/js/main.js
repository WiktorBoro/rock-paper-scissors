var player_id = document.cookie.replace('user_id=', '');

document.addEventListener('DOMContentLoaded', function() {
if (document.getElementById('credits').innerHTML == 0) document.getElementById('addCredits').disabled = false;
}, false);

function addCredits(){
    var credits = parseInt(document.getElementById('credits').innerHTML)

    if (credits == 0) {

    $.ajax({
    url: "/api/add-credits-to-user",
    type: "POST",
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify({
        "user_id": player_id,
    }),
    success:  (result)  =>{

        document.getElementById('credits').innerHTML = result['Credits'];
        document.getElementById('addCredits').disabled = true;
    },
    error: (data)  =>{
        console.log(data);
    }
    });
 }
}

function newSession(){
    document.cookie = "user_id="
    window.location.reload(true);
}

function starGame(players_choice) {
    date_now = Date.now();

    $.ajax({
    url: "/api/play-game",
    type: "POST",
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify({
        "user_id": player_id,
        "players_choice":players_choice
    }),
    success:  (result)  =>{

    if ("Error" in result){
        document.getElementById('comment').innerHTML = result['Error']
    }
    else{
        document.getElementById('rng_result').innerHTML = result['rng_choice'];
        document.getElementById('rng_choice').hidden = false;
        document.getElementById('credits').innerHTML = result['credits_after_game']
        if (result['credits_after_game']==0) document.getElementById('addCredits').disabled = false;
        if (result['result'] == "win") {
            document.getElementById('comment').innerHTML = "You win! You get 4 credits"
            }
        else if (result['result'] == "lose") document.getElementById('comment').innerHTML = "You lost!"
        else if (result['result'] == "draw") document.getElementById('comment').innerHTML = "Draw!"
        }
    },
    error: (data)  =>{
        console.log(data);
    }
    });
}
