import os
import json
import hashlib

# Paper Types: 
# ['core', 'masters', 'memorabilia', 'commander', 
# 'expansion', 'archenemy', 'box', 'draft_innovation', 
# 'masterpiece', 'arsenal', 'funny', 'starter', 'duel_deck', 
# 'from_the_vault', 'promo', 'premium_deck', 'planechase', 
# 'token', 'minigame', 'vanguard', 'spellbook']

##############
# Constants

ALL_PRINTINGS_FILENAME = "AllPrintings.json"
ATOMIC_CARDS_FILENAME = "AtomicCards.json"
CATEGORIES_FILENAME = "categories.json"
COUNTS_FILENAME = "card_counts.json"
DECKLISTS_PATH = "decklists"
OUTPUT_PATH = "output"
BASIC_LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
BLACKLISTED_SETS = ["SUNF"]


##############
# Helper Functions

def load_json(filename) -> dict:
    f = open(filename)
    obj = json.load(f)
    f.close()

    return obj


def load_decklist(deck_path):
    df = open(deck_path)
    dtext = df.readlines()
    df.close()

    deck = dict()

    for line in dtext:
        line = line.strip()
        line_spl = line.split(' ')

        if len(line) == 0 or len(line_spl) <= 1 or not line_spl[0].isnumeric():
            continue

        card_quantity = int(line_spl[0])
        card_name = ' '.join(line_spl[1:])

        if card_name not in deck:
            deck[card_name] = 0

        deck[card_name] += card_quantity

    return deck


def hash_decklist(decklist: dict) -> str:
    """returns the hex digest of the hash"""
    decklist_array = sorted([f'{key}: {decklist[key]}' for key in decklist.keys()])
    return hashlib.md5('\n'.join(decklist_array).encode()).hexdigest()


def add_to_totals(totals: dict, deck: dict):
    """Adds the deck's cards to the totals seen. Remember to clean basics first."""
    for cardname in deck.keys():
        if cardname not in totals["card_counts"]:
            totals["card_counts"][cardname] = 0

        totals["card_counts"][cardname] += deck[cardname]


def save_totals(totals: dict):
    totals["hashes"] = list(totals["hashes"])

    tf = open(COUNTS_FILENAME, 'w')
    json.dump(totals, tf)
    tf.close()

    totals["hashes"] = set(totals["hashes"])


def print_report(category_stats, category_stats_no_lands, categories):
    print("\t\tNonbasic Lands\t\t\t|\t\tNo Lands")
    print("-" * 32 + "|" + "-" * 38)
    print("Category\t\tNo. Cards\t\t| Category\t\tNo. Cards")
    print("\t\t\t\t\t\t\t\t|")

    for cat in categories.keys():
        if cat not in category_stats:
            category_stats[cat] = 0

        if cat not in category_stats_no_lands:
            category_stats_no_lands[cat] = 0

        print(f"{cat}\t\t{category_stats[cat]}", end='')

        if category_stats[cat] < 1000:
            print('\t', end='')
        print(f"\t\t\t| {cat}\t\t{category_stats_no_lands[cat]}")

    print()


def cleanup_database(database: dict):
    """Double-sided cards have // for some reason. This method truncates those."""
    cardnames = list(database.keys())

    for cardname in cardnames:
        if "//" in cardname:
            splitname = cardname.split("//")

            if splitname[0].strip() == splitname[1].strip():
                continue

            newname = splitname[0].strip()

            database[newname] = database[cardname]


##############
# Classes
class DeckAnalyzer:
    def __init__(self, card_database):
        self.atomic_cards = card_database

    def get_card(self, cardname):
        """Produces the card object associated with cardname"""
        if cardname == 'Loot, the Key to Everything':
            return self.atomic_cards['data']['Vizzerdrix'][0]

        return self.atomic_cards['data'][cardname][0]

    def clean_basics(self, deck: dict):
        """Removes all basic lands from deck. Modifies deck."""
        for cardname in list(deck.keys()):
            card = self.get_card(cardname)

            if "Basic" in card["supertypes"]:
                del deck[cardname]

    @staticmethod
    def sort_card(card, category_data: dict) -> str:
        """returns the category name the card falls under. Or, UNKNOWN if it doesn't fall under one."""
        first_printing = card['firstPrinting']

        if len(first_printing) == 4 and first_printing[0] == 'P':
            first_printing = first_printing[1:]

        for category in category_data.keys():
            if first_printing in category_data[category]:
                return category

        print(f"[!] Unknown set {first_printing} for card '{card['name']}'")

        return 'UNKNOWN'

    def analyze_deck(self, deck: dict, category_data: dict):
        """Produces the category counts of the non-basic cards in deck, with and without lands"""
        categories = dict()
        categories_no_land = dict()

        for cardname in list(deck.keys()):
            card = self.get_card(cardname)

            if 'firstPrinting' not in card.keys():
                print(f"[!] Ignoring card with no first printing: {card['name']}")
                continue

            if card['firstPrinting'] in BLACKLISTED_SETS:
                continue

            card_category = self.sort_card(card, category_data)

            if card_category not in categories:
                categories[card_category] = 0

            categories[card_category] += 1

            if "Land" in card["types"]:
                continue

            if card_category not in categories_no_land:
                categories_no_land[card_category] = 0

            categories_no_land[card_category] += 1

        return categories, categories_no_land


##############
# Main program code

if __name__ == "__main__":
    # First, load the category data and put it into sets
    categories = load_json(CATEGORIES_FILENAME)

    for category in categories.keys():
        categories[category] = set(categories[category])

    # Next, load the existing count data so we don't double count
    card_counts = load_json(COUNTS_FILENAME)
    card_counts["hashes"] = set(card_counts["hashes"])

    # Now do the data collection
    atomic_cards = load_json(ATOMIC_CARDS_FILENAME)
    cleanup_database(atomic_cards['data'])
    kowalski = DeckAnalyzer(atomic_cards)

    for filename in os.listdir(DECKLISTS_PATH):
        f = os.path.join(DECKLISTS_PATH, filename)

        if os.path.isfile(f):
            # If we're on a deck file, load it and process it
            deck = load_decklist(f)
            deck_hash = hash_decklist(deck)

            if deck_hash in card_counts["hashes"]:
                continue  # Skip decks we've already processed

            kowalski.clean_basics(deck)

            add_to_totals(card_counts, deck)
            card_counts['hashes'].add(deck_hash)
            save_totals(card_counts)

            category_stats, category_stats_nolands = kowalski.analyze_deck(deck, categories)

            print(f"Report for deck {filename} ({deck_hash}):\n")
            print_report(category_stats, category_stats_nolands, categories)

    total_cats, total_cats_nl = kowalski.analyze_deck(card_counts["card_counts"], categories)
    print(f"Report for totals:\n")
    print_report(total_cats, total_cats_nl, categories)
