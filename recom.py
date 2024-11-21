import mysql.connector  
import networkx as nx

# BAGO 123
    
# Connect to MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="social_media"
)

db_cursor = db_connection.cursor()

# Graph for users and friendships
class SocialMediaGraph: 
    def __init__(self):
        self.graph = nx.Graph()
        self._initialize_graph()

    def _initialize_graph(self):
        """Initialize graph nodes and edges from MySQL database."""
        db_cursor.execute("SELECT username FROM users")
        users = db_cursor.fetchall()
        for user in users:
            self.graph.add_node(user[0])

        db_cursor.execute("SELECT user1, user2 FROM friendships")
        friendships = db_cursor.fetchall()
        for user1, user2 in friendships:
            self.graph.add_edge(user1, user2)

    def add_user(self, username, user_data):
        """Add a new user to the system."""
        db_cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if db_cursor.fetchone():
            print("Username already exists.")
            return False

        db_cursor.execute(
            "INSERT INTO users (username, age, location, gender, interests, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, user_data["age"], user_data["location"], user_data["gender"], ", ".join(user_data["interests"]), user_data["password"])
        )
        db_connection.commit()
        self.graph.add_node(username)
        return True

    def send_friend_request(self, from_user, to_user):
        db_cursor.execute("SELECT username FROM users WHERE username = %s", (to_user,))
        if not db_cursor.fetchone():
            print(f"User {to_user} does not exist.")
            return
        if from_user == to_user:
            print("You cannot send a friend request to yourself.")
            return

        db_cursor.execute("SELECT * FROM friend_requests WHERE from_user = %s AND to_user = %s", (from_user, to_user))
        if db_cursor.fetchone():
            print(f"Friend request already sent to {to_user}.")
            return

        db_cursor.execute(
            "INSERT INTO friend_requests (from_user, to_user) VALUES (%s, %s)",
            (from_user, to_user)
        )
        db_connection.commit()
        print(f"{from_user} sent a friend request to {to_user}")

    def accept_friend_request(self, user, from_user):
        db_cursor.execute("SELECT * FROM friend_requests WHERE from_user = %s AND to_user = %s", (from_user, user))
        if not db_cursor.fetchone():
            print("No friend request found from this user.")
            return

        db_cursor.execute("DELETE FROM friend_requests WHERE from_user = %s AND to_user = %s", (from_user, user))
        db_cursor.execute(
            "INSERT INTO friendships (user1, user2) VALUES (%s, %s), (%s, %s)",
            (user, from_user, from_user, user)
        )
        db_connection.commit()
        self.graph.add_edge(user, from_user)
        print(f"{user} accepted the friend request from {from_user}")

    def decline_friend_request(self, user, from_user):
        db_cursor.execute("SELECT * FROM friend_requests WHERE from_user = %s AND to_user = %s", (from_user, user))
        if not db_cursor.fetchone():
            print("No friend request found from this user.")
            return

        db_cursor.execute("DELETE FROM friend_requests WHERE from_user = %s AND to_user = %s", (from_user, user))
        db_connection.commit()
        print(f"{user} declined the friend request from {from_user}")

    def get_friend_requests(self, user):
        db_cursor.execute("SELECT from_user FROM friend_requests WHERE to_user = %s", (user,))
        return [row[0] for row in db_cursor.fetchall()]

    def recommend_friends(self, username):
        if username not in self.graph:
            print(f"User {username} is not in the system.")
            return {}

        friends = set(self.graph.neighbors(username))
        recommendations = {}

        for friend in friends:
            for fof in self.graph.neighbors(friend):
                if fof != username and fof not in friends:
                    if fof not in recommendations:
                        mutual_count = len(set(self.graph.neighbors(fof)).intersection(friends))
                        recommendations[fof] = mutual_count

        sorted_recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1], reverse=True))

        return sorted_recommendations
    
    def view_all_users(self):
        """Display all registered usernames."""
        try:
            db_cursor.execute("SELECT username FROM users")
            users = db_cursor.fetchall()
            print("\nAll Registered Users:")
            for user in users:
                print(user[0])
        except mysql.connector.Error as err:
            print(f"Error fetching users: {err}")

# Account creation and login functions
def create_account(username, age, location, gender, interests, password):
    sm_graph = SocialMediaGraph()
    user_data = {
        "age": age,
        "location": location,
        "gender": gender,
        "interests": interests,
        "password": password
    }
    if sm_graph.add_user(username, user_data):
        print(f"Account for {username} created successfully.")
    else:
        print("Account creation failed.")

def login(username, password):
    db_cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = db_cursor.fetchone()
    if result and result[0] == password:
        print(f"Welcome back, {username}!")
        return username
    else:
        print("Invalid username or password.")
        return None

# Interactive menu for user actions
def main():
    logged_in_user = None
    sm_graph = SocialMediaGraph()

    while True:
        print("\n--- Social Media Friend Recommendation System ---")
        if not logged_in_user:
            print("1. Create Account")
            print("2. Log In")
            print("3. View All Registered Users")
            print("4. Exit")
        else:
            print("1. View Friend Recommendations")
            print("2. Add Friend Menu")
            print("3. Log Out")
        
        choice = input("Enter your choice: ")

        if choice == "1" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")
            age = int(input("Enter age: "))
            location = input("Enter location: ")
            gender = input("Enter gender: ")
            interests = input("Enter interests (comma-separated): ").split(", ")
            create_account(username, age, location, gender, interests, password)
        
        elif choice == "2" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")
            logged_in_user = login(username, password)

        elif choice == "3" and not logged_in_user:
            sm_graph.view_all_users()

        elif choice == "1" and logged_in_user:
            recommendations = sm_graph.recommend_friends(logged_in_user)
            if recommendations:
                print(f"Friend recommendations for {logged_in_user}:")
                for user, mutual_count in recommendations.items():
                    print(f"Recommended friend: {user}, Mutual friends: {mutual_count}")
            else:
                print("No friend recommendations found.")

        elif choice == "2" and logged_in_user:
            while True:
                print("\n--- Friend Menu ---")
                print("1. View Friend Requests")
                print("2. Send Friend Request")
                print("3. Accept Friend Request")
                print("4. Decline Friend Request")
                print("5. Back to Main Menu")
                sub_choice = input("Enter your choice: ")

                if sub_choice == "1":
                    friend_requests = sm_graph.get_friend_requests(logged_in_user)
                    print(f"Friend requests for {logged_in_user}: {friend_requests}")
                
                elif sub_choice == "2":
                    friend_username = input("Enter the username of the friend you want to add: ")
                    sm_graph.send_friend_request(logged_in_user, friend_username)

                elif sub_choice == "3":
                    friend_username = input("Enter the username of the friend to accept: ")
                    sm_graph.accept_friend_request(logged_in_user, friend_username)

                elif sub_choice == "4":
                    friend_username = input("Enter the username of the friend to decline: ")
                    sm_graph.decline_friend_request(logged_in_user, friend_username)

                elif sub_choice == "5":
                    break

        elif choice == "4" and not logged_in_user:
            print("Exiting...")
            break

        elif choice == "3" and logged_in_user:
            print(f"Logging out {logged_in_user}...")
            logged_in_user = None

if __name__ == "__main__":
    main()
