AUS_STATES = ["ACT","NSW","NT","QLD","SA","TAS","VIC","WA"]

MALES = ["Mr","Mr."]
FEMALES = ["Mrs","Mrs.","Ms","Ms.","Miss","Miss."]
TITLES = ["Dr","Dr.","Prof","Prof.","A/Prof","Conjoint","Associate","Professor"]
MILITARY_RANKS = ["WO","WO1","WO2","COL","LTCOL","BRIG","AIRCDRE","MAJGEN",
                  "Warrant","Officer","Principal","Air","Chief","Marshal",
                  "Hon","Hon.","Justice"]
PREFIXES = set(MALES + FEMALES + TITLES + MILITARY_RANKS)
GENDERS = set(MALES + FEMALES)
MALES = set(MALES)
FEMALES = set(FEMALES)

POST_NOMINALS = ["AC","AM","AO","CBE","CPA","CSC","CSM","DSC","FAA","FAHA",
                 "FAICD","FASSA","FTSE","GAICD","KC","NSC","MBE","MP","OAM",
                 "OLY","OZNM","PFHEA","PSM","QC","QSO","RAN","RANR","RFD","SC"]
SUFFIXES = set(POST_NOMINALS)