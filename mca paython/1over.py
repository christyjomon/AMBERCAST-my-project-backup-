# Cricket Scoreboard Management System

total_runs = 0
wickets = 0
legal_balls = 0
extras = 0
boundaries = 0

print("====== Cricket Scoreboard ======\n")

while legal_balls < 6:
    print(f"\nBall {legal_balls + 1}")

    ball_type = input(
        "Enter Ball Type (0,1,2,3,4,6, Wide, No Ball, Wicket, Run Out): "
    ).strip().lower()

    # Normal Runs
    if ball_type in ["0", "1", "2", "3", "4", "6"]:
        runs = int(ball_type)
        tqotal_runs += runs
        legal_balls += 1

        if runs == 4 or runs == 6:
            boundaries += 1

    # Wide Ball
    elif ball_type == "wide":
        extra_runs = int(input("Additional Runs: "))
        total_runs += 1 + extra_runs
        extras += 1 + extra_runs
        print("Wide Ball - Not counted as a legal ball.")

    # No Ball
    elif ball_type == "no ball":
        batsman_runs = int(input("Runs scored by batsman: "))
        total_runs += 1 + batsman_runs
        extras += 1

        if batsman_runs == 4 or batsman_runs == 6:
            boundaries += 1

        print("No Ball - Not counted as a legal ball.")

    # Wicket
    elif ball_type == "wicket":
        wickets += 1
        legal_balls += 1

    # Run Out
    elif ball_type == "run out":
        attempted = int(input("Runs Attempted: "))

        if attempted == 1:
            completed = 1
        elif attempted == 2:
            completed = 1
        else:
            completed = int(input("Completed Runs: "))

        total_runs += completed
        wickets += 1
        legal_balls += 1

    else:
        print("Invalid input! Please enter a valid ball type.")

print("\n========= SCOREBOARD =========")
print("Total Runs   :", total_runs)
print("Wickets      :", wickets)
print("Legal Balls  :", legal_balls)
print("Extras       :", extras)
print("Boundaries   :", boundaries)
print("OVER COMPLETED")
