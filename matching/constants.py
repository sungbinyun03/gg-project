import json
import os

categorized_media_path = './resFiles/categorized_media.json'
if os.path.exists(categorized_media_path):
    with open(categorized_media_path, 'r') as f:
        media_data = json.load(f)
else:
    media_data = {"TV": {"Drama": [], "Comedy or Musical": []},
                  "Film": {"Drama": [], "Comedy or Musical": [], "Animated Film": [], "Foreign Film": []}}


OFFICIAL_AWARDS = [
    'best actress in a motion picture - drama',
    'best actor in a motion picture - drama',
    'best actress in a motion picture - comedy or musical',
    'best actor in a motion picture - comedy or musical',
    'best actress in a supporting role in a motion picture',
    'best actor in a supporting role in a motion picture',
    'best director - motion picture',
    'best actress in a television series - drama',
    'best actor in a television series - drama',
    'best actress in a television series - comedy or musical',
    'best actor in a television series - comedy or musical',
    'best actress in a mini-series or motion picture made for television',
    'best actor in a mini-series or motion picture made for television',
    'best actress in a supporting role in a series, mini-series or motion picture made for television',
    'best actor in a supporting role in a series, mini-series or motion picture made for television'
]

AWARD_SYNONYMS = {
    'television': ['television', 'tv'],
    'motion picture': ['motion picture', 'film', 'movie'],
    'series': ['series', 'show'],
    'mini-series': ['mini-series', 'limited series']
}

POSITIVE_PHRASES = {
    r'\bwins\b.*\bBest\b': 3, r'\bawarded\b.*\bfor\b': 3,
    r'\bwon\b.*\baward\b': 3, r'\btakes home\b': 3,
    r'\breceives\b.*\baward\b': 2, r'\bbest\b.*\bgoes to\b': 3,
    r'\bwins everything\b': 2, r'\bhigh fives\b.*\bafter win\b': 2,
    r'\bGolden Globe winner\b': 3, r'\bso proud\b.*\baward\b': 1,
    r'\bdeserves\b.*\baward\b': 1, r'\bcongratulations\b.*\bnominated\b': 1,
    r'\bshould win\b': 1
}

NEGATIVE_PHRASES = {
    r'\bdidn\'t win\b': -3, r'\blost\b.*\baward\b': -2,
    r'\brobbed\b': -2, r'\bshould have won\b': -1,
    r'\bdeserved\b.*\bwin\b': -1, r'\bso sad\b.*\bdeserved to win\b': -1,
    r'\bwas hoping\b.*\bto win\b': -1, r'\bnever wins\b': -2
}

AWARD_CATEGORIES = {
    "best television series - drama": media_data["TV"]["Drama"],
    "best television series - comedy or musical": media_data["TV"]["Comedy or Musical"],
    "best motion picture - drama": media_data["Film"]["Drama"],
    "best motion picture - comedy or musical": media_data["Film"]["Comedy or Musical"],
    "best animated feature film": media_data["Film"]["Animated Film"],
    "best foreign language film": media_data["Film"]["Foreign Film"],
    "best screenplay - motion picture": [],
    "best mini-series or motion picture made for television": [],
    "best original score - motion picture": [],
    "best original song - motion picture": []
}

ADDITIONAL_AWARD_KEYWORDS = {
    "best screenplay - motion picture": "best screenplay",
    "best mini-series or motion picture made for television": "best miniseries",
    "best original score - motion picture": "best original score",
    "best original song - motion picture": "best original song"
}


CATEGORIES = {
    "TV": {
        "Drama": ["drama", "crime", "thriller", "mystery"],
        "Comedy or Musical": ["comedy", "sitcom", "musical", "parody", "romantic comedy"]
    },
    "Film": {
        "Foreign Film": ["danish", "french"],
        "Animated Film": ["animated", "animation", "cartoon"],
        "Comedy or Musical": ["comedy", "comedy-drama", "romantic" , "musical", "parody", "romantic comedy"],
        "Drama": ["drama", "biography", "historical", "thriller", "revisionist"],
        
    }
}


WINNING_PHRASES = [' win ', 'WIN', 'WINS', 'WON', 'Wins', 'Win', 'Nominated', 'Winner', 
                   ' won ', ' winner ', ' wins ', ' awarded ', ' takes', ' got ', ' nom', ' nominated ']


WINNER_PATTERNS = [
        r"\b(wins?|won|winner|awarded)\b",
        r"\b(is|are)\s+(the)?\s*winners?\b",
        r"\b(the\s*winner\s*is)\b",
        r"\b(goes\s*to)\b"
    ]


