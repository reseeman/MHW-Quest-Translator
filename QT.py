import requests
from bs4 import BeautifulSoup
import pyperclip
import xml.etree.ElementTree as ET
import sys
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def get_quest_translation(query):
    url = f"https://mhw.poedb.tw/eng/quest/{query}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error on page retrieval.")
        print("Response Code: ", response.status_code)
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            header = row.find('th')
            value = row.find('td')
            if header and value:
                if language in header:
                    return value
    
    print("Couldn't find a translation.")
    return None

Tk().withdraw()
input_file_path = askopenfilename(title="Select XML file", filetypes=[("XML files", "*.xml")])
if not input_file_path:
    print("No file selected. Exiting...")
    exit()

tree = ET.parse(input_file_path)
root = tree.getroot()

print("")
print("Languages:\nUS English | FR Français | ES Español | DE Deutsch |\nIT Italiano | RU Русский | PL Polski | O Português do Brasil\n")
print("*If it says 'Couldn't find a translation', then most likely you \nhave entered the wrong language. It should be entered\nexactly as in the example between the '|' signs ")
print("")

language = input("Enter your language (just as in the examples above): ")
if language.lower() == "exit":
    exit()

quests_element = root.find('Quests')
if quests_element is None:
    print("The <Quests> element was not found in the XML file. Exiting...")
    exit()

world_element = quests_element.find('World')
if world_element is None:
    print("The <World> element was not found in the XML file. Exiting...")
    exit()

world_quests = world_element.findall('Quest')
total_quests = len(world_quests)

start_time = time.time()

try:
    for index in range(6, total_quests):
        quest = world_quests[index]
        quest_id = quest.get('Id')
        quest_id_padded = quest_id.zfill(5)

        translation = get_quest_translation(quest_id_padded)
        if translation:
            result_text = str(translation).lstrip('<td>').split('<')[0]
            quest.set('String', result_text)

        elapsed_time = time.time() - start_time
        processed_quests = index + 1 - 6
        remaining_quests = total_quests - processed_quests - 6
        
        if processed_quests > 0:
            avg_time_per_quest = elapsed_time / processed_quests
            estimated_remaining_time = avg_time_per_quest * remaining_quests
            
            hours, remainder = divmod(estimated_remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            sys.stdout.write(f"\rUpdating quest ID: {quest_id_padded} ({processed_quests}/{total_quests - 5}) | Estimated time remaining: {int(hours)}h {int(minutes)}m {int(seconds)}s.")
            sys.stdout.flush()

except KeyboardInterrupt:
    print("\nProcess interrupted by user. Saving current progress...")
except Exception as e:
    print(f"\nAn error occurred: {e}. Saving current progress...")

output_file_path = asksaveasfilename(title="Save updated quests XML", defaultextension=".xml", filetypes=[("XML files", "*.xml")])
if output_file_path:
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
    print(f"\nTranslations have been updated and saved to '{output_file_path}'.")
else:
    print("\nNo file selected for saving. Exiting without saving...")