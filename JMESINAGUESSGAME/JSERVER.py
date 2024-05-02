
import socket
import random
import json

# Load leaderboard data from file
def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = {}
    return leaderboard

# Save leaderboard data to file
def save_leaderboard(leaderboard):
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)

# Generate a random number based on difficulty
def generate_number(difficulty):
    if difficulty == 'Easy':
        return random.randint(1, 50)
    elif difficulty == 'Medium':
        return random.randint(1, 100)
    elif difficulty == 'Hard':
        return random.randint(1, 500)
    else:
        return None

# Update leaderboard with new score
def update_leaderboard(leaderboard, name, score):
    if name in leaderboard:
        if score < leaderboard[name]:
            leaderboard[name] = score
    else:
        leaderboard[name] = score

# Handle client connection
def handle_client(conn):
    conn.send("Welcome to the Number Guessing Game!\n".encode())
    name = conn.recv(1024).decode().strip()
    conn.send("Choose difficulty: Easy, Medium, Hard: ".encode())
    difficulty = conn.recv(1024).decode().strip()

    number_to_guess = generate_number(difficulty)
    if number_to_guess is None:
        conn.send("Invalid difficulty!\n".encode())
        conn.close()
        return

    tries = 0
    try:
        while True:
            guess = conn.recv(1024).decode().strip()
            if not guess.isdigit():
                conn.send("Please enter a valid number!\n".encode())
                continue
            guess = int(guess)
            tries += 1
            if guess == number_to_guess:
                conn.send(f"Congratulations! You've guessed the number in {tries} tries!\n".encode())
                break
            elif guess < number_to_guess:
                conn.send("Try higher!\n".encode())
            else:
                conn.send("Try lower!\n".encode())
    except (ConnectionResetError, ConnectionAbortedError):
        # Handle client disconnect
        print("Client disconnected unexpectedly.")

    # Display the correct number
    conn.send(f"The correct number was: {number_to_guess}\n".encode())
    
    # Update leaderboard
    leaderboard = load_leaderboard()
    update_leaderboard(leaderboard, name, tries)
    save_leaderboard(leaderboard)

    conn.close()


# Main function
def main():
    HOST = '192.168.68.115'
    PORT = 7777

    leaderboard = load_leaderboard()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"Server started, listening on {PORT}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            handle_client(conn)

if __name__ == "__main__":
    main()