from flask import Flask, render_template, jsonify, redirect, url_for
import random

app = Flask(__name__)

# Initialize game state
game_state = {
    "blue_pieces": [0, 0, 0, 0, 0, 0],  # Positions of blue team pieces (0 = start)
    "red_pieces": [13, 13, 13, 13, 13, 13],  # Positions of red team pieces (13 = start)
    "blue_home": 0,  # Blue team home count
    "red_home": 0,  # Red team home count
    "turn": "blue",  # Current turn (blue or red)
}

# Define the size of the board
BOARD_SIZE = 26


def roll_dice():
    return random.randint(1, 6)


def move_piece(piece, team):
    """ Move the piece forward by the dice roll """
    if team == "blue":
        # Move counterclockwise for blue team
        return (piece - roll_dice()) % BOARD_SIZE
    else:
        # Move counterclockwise for red team
        return (piece + roll_dice()) % BOARD_SIZE


def check_for_collision():
    """ Check if any piece of one team collides with the other team's pieces """
    for b_piece in game_state["blue_pieces"]:
        if b_piece in game_state["red_pieces"]:
            return "red", b_piece  # Blue piece lands on red piece
    for r_piece in game_state["red_pieces"]:
        if r_piece in game_state["blue_pieces"]:
            return "blue", r_piece  # Red piece lands on blue piece
    return None, None


def update_game_state():
    """ Update the game state after each move """
    collision_team, collided_piece = check_for_collision()
    if collision_team:
        # Send the opponent's piece back to the start
        if collision_team == "blue":
            game_state["blue_pieces"][game_state["blue_pieces"].index(collided_piece)] = 0
        else:
            game_state["red_pieces"][game_state["red_pieces"].index(collided_piece)] = 13

    # Check if any piece reaches the home base and update the score
    blue_home_count = sum(1 for p in game_state["blue_pieces"] if p == 0)
    red_home_count = sum(1 for p in game_state["red_pieces"] if p == 13)

    game_state["blue_home"] = blue_home_count
    game_state["red_home"] = red_home_count


@app.route('/')
def index():
    """ Render the main page with current game state """
    return render_template('index.html', game_state=game_state)


@app.route('/roll_dice')
def roll():
    """ Roll the dice and move the current team """
    if game_state["turn"] == "blue":
        # Blue team rolls
        team = "blue"
        piece_to_move = random.choice([p for p in game_state["blue_pieces"] if p != 0])  # Select a piece that's not in home
        new_position = move_piece(piece_to_move, team)
        game_state["blue_pieces"][game_state["blue_pieces"].index(piece_to_move)] = new_position
    else:
        # Red team rolls
        team = "red"
        piece_to_move = random.choice([p for p in game_state["red_pieces"] if p != 13])  # Select a piece that's not in home
        new_position = move_piece(piece_to_move, team)
        game_state["red_pieces"][game_state["red_pieces"].index(piece_to_move)] = new_position

    # After moving, check for collisions and update the game state
    update_game_state()

    # Switch turns
    game_state["turn"] = "red" if team == "blue" else "blue"

    return redirect(url_for('index'))


@app.route('/game_state')
def game_state_json():
    """ Return the current game state as JSON """
    return jsonify(game_state)


if __name__ == '__main__':
    app.run(debug=True)
