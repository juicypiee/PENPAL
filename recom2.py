import json
import os
import networkx as nx

# Define file paths for user data and friend recommendations
user_data_file = "/home/jkim/python/FILE HANDLING/users_data2.json"

# Ensure the directory exists
os.makedirs(os.path.dirname(user_data_file), exist_ok=True)

# Load and save functions2
def load_user_data():
    try:
        with open(user_data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_data(users_data):
    with open(user_data_file, 'w') as file:
        json.dump(users_data, file, indent=4)

# Graph for users and friendships
class SocialMediaGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.users_data = load_user_data()  # Always load the data on initialization
        self._initialize_graph()

    def _initialize_graph(self):
        """Initialize graph nodes and edges from saved data."""
        for user in self.users_data:
            self.graph.add_node(user)
            for friend in self.users_data[user].get("friends", []):
                self.graph.add_edge(user, friend)

    def add_user(self, username, user_data):
        """Add a new user to the system."""
        if username not in self.users_data:
            self.users_data[username] = user_data
            save_user_data(self.users_data)  # Save the new user data immediately

            # Reinitialize the graph to reflect the new user and friendships
            self._initialize_graph()

    def send_friend_request(self, from_user, to_user):
        self.users_data = load_user_data()  # Reload the latest data before any operation
        if to_user not in self.users_data:
            print(f"User {to_user} does not exist.")
            return
        if from_user == to_user:
            print("You cannot send a friend request to yourself.")
            return
        if "friend_requests" not in self.users_data[to_user]:
            self.users_data[to_user]["friend_requests"] = []
        
        # Avoid adding the same request multiple times
        if from_user not in self.users_data[to_user]["friend_requests"]:
            self.users_data[to_user]["friend_requests"].append(from_user)
            save_user_data(self.users_data)
            print(f"{from_user} sent a friend request to {to_user}")
        else:
            print(f"Friend request already sent to {to_user}.")

    def accept_friend_request(self, user, from_user):
        self.users_data = load_user_data()  # Reload latest data
        if user not in self.users_data or from_user not in self.users_data.get(user, {}).get("friend_requests", []):
            print("No friend request found from this user.")
            return
        # Remove the friend request from the user's pending list
        self.users_data[user]["friend_requests"].remove(from_user)
        
        # Add the new friend to both users' friend lists if not already present
        if "friends" not in self.users_data[user]:
            self.users_data[user]["friends"] = []
        if "friends" not in self.users_data[from_user]:
            self.users_data[from_user]["friends"] = []
        
        if from_user not in self.users_data[user]["friends"]:
            self.users_data[user]["friends"].append(from_user)
        if user not in self.users_data[from_user]["friends"]:
            self.users_data[from_user]["friends"].append(user)
        
        # Add an edge between the two users in the graph
        self.graph.add_edge(user, from_user)
        
        save_user_data(self.users_data)
        print(f"{user} accepted the friend request from {from_user}")

    def decline_friend_request(self, user, from_user):
        self.users_data = load_user_data()  # Reload latest data
        if user not in self.users_data or from_user not in self.users_data.get(user, {}).get("friend_requests", []):
            print("No friend request found from this user.")
            return
        self.users_data[user]["friend_requests"].remove(from_user)
        save_user_data(self.users_data)
        print(f"{user} declined the friend request from {from_user}")

    def get_friend_requests(self, user):
        self.users_data = load_user_data()  # Reload latest data
        # Safely handle missing data
        return self.users_data.get(user, {}).get("friend_requests", [])

    def recommend_friends(self, username):
        """Recommend friends for a user based on mutual friends and current friendships."""
        self.users_data = load_user_data()  # Reload latest data
        if username not in self.graph:
            print(f"User {username} is not in the system.")
            return {}

        friends = set(self.graph.neighbors(username))
        recommendations = {}

        # Loop through each friend to find friends of friends (fof)
        for friend in friends:
            for fof in self.graph.neighbors(friend):  # fof = friend of friend
                if fof != username and fof not in friends:  # Exclude the user and their current friends
                    # Count mutual friends only once for each unique fof
                    if fof not in recommendations:
                        # Calculate mutual friends once per fof
                        mutual_count = len(set(self.graph.neighbors(fof)).intersection(friends))
                        recommendations[fof] = mutual_count

        # Sort recommendations by mutual friends count (descending order)
        sorted_recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1], reverse=True))

        return sorted_recommendations

# Account creation and login functions
def create_account(username, age, location, gender, interests, password):
    users_data = load_user_data()  # Reload user data
    if username in users_data:
        print("Username already exists. Choose a different username.")
        return False

    user = {
        "age": age,
        "location": location,
        "gender": gender,
        "interests": interests,
        "friends": [],
        "friend_requests": [],
        "password": password
    }

    sm_graph = SocialMediaGraph()
    sm_graph.add_user(username, user)
    print(f"Account for {username} created successfully.")
    return True

def login(username, password):
    users_data = load_user_data()  # Reload user data
    if username in users_data and users_data[username]["password"] == password:
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
            print("3. Exit")
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
                else:
                    print("Invalid choice. Please try again.")
        
        elif choice == "3":
            if logged_in_user:
                logged_in_user = None
                print("You have logged out.")
            else:
                break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
