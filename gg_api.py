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

import json

def output_final_results(winners, hosts, mostDrunk):
    with open('./resFiles/final_nominees.json', 'r') as f:
        nominees_data = json.load(f)
    human_readable_output = ''
    json_output = {}
    human_readable_output += f'Host: {hosts}\n\n'
    json_output['Host'] = hosts
    
    for award, nominees in nominees_data.items():
        if not nominees:
            continue
        
        award_key = award.lower().strip()
        
        winner = winners.get(award_key, None)
        
        presenters = []
        
        human_readable_output += f'Award: {award.title()}\n'
        if presenters:
            human_readable_output += f'Presenters: {", ".join(presenters)}\n'
        else:
            human_readable_output += f'Presenters: N/A\n'
        if nominees:
            human_readable_output += f'Nominees: {", ".join(nominees)}\n'
        else:
            human_readable_output += f'Nominees: N/A\n'
        if winner:
            human_readable_output += f'Winner: {winner.title()}\n\n'
        else:
            human_readable_output += f'Winner: N/A\n\n'
        
        json_output[award.title()] = {
            'Presenters': presenters,
            'Nominees': nominees,
            'Winner': winner.title() if winner else None
        }
    
    human_readable_output += f'Most Drunk: {mostDrunk}\n\n'
    json_output['Most Drunk'] = mostDrunk

    json_str = json.dumps(json_output, indent=4)
    with open('./resFiles/human_readable_output.txt', 'w') as f:
        f.write(human_readable_output)
    
    with open('./resFiles/output.json', 'w') as f:
        json.dump(json_output, f, indent=4)
    
    return human_readable_output, json_str
    



def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    with open("./resFiles/firstpass.json", "r") as f:
        tweets = json.load(f)

    hosts = extract_top_hosts(tweets)
    # print("HOSTS: ", hosts)
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
    presenters = {}
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
    hosts = get_hosts(2013)
    get_awards(2013)
    get_nominees(2013)
    winners = get_winner(2013)
    mostDrunk = get_mostDrunk()
    human_output, json = output_final_results(winners, hosts, mostDrunk)
    return human_output, json

if __name__ == '__main__':
    main()
