
# =========================================================
# COLLEGE TOURNAMENT SCORING SYSTEM
# =========================================================
# Features:
# - Team and individual registration
# - One-event-only competitors
# - Team and individual events
# - Automatic point allocation
# - Event leaderboards
# - Overall leaderboard
# - Save/load data using JSON
# =========================================================

import json

POINTS_TABLE = [10, 8, 6, 5, 4, 3, 2, 1]


# =========================================================
# CLASSES
# =========================================================

class Participant:
    def __init__(self, name, participant_type, single_event=False):
        self.name = name
        self.participant_type = participant_type
        self.single_event = single_event
        self.total_points = 0

    def add_points(self, points):
        self.total_points += points

    def to_dict(self):
        return {
            "name": self.name,
            "participant_type": self.participant_type,
            "single_event": self.single_event,
            "total_points": self.total_points
        }


class Team(Participant):
    def __init__(self, team_name, members):
        super().__init__(team_name, "Team")
        self.members = members

    def to_dict(self):
        data = super().to_dict()
        data["members"] = self.members
        return data


class Event:
    def __init__(self, event_name, event_type, category):
        self.event_name = event_name
        self.event_type = event_type
        self.category = category
        self.results = []

    def add_result(self, participant_name, rank, points):
        self.results.append({
            "participant": participant_name,
            "rank": rank,
            "points": points
        })

    def to_dict(self):
        return {
            "event_name": self.event_name,
            "event_type": self.event_type,
            "category": self.category,
            "results": self.results
        }


# =========================================================
# GLOBAL DATA
# =========================================================

participants = []
events = []


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_participant(name):
    for participant in participants:
        if participant.name.lower() == name.lower():
            return participant
    return None


def award_points(rank):
    if rank <= len(POINTS_TABLE):
        return POINTS_TABLE[rank - 1]
    return 1


# =========================================================
# REGISTRATION FUNCTIONS
# =========================================================

def register_team():
    print("\n=== REGISTER TEAM ===")

    team_name = input("Enter team name: ")

    if find_participant(team_name):
        print("Team already exists.")
        return

    members = []

    for i in range(5):
        member = input(f"Enter member {i + 1} name: ")
        members.append(member)

    team = Team(team_name, members)
    participants.append(team)

    print("Team registered successfully.")


def register_individual():
    print("\n=== REGISTER INDIVIDUAL ===")

    name = input("Enter competitor name: ")

    if find_participant(name):
        print("Competitor already exists.")
        return

    single = input("Single event only? (Y/N): ").upper()

    single_event = single == "Y"

    competitor = Participant(name, "Individual", single_event)
    participants.append(competitor)

    print("Individual registered successfully.")


# =========================================================
# EVENT FUNCTIONS
# =========================================================

def create_event():
    print("\n=== CREATE EVENT ===")

    name = input("Event name: ")

    event_type = input("Event type (Team/Individual): ").title()

    if event_type not in ["Team", "Individual"]:
        print("Invalid event type.")
        return

    category = input("Category (Sporting/Academic): ").title()

    event = Event(name, event_type, category)

    events.append(event)

    print("Event created successfully.")


def enter_event_results():
    print("\n=== ENTER EVENT RESULTS ===")

    if not events:
        print("No events available.")
        return

    for index, event in enumerate(events):
        print(f"{index + 1}. {event.event_name}")

    try:
        choice = int(input("Choose event: ")) - 1
        event = events[choice]
    except:
        print("Invalid selection.")
        return

    valid_participants = [
        p for p in participants
        if p.participant_type == event.event_type
    ]

    if not valid_participants:
        print("No valid participants.")
        return

    print("\nParticipants:")
    for p in valid_participants:
        print("-", p.name)

    rankings_used = []

    while True:
        participant_name = input(
            "\nEnter participant name (or 'done'): "
        )

        if participant_name.lower() == "done":
            break

        participant = find_participant(participant_name)

        if not participant:
            print("Participant not found.")
            continue

        if participant.participant_type != event.event_type:
            print("Wrong participant type.")
            continue

        try:
            rank = int(input("Enter rank: "))
        except:
            print("Invalid rank.")
            continue

        if rank in rankings_used:
            print("Rank already used.")
            continue

        rankings_used.append(rank)

        points = award_points(rank)

        participant.add_points(points)

        event.add_result(participant.name, rank, points)

        print(f"{participant.name} awarded {points} points.")


# =========================================================
# DISPLAY FUNCTIONS
# =========================================================

def display_leaderboard():
    print("\n=== OVERALL LEADERBOARD ===")

    sorted_participants = sorted(
        participants,
        key=lambda x: x.total_points,
        reverse=True
    )

    for position, participant in enumerate(sorted_participants, start=1):
        print(
            f"{position}. "
            f"{participant.name} "
            f"({participant.participant_type}) - "
            f"{participant.total_points} pts"
        )


def display_event_results():
    print("\n=== EVENT RESULTS ===")

    if not events:
        print("No events available.")
        return

    for event in events:
        print(f"\n{event.event_name}")
        print("-" * 30)

        sorted_results = sorted(
            event.results,
            key=lambda x: x["rank"]
        )

        for result in sorted_results:
            print(
                f"Rank {result['rank']} - "
                f"{result['participant']} "
                f"({result['points']} pts)"
            )


# =========================================================
# SAVE / LOAD FUNCTIONS
# =========================================================

def save_data():
    data = {
        "participants": [],
        "events": []
    }

    for participant in participants:
        data["participants"].append(participant.to_dict())

    for event in events:
        data["events"].append(event.to_dict())

    with open("tournament_data.json", "w") as file:
        json.dump(data, file, indent=4)

    print("Data saved successfully.")


def load_data():
    global participants
    global events

    try:
        with open("tournament_data.json", "r") as file:
            data = json.load(file)

        participants = []

        for p in data["participants"]:

            if p["participant_type"] == "Team":
                team = Team(p["name"], p["members"])
                team.total_points = p["total_points"]
                participants.append(team)

            else:
                competitor = Participant(
                    p["name"],
                    p["participant_type"],
                    p["single_event"]
                )

                competitor.total_points = p["total_points"]

                participants.append(competitor)

        events = []

        for e in data["events"]:
            event = Event(
                e["event_name"],
                e["event_type"],
                e["category"]
            )

            event.results = e["results"]

            events.append(event)

        print("Data loaded successfully.")

    except FileNotFoundError:
        print("No save file found.")


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():

    while True:

        print("\n=================================================")
        print(" COLLEGE TOURNAMENT SCORING SYSTEM ")
        print("=================================================")

        print("1. Register Team")
        print("2. Register Individual")
        print("3. Create Event")
        print("4. Enter Event Results")
        print("5. View Overall Leaderboard")
        print("6. View Event Results")
        print("7. Save Data")
        print("8. Load Data")
        print("9. Exit")

        choice = input("\nEnter choice: ")

        if choice == "1":
            register_team()

        elif choice == "2":
            register_individual()

        elif choice == "3":
            create_event()

        elif choice == "4":
            enter_event_results()

        elif choice == "5":
            display_leaderboard()

        elif choice == "6":
            display_event_results()

        elif choice == "7":
            save_data()

        elif choice == "8":
            load_data()

        elif choice == "9":
            print("Exiting program...")
            break

        else:
            print("Invalid option.")


# =========================================================
# START PROGRAM
# =========================================================

main_menu()
