import json
from statistics import mean
from gender_guesser.detector import Detector

# Initialize the gender detector
detector = Detector()

# Load JSON data
with open('../resFiles/organized_awards_noMatching.json') as f:
    award_nominees = json.load(f)

with open('../resFiles/firstpass_timeStamp.json') as f:
    tweets = json.load(f)

with open('../resFiles/likely_nominees.json') as f:
    likely_nominees = json.load(f)

# Function to calculate average timestamp
def calculate_average_timestamp(mentions):
    timestamps = [int(tweet['timestamp_ms']) for tweet in mentions if 'timestamp_ms' in tweet]
    return mean(timestamps) if timestamps else None

# Find mentions of a person in tweets
def get_mentions(person_name, tweets):
    return [tweet for tweet in tweets if person_name.lower() in tweet['text'].lower()]

# Determine expected gender from the award category
def get_expected_gender(category):
    if 'actress' in category:
        return 'female'
    elif 'actor' in category:
        return 'male'
    return None

# Check if a person matches the expected gender
def is_gender_match(name, expected_gender):
    guessed_gender = detector.get_gender(name.split()[0])
    if expected_gender == 'female':
        return guessed_gender in ['female', 'mostly_female']
    elif expected_gender == 'male':
        return guessed_gender in ['male', 'mostly_male']
    return False

# Process each likely winner
winner_timestamps = {}
for category, info in award_nominees.items():
    likely_winner = info.get("likely winner")
    if likely_winner:
        expected_gender = get_expected_gender(category)
        # Check if the likely winner matches the expected gender
        if is_gender_match(likely_winner, expected_gender):
            # Get mentions of the likely winner and calculate average timestamp
            winner_mentions = get_mentions(likely_winner, tweets)
            winner_avg_timestamp = calculate_average_timestamp(winner_mentions)
            if winner_avg_timestamp:
                winner_timestamps[category] = {
                    "likely winner": likely_winner,
                    "winner_avg_timestamp": winner_avg_timestamp,
                    "expected_gender": expected_gender
                }

# Create a set of all likely winners to exclude them from nominees
all_likely_winners = {info["likely winner"] for info in winner_timestamps.values()}

# Process each nominee in likely_nominees and calculate average timestamp
nominee_timestamps = {}
for nominee, data in likely_nominees.items():
    if nominee not in all_likely_winners:  # Exclude if nominee is a likely winner
        nominee_mentions = get_mentions(nominee, tweets)
        nominee_avg_timestamp = calculate_average_timestamp(nominee_mentions)
        if nominee_avg_timestamp:
            nominee_timestamps[nominee] = nominee_avg_timestamp

# Structure results: Compare average timestamps of each winner with nominees and apply gender filtering
results = {}
for category, winner_info in winner_timestamps.items():
    likely_winner = winner_info["likely winner"]
    winner_avg_timestamp = winner_info["winner_avg_timestamp"]
    expected_gender = winner_info["expected_gender"]

    # Find nominees closest to the winner's average timestamp, filtered by gender and excluding other likely winners
    closest_nominees = sorted(
        [
            (nominee, abs(nominee_avg_timestamp - winner_avg_timestamp))
            for nominee, nominee_avg_timestamp in nominee_timestamps.items()
            if is_gender_match(nominee, expected_gender)
        ],
        key=lambda x: x[1]
    )[:4]  # Get top 3 closest nominees

    results[category] = {
        "likely winner": likely_winner,
        "winner_avg_timestamp": winner_avg_timestamp,
        "top_4_closest_nominees": closest_nominees
    }

# Save results to JSON
with open('categorized_winners_and_nominees.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Script executed successfully! Results are saved in 'categorized_winners_and_nominees.json'")
