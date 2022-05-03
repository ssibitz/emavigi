#
# EMA vigi - simple tool for getting all results in plain text
# Copyright (c) 2022 by Stefan Sibitz
#
import json, requests

# Search word
SEARCH_FOR = "covid-19 vaccine"
# Site urls
SITE_URL = "https://vigiaccess.org"
SEARCH_4_DRUG_URL = SITE_URL + "/protocol/IProtocol/search"
LIST_ALL_GROUPS = SITE_URL + "/protocol/IProtocol/distribution"
LIST_ALL_TERMS = SITE_URL + "/protocol/IProtocol/primaryTerm"

# List to de obfuscate invalid chars, but readable !
UTF8_CHAR_MAPPING_LIST = {
# Indigene Zeichen
5024: "D",
5025: "R",
5026: "T",
5029: "i",
5033: "y",
5034: "A",
5035: "J",
5036: "E",
5043: "W",
5046: "G",
5047: "M",
5051: "H",
5058: "h",
5058: "Z",
5062: "I",
5071: "b",
5074: "R",
5081: "V",
5082: "S",
5086: "L",
5086: "C",
5090: "P",
5094: "K",
5095: "d",
5108: "B",
# Römische Zeichen
8544: "I",
8548: "V",
8553: "X",
8556: "L",
8557: "C",
8558: "D",
8559: "M",
8560: "i",
8564: "v",
8569: "x",
8572: "l",
8573: "c",
8574: "d",
8575: "m",
# Lisu
42192: "B",
# Invalid chars to "ignore"
173: "",
8289: "",
8290: "",
8291: "",
}

def DeObfuscated(val):
    res = ""
    pos = 0
    print("Value: '"+val+"'")
    for char in val:
        UniCodeValue = ord(char)
        pos = pos + 1
        print(str(pos) + ".) " + "Char at: [" + str(UniCodeValue) + "], '" + char + "'")
        if char in [" "]:
            res = res + char
        elif UniCodeValue in UTF8_CHAR_MAPPING_LIST:
            res = res + UTF8_CHAR_MAPPING_LIST[UniCodeValue]
        elif str.isalnum(char):
            res = res + char
    print("Result: "+res)
    return res

def Dump_Effect_Details(Outputfile, EncryptedDrugID, EncryptedSocId):
    # Get complete detail list
    Page = 0
    while(True):
        FullDetailsList = requests.post(LIST_ALL_TERMS, json = [{"DrugId": {"DrugId": {"Encrypted": EncryptedDrugID}}, "SocId": {"SocId": {"Encrypted": EncryptedSocId}}, "Page": Page}])
        if "Pts" in FullDetailsList.json():
            FullDetailsListJson = FullDetailsList.json()["Pts"]
            if len(FullDetailsListJson) > 0:
                for Detail in FullDetailsListJson:
                    Count = Detail["Count"]
                    Description = DeObfuscated(Detail["Description"]["Obfuscated"])
                    Outputfile.write("    "+Description+ " ("+ str(Count) + " ADRs)"+ "\n")
                Page = Page + 1 # Next page at next loop
            else:
                break # No details any more -> finished
        else:
            break  # No details any more -> finished

def Dump_Effect_Group(Outputfile, val, EncryptedDrugID):
    Count = val["Count"]
    EncryptedSocId = val["SocId"]["SocId"]["Encrypted"]
    Description = DeObfuscated(val["Description"]["Obfuscated"])
    Outputfile.write(Description+ " ("+ str(Count) + " ADRs)" + "\n")
    Dump_Effect_Details(Outputfile, EncryptedDrugID, EncryptedSocId)

def LoadSite(Outputfile):
    # Search for drug id
    SearchFor = requests.post(SEARCH_4_DRUG_URL, json = [SEARCH_FOR])
    EncryptedDrugID = SearchFor.json()[0]["DrugId"]["DrugId"]["Encrypted"]
    # Get complete result
    FullSearchList = requests.post(LIST_ALL_GROUPS, json = [{"DrugId": {"Encrypted": EncryptedDrugID}}])
    Reactions = FullSearchList.json()["Reaction"]
    # List all from result
    for AllSideEffects in Reactions:
        Dump_Effect_Group(Outputfile, AllSideEffects, EncryptedDrugID)

if __name__ == '__main__':
    # File name to output
    OutputfileName = "EMA-Vigiaccess.txt"
    Outputfile = open(OutputfileName, "w", encoding="utf-8")
    LoadSite(Outputfile)
    Outputfile.close()
    print("Done.")
