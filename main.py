import random as rnd
from colorama import init, Fore, Back, Style
import math

#Makes colorama work on windows
init(convert=True)

factions = [
    "Retreat",      # 0
    "Ignore",       # 1
    "Subjugate",    # 2
    "infiltrate",   # 3
    "Eradicate",    # 4
    "Cooperate",    # 5
    "Contain"       # 6
]

factionColours = [
    Fore.LIGHTYELLOW_EX,      # 0
    Fore.YELLOW,       # 1
    Fore.LIGHTBLUE_EX,    # 2
    Fore.MAGENTA,   # 3
    Fore.RED,    # 4
    Fore.GREEN,    # 5
    Fore.CYAN       # 6
]

factionCentroids = [ # Note, these do not precisly map to the centroids of the regions on the sentiment map.
    (1.5,5),  #r
    (-0.5,-2), #ig
    (2,-2),  #Sub
    (1,2),  #inf
    (4,0), #e
    (-5,2), #coop
    (-4,-2) #cont
]

sentimentMap = [
    #-5 -4  -3  -2  -1  0  1  2  3  4  5
    [ 5, 5,  6,  0,  0, 0, 0, 0, 0, 0, 4], # 5
    [ 5, 5,  6,  3,  3, 3, 3, 3, 3, 4, 4], # 4
    [ 5, 5,  6,  6,  3, 3, 3, 3, 2, 4, 4], # 3
    [ 5, 5,  6,  6,  1, 3, 3, 2, 2, 4, 4], # 2
    [ 5, 6,  6,  1,  1, 3, 3, 2, 2, 4, 4], # 1
    [ 5, 6,  6,  1,  1, 3, 3, 2, 2, 4, 4], # 0
    [ 5, 6,  6,  1,  1, 1, 2, 2, 2, 4, 4], #-1
    [ 5, 6,  6,  1,  1, 1, 2, 2, 2, 2, 4], #-2
    [ 5, 6,  6,  1,  1, 1, 2, 2, 2, 2, 4], #-3
    [ 5, 6,  6,  1,  1, 1, 2, 2, 2, 2, 2], #-4
    [ 6, 6,  6,  1,  1, 1, 2, 2, 2, 2, 2]  #-5
]

factionActions = [
    [
        "Pull back Ships",
         "Consolidate Fleet",
         "build Defensive modules",
         "Abandon Habs",
         "Extract Alien Councillors from Earth",
         "Retreat Councilor through wormhole"
    ],
    [
         "build colony ships",
         "build new hab/base",
         "build Mines",
         "Build Biofactories",
        "Surveil Earth"
     ],
    [
        "Land Alien Armies",
         "Invade Nation",
         "Attack Human Military Ships",
         "Attack Human Defensive Stations",
         "Build Fleets",
         "Land Hydras",
         "Create Alien Armies",
         "Xenoforming",
         "Abduct Humans",
         "Demand Surrender",
        "Bombard earth armies",
         "Offer Deal (Insulting)"
     ],
    [
         "Abduct Humans",
         "Control Nation",
         "Control Space Asset",
         "Xenoforming",
         "Surveil Earth",
         "Land Hydras",
         "Attack Human Councillor",
         "Sabotage Human Facilities",
         "Sabotage Human Research",
         "Turn Human Councillor",
         "Summon New Councillors",
         "Build Embassy Modules",
         "Offer Deal (duplicitous)"
     ],
    [
         "Raze cities with Armies",
         "Bombard earth regions",
        "Bombard earth armies",
         "Nuke Earth Regions",
         "Build Fleets",
         "Attack Human Military Ships",
         "Attack Human Stations",
         "Build Asteroid Diversion Engines",
         "Spawn Megafauna"
     ],
    [
        "Build Embassy Modules",
        "build new hab/base",
        "Consolidate Fleet",
        "build Defensive modules",
        "Offer Deal (Fair)",
        "Offer Cease Fire",
        "Negotiate Treaty",
        "Release Controlled Nation"
    ],
    [
        "Control Space Asset",
        "Attack Human Deep Space Assets",
        "Build Defensive Stations",
        "Consolidate Fleet",
        "Offer Deal (Insulting)",
        "Offer Cease Fire",
        "Build Containment Stations in LEO",
        "Demand Surrender",
        "Disarm Nukes",
        "Offer Deal (Fair)",
        "Release Controlled Nation"
    ]
]