AWARD_NOMINEES = {
    "best screenplay - motion picture": [
        "zero dark thirty",
        "lincoln",
        "silver linings playbook",
        "argo",
        "django unchained"
    ],
    "best director - motion picture": [
        "kathryn bigelow",
        "ang lee",
        "steven spielberg",
        "quentin tarantino",
        "ben affleck"
    ],
    "best performance by an actress in a television series - comedy or musical": [
        "zooey deschanel",
        "tina fey",
        "julia louis-dreyfus",
        "amy poehler",
        "lena dunham"
    ],
    "best foreign language film": [
        "the intouchables",
        "kon tiki",
        "a royal affair",
        "rust and bone",
        "amour"
    ],
    "best performance by an actor in a supporting role in a motion picture": [
        "alan arkin",
        "leonardo dicaprio",
        "philip seymour hoffman",
        "tommy lee jones",
        "christoph waltz"
    ],
    "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television": [
        "hayden panettiere",
        "archie panjabi",
        "sarah paulson",
        "sofia vergara",
        "maggie smith"
    ],
    "best motion picture - comedy or musical": [
        "the best exotic marigold hotel",
        "moonrise kingdom",
        "salmon fishing in the yemen",
        "silver linings playbook",
        "les miserables"
    ],
    "best performance by an actress in a motion picture - comedy or musical": [
        "emily blunt",
        "judi dench",
        "maggie smith",
        "meryl streep",
        "jennifer lawrence"
    ],
    "best mini-series or motion picture made for television": [
        "the girl",
        "hatfields & mccoys",
        "the hour",
        "political animals",
        "game change"
    ],
    "best original score - motion picture": [
        "argo",
        "anna karenina",
        "cloud atlas",
        "lincoln",
        "life of pi"
    ],
    "best performance by an actress in a television series - drama": [
        "connie britton",
        "glenn close",
        "michelle dockery",
        "julianna margulies",
        "claire danes"
    ],
    "best performance by an actress in a motion picture - drama": [
        "marion cotillard",
        "sally field",
        "helen mirren",
        "naomi watts",
        "rachel weisz",
        "jessica chastain"
    ],
    "cecil b. demille award": [
        "jodie foster"
    ],
    "best performance by an actor in a motion picture - comedy or musical": [
        "jack black",
        "bradley cooper",
        "ewan mcgregor",
        "bill murray",
        "hugh jackman"
    ],
    "best motion picture - drama": [
        "django unchained",
        "life of pi",
        "lincoln",
        "zero dark thirty",
        "argo"
    ],
    "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television": [
        "max greenfield",
        "danny huston",
        "mandy patinkin",
        "eric stonestreet",
        "ed harris"
    ],
    "best performance by an actress in a supporting role in a motion picture": [
        "amy adams",
        "sally field",
        "helen hunt",
        "nicole kidman",
        "anne hathaway"
    ],
    "best television series - drama": [
        "boardwalk empire",
        "breaking bad",
        "downton abbey (masterpiece)",
        "the newsroom",
        "homeland"
    ],
    "best performance by an actor in a mini-series or motion picture made for television": [
        "benedict cumberbatch",
        "woody harrelson",
        "toby jones",
        "clive owen",
        "kevin costner"
    ],
    "best performance by an actress in a mini-series or motion picture made for television": [
        "nicole kidman",
        "jessica lange",
        "sienna miller",
        "sigourney weaver",
        "julianne moore"
    ],
    "best animated feature film": [
        "frankenweenie",
        "hotel transylvania",
        "rise of the guardians",
        "wreck-it ralph",
        "brave"
    ],
    "best original song - motion picture": [
        "act of valor",
        "stand up guys",
        "the hunger games",
        "les miserables",
        "skyfall"
    ],
    "best performance by an actor in a motion picture - drama": [
        "richard gere",
        "john hawkes",
        "joaquin phoenix",
        "denzel washington",
        "daniel day-lewis"
    ],
    "best television series - comedy or musical": [
        "the big bang theory",
        "episodes",
        "modern family",
        "smash",
        "girls"
    ],
    "best performance by an actor in a television series - drama": [
        "steve buscemi",
        "bryan cranston",
        "jeff daniels",
        "jon hamm",
        "damian lewis"
    ],
    "best performance by an actor in a television series - comedy or musical": [
        "alec baldwin",
        "louis c.k.",
        "matt leblanc",
        "jim parsons",
        "don cheadle"
    ]
}


NOMINEE_LIST = [
    "Kathryn Bigelow", "Ang Lee", "Steven Spielberg", "Quentin Tarantino", 
    "Zooey Deschanel", "Tina Fey", "Julia Louis-Dreyfus", "Amy Poehler", 
    "Hayden Panettiere", "Archie Panjabi", "Sarah Paulson", "Sofia Vergara", 
    "Alan Arkin", "Leonardo DiCaprio", "Philip Seymour Hoffman", "Tommy Lee Jones", 
    "Emily Blunt", "Judi Dench", "Maggie Smith", "Meryl Streep", 
    "Ben Affleck", "Benedict Cumberbatch", "Woody Harrelson", "Toby Jones", 
    "Clive Owen", "Nicole Kidman", "Jessica Lange", "Sienna Miller", 
    "Sigourney Weaver", "Jack Black", "Bradley Cooper", "Ewan McGregor",
    "Bill Murray", "Marion Cotillard", "Sally Field", "Helen Mirren", 
    "Naomi Watts", "Rachel Weisz", "Connie Britton", "Glenn Close", 
    "Michelle Dockery", "Julianna Margulies", "Richard Gere", "John Hawkes", 
    "Joaquin Phoenix", "Denzel Washington", "Steve Buscemi", "Bryan Cranston", 
    "Jeff Daniels", "Jon Hamm", "Alec Baldwin", "Louis C.K.", 
    "Matt LeBlanc", "Jim Parsons", "Max Greenfield", "Danny Huston", 
    "Mandy Patinkin", "Eric Stonestreet", "Amy Adams", "Sally Field", 
    "Helen Hunt", "Nicole Kidman"
]