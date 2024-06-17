from analysis import load_json, ATOMIC_CARDS_FILENAME

atomic_cards = load_json(ATOMIC_CARDS_FILENAME)
totalToughness = 0
cardsCounted = 0

toughnessArray = []

for cardName in atomic_cards['data']:
    card = atomic_cards['data'][cardName]
    if card[0]['manaValue'] <= 3 and 'Creature' in card[0]['types']:
        toughness = int(card[0]['toughness']) if card[0]['toughness'].isdigit() else 1

        toughnessArray.append(toughness)
        totalToughness += toughness
        cardsCounted += 1

print(f"Average Toughness: {totalToughness / cardsCounted : .5f}")
toughnessArray.sort()
if len(toughnessArray) % 2 == 0:
    print((toughnessArray[len(toughnessArray)//2] + toughnessArray[len(toughnessArray)//2 - 1])/2)
else:
    print(toughnessArray[len(toughnessArray)//2])
