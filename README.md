# emavigi
Tool to load data from ema - vigiaccess and decode data's

Loading datas from:
https://vigiaccess.org

by using the search keyword:
covid-19 vaccine

# 1.) Call search with search keyword to get list of search words
https://vigiaccess.org/protocol/IProtocol/search
and JSON-Body:
["covid-19 vaccine"]

# 2.) Parsing first encrypted DrugId from list and call service for getting "Overview" list:
https://vigiaccess.org/protocol/IProtocol/distribution
and JSON-Body:
[{"DrugId": {"Encrypted": EncryptedDrugID}}]

# 3.) For each "Overview" point load "Details" from service until no more data (No more pages):
EncryptedSocId = "Encrypted overview Id"
https://vigiaccess.org/protocol/IProtocol/primaryTerm
and JSON-Body:
[{"DrugId": {"DrugId": {"Encrypted": EncryptedDrugID}}, "SocId": {"SocId": {"Encrypted": EncryptedSocId}}, "Page": Page}]

**The text is encrypted in unicode so a simple mapping function is used to decode ...
