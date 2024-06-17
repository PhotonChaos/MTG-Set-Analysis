from analysis import COUNTS_FILENAME, ATOMIC_CARDS_FILENAME, load_json


counts = load_json(COUNTS_FILENAME)
atomics = load_json(ATOMIC_CARDS_FILENAME)

leaderboard = []

for card in counts["card_counts"].keys():
    if card in atomics['data'] and 'Land' in atomics['data'][card][0]['types']:
        continue

    leaderboard.append((card, counts["card_counts"][card]))

leaderboard.sort(key=lambda x: x[1], reverse=True)

for i in range(10):
    print(f"{i+1}. {leaderboard[i][0]}: {leaderboard[i][1]}")