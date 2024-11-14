from flask import Flask, render_template, jsonify, redirect, url_for, request
import random

app = Flask(__name__)

# Function to initialize the game state
def init_game():
    return {
        "blue_pieces": [-1, -1, -1, -1, -1, -1],  # Blue team pieces in home base (starting at -1)
        "red_pieces": [26, 26, 26, 26, 26, 26],  # Red team pieces in home base (starting at 26)
        "blue_home": 0,  # Blue team home count
        "red_home": 0,  # Red team home count
        "turn": "blue",  # Current turn (blue or red)
        "winner": None,  # Winner of the game (if any)
    }

# Initialize game state
game_state = init_game()

# Define the size of the board (26 spaces)
BOARD_SIZE = 26

def roll_dice():
    return random.randint(1, 6)

def move_piece(piece, team, dice_roll):
    """Move a piece forward by the dice roll (clockwise)"""
    if team == "blue":
        # Blue team moves forward (clockwise)
        new_position = piece + dice_roll
        if new_position > 25:
            new_position = 25  # Don't allow movement past the board
        return new_position
    else:
        # Red team moves forward (clockwise)
        new_position = piece + dice_roll
        if new_position > 25:
            new_position = 25  # Don't allow movement past the board
        return new_position

def check_for_collision():
    """Check if any piece of one team collides with the other team's pieces"""
    for b_piece in game_state["blue_pieces"]:
        if b_piece in game_state["red_pieces"]:
            return "red", b_piece  # Blue piece lands on red piece
    for r_piece in game_state["red_pieces"]:
        if r_piece in game_state["blue_pieces"]:
            return "blue", r_piece  # Red piece lands on blue piece
    return None, None

def update_game_state():
    """Update the game state after each move"""
    collision_team, collided_piece = check_for_collision()
    if collision_team:
        # Send the opponent's piece back to the start
        if collision_team == "blue":
            game_state["blue_pieces"][game_state["blue_pieces"].index(collided_piece)] = -1
        else:
            game_state["red_pieces"][game_state["red_pieces"].index(collided_piece)] = 26

    # Check if any piece reaches the home base and update the score
    blue_home_count = sum(1 for p in game_state["blue_pieces"] if p == -1)
    red_home_count = sum(1 for p in game_state["red_pieces"] if p == 26)

    game_state["blue_home"] = blue_home_count
    game_state["red_home"] = red_home_count

    # Check if either team has won
    if blue_home_count == 6:
        game_state["winner"] = "Blue"
    elif red_home_count == 6:
        game_state["winner"] = "Red"

@app.route('/')
def index():
    """Render the main page with current game state"""
    return render_template('index.html', game_state=game_state)

@app.route('/roll_dice')
def roll():
    """Roll the dice and move the current team"""
    if game_state["winner"]:
        return redirect(url_for('game_over'))  # Redirect to game over page if the game has a winner

    if game_state["turn"] == "blue":
        team = "blue"
        # Check if there are any blue pieces in home base (-1)
        if -1 in game_state["blue_pieces"]:
            # Move a piece out of the home base
            home_piece = game_state["blue_pieces"].index(-1)
            dice_roll = roll_dice()
            game_state["blue_pieces"][home_piece] = dice_roll  # Place the piece based on the dice roll
        else:
            # Move an existing piece
            piece_to_move = random.choice([p for p in game_state["blue_pieces"] if p != -1])  # Select a piece that's not in home
            dice_roll = roll_dice()
            new_position = move_piece(piece_to_move, team, dice_roll)
            game_state["blue_pieces"][game_state["blue_pieces"].index(piece_to_move)] = new_position

    else:
        team = "red"
        # Check if there are any red pieces in home base (26)
        if 26 in game_state["red_pieces"]:
            # Move a piece out of the home base
            home_piece = game_state["red_pieces"].index(26)
            dice_roll = roll_dice()
            game_state["red_pieces"][home_piece] = 25  # Place the piece on the first space (25)
        else:
            # Move an existing piece
            piece_to_move = random.choice([p for p in game_state["red_pieces"] if p != 26])  # Select a piece that's not in home
            dice_roll = roll_dice()
            new_position = move_piece(piece_to_move, team, dice_roll)
            game_state["red_pieces"][game_state["red_pieces"].index(piece_to_move)] = new_position

    # After moving, check for collisions and update the game state
    update_game_state()

    # Switch turns
    if not game_state["winner"]:  # Only switch turns if no one has won yet
        game_state["turn"] = "red" if team == "blue" else "blue"

    return redirect(url_for('index'))



@app.route('/game_over', methods=["GET", "POST"])
def game_over():
    """Handle game over and prompt user for new game"""
    if request.method == "POST":
        # Reset game if user wants to play again
        global game_state
        game_state = init_game()  # Reset the game state to the initial state
        return redirect(url_for('index'))  # Redirect to the main game page

    # For GET request, just display the winner page
    return render_template('game_over.html', winner=game_state['winner'])


if __name__ == '__main__':
    app.run(debug=True)
