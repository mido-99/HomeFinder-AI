import json
import urllib.parse


search_str = 'https://www.zillow.com/new-york-ny/sold/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-74.73705099511717%2C%22east%22%3A-73.20857809472655%2C%22south%22%3A40.32616362257277%2C%22north%22%3A41.05919368995071%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A6181%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22New%20York%20NY%22%2C%22listPriceActive%22%3Atrue%7D'

parsed_query = urllib.parse.parse_qs(urllib.parse.urlparse(search_str).query)
encoded_json_string = parsed_query.get('searchQueryState', [None])[0]
json_string = urllib.parse.unquote(encoded_json_string)
search_dict = json.loads(json_string)

print("✅ Successfully Extracted and Decoded Dictionary:")
print(json.dumps(search_dict, indent=2))
print("\n--- Verification ---")
print(f"Type of result: {type(search_dict)}")
print(f"Extracted User Search Term: {search_dict['usersSearchTerm']}")