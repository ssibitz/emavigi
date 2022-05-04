#
# EMA vigi - Tool for getting all results in plain utf-8 text
# Copyright (c) 2022 by Stefan Sibitz
#
import json, requests, logging, os, unicodedata
from unicodedata import *
from datetime import date
from os.path import exists

# Search word
SEARCH_FOR = "covid-19 vaccine"
TAB = "    "
# Site urls + services
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
    42193: "P",
    42194: "d",
    42195: "D",
    42196: "T",
    42198: "G",
    42199: "K",
    42201: "J",
    42202: "C",
    42204: "Z",
    42205: "F",
    42207: "M",
    42208: "N",
    42209: "L",
    42210: "S",
    42211: "R",
    42214: "V",
    42215: "H",
    42218: "W",
    42219: "X",
    42220: "Y",
    42222: "A",
    42224: "E",
    42226: "I",
    42227: "O",
    42228: "U",
    # Others
    927: "O",
    1054: "O",
    5056: "G",
    5059: "Z",
    5087: "C",
    5261: "J",
    5741: "X",
    8490: "K",
    11576: "V",
    11613: "X",
    65335: "W",
}

# Invalid chars to "ignore"
UTF8_INVALID_CHAR_MAPPING_LIST = {
    39: "'---APOSTROPHE",
    40: "(---LEFT PARENTHESIS",
    41: ")---RIGHT PARENTHESIS",
    44: ",---COMMA",
    45: "----HYPHEN-MINUS",
    47: "/---SOLIDUS",
    48: "0---DIGIT ZERO",
    49: "1---DIGIT ONE",
    50: "2---DIGIT TWO",
    51: "3---DIGIT THREE",
    52: "4---DIGIT FOUR",
    53: "5---DIGIT FIVE",
    54: "6---DIGIT SIX",
    55: "7---DIGIT SEVEN",
    56: "8---DIGIT EIGHT",
    57: "9---DIGIT NINE",
    173: "\u00ad---SOFT HYPHEN",
    847: "\u034f---COMBINING GRAPHEME JOINER",
    8203: "\u200b---ZERO WIDTH SPACE",
    8204: "\u200c---ZERO WIDTH NON-JOINER",
    8288: "\u2060---WORD JOINER",
    8289: "\u2061---FUNCTION APPLICATION",
    8290: "\u2062---INVISIBLE TIMES",
    8291: "\u2063---INVISIBLE SEPARATOR",
    8298: "\u206a---INHIBIT SYMMETRIC SWAPPING",
    8299: "\u206b---ACTIVATE SYMMETRIC SWAPPING",
    8300: "\u206c---INHIBIT ARABIC FORM SHAPING",
    8301: "\u206d---ACTIVATE ARABIC FORM SHAPING",
    8302: "\u206e---NATIONAL DIGIT SHAPES",
    8303: "\u206f---NOMINAL DIGIT SHAPES",
    65279: "\ufeff---ZERO WIDTH NO-BREAK SPACE",
}

