import json
import urllib.parse


search_str = 'https://www.zillow.com/nc/sold/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-85.9748856015625%2C%22east%22%3A-73.7471023984375%2C%22south%22%3A31.961578653542134%2C%22north%22%3A38.281401066213%7D%2C%22mapZoom%22%3A7%2C%22usersSearchTerm%22%3A%22NC%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A36%2C%22regionType%22%3A2%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22price%22%3A%7B%22min%22%3A50000%2C%22max%22%3Anull%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22doz%22%3A%7B%22value%22%3A%2260%22%7D%2C%22mp%22%3A%7B%22min%22%3A250%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%7D'

def data_from_url(url: str):
    parsed_query = urllib.parse.parse_qs(urllib.parse.urlparse(search_str).query)
    encoded_json_string = parsed_query.get('searchQueryState', [None])[0]
    json_string = urllib.parse.unquote(encoded_json_string)
    search_dict = json.loads(json_string)

    print("✅ Successfully Extracted and Decoded Dictionary:")
    print(json.dumps(search_dict, indent=2))
    print("\n--- Verification ---")
    print(f"Type of result: {type(search_dict)}")
    print(f"Extracted User Search Term: {search_dict['usersSearchTerm']}")

def url_from_data(data: dict):

    base_url = 'https://www.zillow.com/nc/sold/'
    json_string = json.dumps(data)
    encoded_json_string = urllib.parse.quote(json_string)
    final_url = f"{base_url}?searchQueryState={encoded_json_string}"
    
    print("## ✨ Final Zillow URL")
    print(final_url)
    print("\n--- Verification ---")
    # Check if the resulting URL matches the original structure
    original_prefix = 'https://www.zillow.com/nc/sold/?searchQueryState='
    # print(f"URL Length: {len(final_url)}")


if __name__=="__main__":
    # data_from_url(search_str)

    url_from_data(
{
  "filterState": {
    "auc": { "value": False },
    "cmsn": { "value": False },
    "fore": { "value": False },
    "fsba": { "value": False },
    "fsbo": { "value": False },
    "nc": { "value": False },
    "rs": { "value": True },
    "sort": { "value": "globalrelevanceex" }
  },

  "isListVisible": True,
  "isMapVisible": True,
  "mapBounds": {
    "east": -75.400119,
    "north": 36.588157,
    "south": 33.752878,
    "west": -84.321869
  },
  "mapZoom": 7,
  "pagination": {},
  "regionSelection": [{ "regionId": 36, "regionType": 2 }],
  "usersSearchTerm": "NC"
}
    )