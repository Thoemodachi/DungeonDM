from backend.player_api import PlayerDrivenCampaign

def main():
    player_id = input("Enter your player name: ").strip()
    campaign = PlayerDrivenCampaign()

    print("\n--- Dungeon Master ---")
    print("Welcome, adventurer! The story begins. Your choices shape the world.\n")

    while True:
        player_input = input("> Your action: ").strip()
        if player_input.lower() in ["quit", "exit"]:
            print("\n--- Dungeon Master ---")
            print("The adventure ends here. Farewell, brave adventurer!")
            break

        response = campaign.play_turn(player_id, player_input)
        print("\n--- Dungeon Master ---")
        print(response)
        print("\n(Type 'quit' to exit the adventure)\n")

if __name__ == "__main__":
    main()
