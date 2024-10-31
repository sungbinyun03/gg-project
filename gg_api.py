from matching.getHosts import extract_top_hosts
import json
import subprocess
from matching.firstpass import run_firstpass
from matching.entities import extract_entities
from matching.media_classify import classify_media
from matching.mediaMatcher import match_media
from matching.winProb import Winners
from matching.nominee import get_people_nom
from matching.mediaNom import get_media_nom
from matching.round1 import get_winners
from matching.mostDrunk import get_most_drunk
from matching.Awards import get_award_list

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    with open("./resFiles/firstpass.json", "r") as f:
        tweets = json.load(f)

    hosts = extract_top_hosts(tweets)
    print("HOSTS: ", hosts)
    return hosts

def get_awards(year):
    '''Awards is ea list of strings. Do NOT change the nam
    of this function or what it returns.'''
    # Your code here
    awards = get_award_list()
    print("@@@ AWARDS: ", awards)
    return awards

def get_mostDrunk():
    mostDrunk = get_most_drunk()
    print(mostDrunk)
    return mostDrunk

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''

    ## FOR PEOPLE
    # Win prob (using people.json -> organized_awards.json, likely_nominees.json)
    # Nominee (combining above files into final_noms_people.json)
    Winners()
    get_people_nom()
    ## FOR MEDIA:
    get_media_nom()
    

    with open("./resFiles/people_nominees.json", "r") as f:
        peopleNoms = json.load(f)

    with open("./resFiles/media_nominees.json", "r") as f:
        mediaNoms = json.load(f)

    nominees = {**peopleNoms, **mediaNoms}
    with open("./resFiles/final_nominees.json", "w") as f:
        json.dump(nominees, f, indent=4)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = get_winners(year)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters = []
    return presenters

def pre_ceremony(year):
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    #FIRSTPASS.PY
    #ENTITIES.PY
    #MEDIA_CLASSIFY.py
    #MEDIA_MATCHER.py
    run_firstpass(year)
    extract_entities()
    classify_media()
    match_media()

 
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    pre_ceremony(2013)
    get_hosts(2013)
    get_awards(2013)
    get_nominees(2013)
    get_winner(2013)
    get_mostDrunk()
    return

if __name__ == '__main__':
    main()
