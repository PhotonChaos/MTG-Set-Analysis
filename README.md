# TLR Deck Analyzer
This tool was developed to collect stats on tiny leaders decks. Put decklists (as `deckName.txt` files) in the `decklists` folder, and run the program.

`card_counts.json` will keep track of the total number of each card found so far, indexed by card name. It will also keep track of the Cockatrice deck hashes seen so far (the program calculates these, so you don't need to provide them) to make sure that we don't pollute our data with a duplicate of a deck we have already analyzed. 

Since Cockatrice's hashing algorithm is pretty good, we *should* have that the size of `hashes` in `card_counts.json` is equal to the total number of decks analyzed.

## Output Format
This program once run will upadte `card_counts.json` with the total number of each card it has seen among the decks it analyzed. It will print to the screen the total number of cards in each category, with and without counting lands. 

## Decklist Format
- The decklist should be a list of english card names separated by line breaks
- Empty lines are allowed
- Do NOT include anything other than the card names

## JSON Example Formats
For `card_counts.json`:
```json
{
    "hashes": ["hash1", "hash2", "etc"],
    "card_counts": {
        "cardname1": 3,
        "cardname 2": 4
    }
}
```
defaults to:
```json
{"hashes": [], "card_counts": {}}
```