# Class to access vigiaccess and parse results from services
class VigiAccess:
    def __init__(self):
        self.unknown_chars = {}
        self.InitLogging()

    def InitLogging(self):
        # Delete old log file before restarting script
        if os.path.exists('EMAVigi.log'):
            os.remove('EMAVigi.log')
        logging.basicConfig(filename='EMAVigi.log', encoding='utf-8', level=logging.INFO)

    def BuildOutputFile(self, OutputfileName):
        self.Outputfile = open(OutputfileName, "w", encoding="utf-8")
        self.LoadSite()
        self.Outputfile.close()
        self.DumpUnknownCharsList()

    def LoadSite(self):
        # Search for drug id
        logging.info(f"Loading drug search words list for {SEARCH_FOR}.")
        SearchFor = requests.post(SEARCH_4_DRUG_URL, json=[SEARCH_FOR])
        EncryptedDrugID = SearchFor.json()[0]["DrugId"]["DrugId"]["Encrypted"]
        logging.info(f"Taking first encrypted DrugId searchword: {EncryptedDrugID}")
        # Get complete result
        self.FullSearchList = requests.post(LIST_ALL_GROUPS, json=[{"DrugId": {"Encrypted": EncryptedDrugID}}])
        logging.info(
            f"Getting full crypted list of statistics: {json.dumps(self.FullSearchList.json(), indent=4, sort_keys=True)}")
        # get json datas
        TotalCount = self.FullSearchList.json()["TotalCount"]
        ReactionsJSON = self.FullSearchList.json()["Reaction"]
        GeoDisJSON = self.FullSearchList.json()["Continent"]
        AgeGroupDistributionJSON = self.FullSearchList.json()["AgeGroup"]
        SexJSON = self.FullSearchList.json()["Sex"]
        ReportsPerYearJSON = self.FullSearchList.json()["Year"]
        # TotalCount
        self.DumpTotalCount(TotalCount)
        # Reactions
        self.DumpReactions(ReactionsJSON, EncryptedDrugID)
        # Geographical distribution
        self.DumpGeographicalDistribution(GeoDisJSON)
        # Age group distribution
        self.DumpAgeGroupDistribution(AgeGroupDistributionJSON)
        # Sex
        self.DumpSex(SexJSON)
        # Reports per year
        self.DumpReportsPerYear(ReportsPerYearJSON)

    def DumpTotalCount(self, TotalCount):
        self.WriteOutputLine(f"")
        self.WriteOutputLine(f"VigiAccess™ FAQ")
        self.WriteOutputLine(f"Hover to show search tips")
        self.WriteOutputLine(f"")
        self.WriteOutputLine(f"covid-19 vaccine contains the active ingredient(s): Covid-19 vaccine.")
        self.WriteOutputLine(f"Result is presented for the active ingredient(s).")
        self.WriteOutputLine(f"Total number of records retrieved: {TotalCount}. Hover to show information")

    def DumpReactions(self, ReactionsJSON, EncryptedDrugID):
        self.WriteOutputLine(f"Distribution")
        self.WriteOutputLine(f"Adverse drug reactions (ADRs)")
        self.WriteOutputLine(f"")
        for AllSideEffects in ReactionsJSON:
            self.Dump_Effect_Group(AllSideEffects, EncryptedDrugID)

    def Dump_Effect_Group(self, val, EncryptedDrugID):
        Count = val["Count"]
        EncryptedSocId = val["SocId"]["SocId"]["Encrypted"]
        Description = self.DeObfuscated(val["Description"]["Obfuscated"])
        Output = f"{TAB}{Description} ({Count})"
        logging.info(f"Output group: {Output}")
        self.WriteOutputLine(Output)
        self.Dump_Effect_Details(EncryptedDrugID, EncryptedSocId)

    def Dump_Effect_Details(self, EncryptedDrugID, EncryptedSocId):
        Page = 0
        while (True):
            FullDetailsListJSON = requests.post(LIST_ALL_TERMS,
                                                json=[{"DrugId": {"DrugId": {"Encrypted": EncryptedDrugID}},
                                                       "SocId": {"SocId": {"Encrypted": EncryptedSocId}},
                                                       "Page": Page}])
            if "Pts" in FullDetailsListJSON.json():
                FullDetailsListJson = FullDetailsListJSON.json()["Pts"]
                if len(FullDetailsListJson) > 0:
                    for Detail in FullDetailsListJson:
                        Count = Detail["Count"]
                        Description = self.DeObfuscated(Detail["Description"]["Obfuscated"])
                        Output = f"{TAB}{TAB}{Description} ({Count})"
                        logging.info(f"Output detail: {Output}")
                        self.WriteOutputLine(Output)
                    Page = Page + 1  # Next page at next loop
                else:
                    break  # No details any more -> finished
            else:
                break  # No details any more -> finished

    def DumpGeographicalDistribution(self, GeoDisJSON):
        self.WriteOutputLine(f"")
        self.WriteOutputLine(f"Geographical distribution")
        self.WriteOutputLine(f"Continent 	Count 	Percentage")
        self.BuildAllDis(self.AddAllDis(GeoDisJSON))

    def DumpAgeGroupDistribution(self, AgeGroupDistributionJSON):
        self.WriteOutputLine(f"Age group distribution")
        self.WriteOutputLine(f"Age group 	Count 	Percentage")
        self.BuildAllDis(self.AddAllDis(AgeGroupDistributionJSON))

    def DumpSex(self, SexJSON):
        self.WriteOutputLine(f"Patient sex distribution")
        self.WriteOutputLine(f"Sex 	Count 	Percentage")
        self.BuildAllDis(self.AddAllDis(SexJSON))

    def DumpReportsPerYear(self, ReportsPerYearJSON):
        self.WriteOutputLine(f"ADR reports per year")
        self.WriteOutputLine(f"Year 	Count 	Percentage")
        self.BuildAllDis(self.AddAllDis(ReportsPerYearJSON))

# Helper functions
    def WriteOutputLine(self, val):
        self.Outputfile.write(val + "\n")

    def AddDescCount(self, json):
        self.SumCount = self.SumCount + json["Count"]
        return {"Description": json["Description"], "Count": json["Count"]}

    def AddAllDis(self, jsonlist):
        dis = []
        self.SumCount = 0
        for alldis in jsonlist:
            dis.append(self.AddDescCount(alldis))
        return dis

    def BuildAllDis(self, dis):
        for alldis in dis:
            Desc = alldis["Description"]
            Count = alldis["Count"]
            Percent = int(100 * float(Count) / float(self.SumCount))
            self.WriteOutputLine(f"{Desc} 	{Count} 	{Percent}")

    def TryDetectAnsiCharFromUnicodeName(self, char):
        return name(char)

    def IsCharValid(self, char):
        Result = False
        unicodedata.normalize('NFKD', char).encode('ascii', 'ignore')
        asciival = ord(char)
        if (asciival >= 97 and asciival <= 122):  # a-z
            Result = True
        if (asciival >= 65 and asciival <= 90):  # A-Z
            Result = True
        return Result

    def DeObfuscated(self, val):
        res = ""
        pos = 0
        InvalidChars = False
        for char in val:
            UniCodeValue = ord(char)
            pos = pos + 1
            if char in [" "]:
                res = res + char
            elif UniCodeValue in UTF8_CHAR_MAPPING_LIST:
                res = res + UTF8_CHAR_MAPPING_LIST[UniCodeValue]
            elif UniCodeValue in UTF8_INVALID_CHAR_MAPPING_LIST:
                pass
            elif self.IsCharValid(char):
                res = res + char
            else:
                InvalidChars = True
                self.unknown_chars[UniCodeValue] = f"{char}---{self.TryDetectAnsiCharFromUnicodeName(char)}"
                logging.warning(f"Unknown char '{char}' [{UniCodeValue}] found at position {pos}")
                logging.warning(f"CharName is: {self.TryDetectAnsiCharFromUnicodeName(char)}")
        if InvalidChars:
            logging.warning(f"Invalid text:")
            logging.warning(f">> {val}")
        return res

    def DumpUnknownCharsList(self):
        logging.info("SAMPLES::")
        logging.info(json.dumps(self.unknown_chars, indent=4, sort_keys=True))

# Entry point
if __name__ == '__main__':
    today = date.today()
    FileDate = date.today().strftime("%d-%m-%Y")
    FileName = f"WHO_DataBase_Covid19_{FileDate}.txt"
    vigiaccess = VigiAccess()
    vigiaccess.BuildOutputFile(FileName)