humanActions = {
    "Bully The Servants/Protectorate" : [+0.1,0.0] ,
    "Bully Humanity First/Resistance" : [-0.1,-0.05] ,
    "Grow Nation's Economy" : [0.0,+0.05] ,
    "Build Armies" : [0.0,0.1] ,
    "Build Fleets" : [0.05,0.15] ,
    "Research scary Technology" : [0.1,0.2] ,
    "Attack Alien Fleets (and lose)" : [0.1,-0.2] ,
    "Attack Alien Fleets (and win)": [0.1, 0.1],
    "Build Habs/Stations": [0.1, 0.05],
    "Destroy Alien Hab": [0.2, 0.1],
    "Attack Alien Army (and win)": [0.2, 0.05],
    "Attack Alien Army (and lose)": [0.0, -0.1],
    "Liberate Alien controlled region": [0.2, 0.1],
    "Attack Alien Councillor (failure)": [0.1, -0.1],
    "Attack Alien Councillor (success)": [0.3, 0.2],
    "Offer Fair Deal": [-0.2, -0.05],
    "Offer Duplicitous Deal": [0.2, 0.0],
    "Offer Insulting Deal": [0.1, 0.0],
    "Build Nukes": [0.01, 0.1],
    "Decomission Hab": [-0.01, -0.1],
    "Clear Xenoforming": [0.01, 0.01],
    "Decomission Fleet": [-0.05, -0.2]
}

def getExecutive(alienSentiment):
#    print("mapped alienSentiment:",int(-alienSentiment[1]+5),int(alienSentiment[0]+5))
    return sentimentMap[ round(-alienSentiment[1]+5) ][ round(alienSentiment[0]+5) ]


#Increasing this number centralises the power of aliens, and means that the most popular faction gains a boost to their actions
executiveBoost = 5.0

#Increasing this number makes the actions stronger, so you can see what the effect is of actions quicker.
moodBoost = 5.0


### Start model
alienSentiment = [rnd.uniform(-5.0,5.0),rnd.uniform(-5.0,4.0)]
run = True
while(run):
    print("Which action do you want to do:")
    print("(press 1,2,3,4 or 5 then Enter)")
    opt1, outcome1 = rnd.choice(list(humanActions.items()))
    opt2, outcome2 = rnd.choice(list(humanActions.items()))
    opt3, outcome3 = rnd.choice(list(humanActions.items()))
    opt4, outcome4 = rnd.choice(list(humanActions.items()))

    print("\n 1: ",opt1,"\n 2: ",opt2,"\n 3: ",opt3,"\n 4: ",opt4)
    print("Or type anything else to exit")

    playerInput = input("")
    if not playerInput.isdigit():
        print("Input is not numeric. Exiting.")
        exit()
    selection = int(playerInput)


    choice, outcome = None,None
    if selection == 1:
        choice, outcome = opt1, outcome1
    elif selection == 2:
        choice, outcome = opt2, outcome2
    elif selection == 3:
        choice, outcome = opt3, outcome3
    elif selection == 4:
        choice, outcome = opt4, outcome4
    else:
        print("Input is not 1,2,3 or 4. Exiting.")
        exit()

    #Update Alien Sentiment based on choice
    alienSentiment[0] += outcome[0]*moodBoost
    alienSentiment[1] += outcome[1]*moodBoost

    if alienSentiment[0] > 5:
        alienSentiment[0] = 4.999

    if alienSentiment[0] < -5:
        alienSentiment[0] = -4.999

    if alienSentiment[1] > 5:
        alienSentiment[1] = 4.999

    if alienSentiment[1] < -5:
        alienSentiment[1] = -4.999

    print("The current alien sentiment is:: ", alienSentiment)
#    print("The mapped alien sentiment is:",-round(alienSentiment[1]+5),round(alienSentiment[0]+4))

    #calculate faction probabilities
    reciprocals = []
    sumReciprocals = 0
    for index,cen in enumerate(factionCentroids):
        diff = ( (alienSentiment[0] - cen[0])**2 + (alienSentiment[1] - cen[1])**2 ) ** 0.5

        #Just to catch if alien sentiment is REALLY close to a faction centroid
        if math.isclose(diff,0) or diff < 1e-6:
            diff = 1000000

        if index == sentimentMap[ getExecutive(alienSentiment) ]:
            diff = diff/executiveBoost
        reciprocals.append(1/diff)
        sumReciprocals += 1/diff

    probs = []
    probs.insert(0, 0)
    support = []
    counter=0
    for r in reciprocals:
        support.append(r/sumReciprocals)
        probs.append(r/sumReciprocals + probs[counter])
        counter +=1

    print("The current alien executive is: ", factionColours[getExecutive(alienSentiment)] + factions[ getExecutive(alienSentiment) ] + Fore.RESET)
    print("The faction support is: ")
    for c, s in zip(factionColours,support):
        print(c + '{:.1%}'.format(s) + Fore.RESET)


    print("The aliens have responded with the following actions:")
    for run in (1,2,3,4,5,6,7,8):
        action = rnd.random()
        actor = None

        for n in range(1,8):
 #           print("comparing:",action,probs[n-1],probs[n])
            if action > probs[n-1] and action <= probs[n]:
                actor = n-1
#                print("faction:",actor, factions[actor])
                break

        actionString=rnd.choice(factionActions[actor])
        print(factionColours[actor] + str(run),": ",  actionString)
    print(Fore.RESET + "Your Turn!")