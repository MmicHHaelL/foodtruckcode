import json 
from pathlib import Path
import winsound
file_path = Path(__file__).resolve().parent / "starter_data.json"
with open(file_path, "r", encoding="utf-8") as file:
    inventory = json.load(file)
def menu_and_recipe():
    print(f"{product_id} {product['name']} {product['price']}")

def song():
    for i in range(10):    
        winsound.Beep(1000, 200)
        winsound.Beep(500, 1000)
        winsound.Beep(1000, 200)
        winsound.Beep(500, 1000)
        winsound.Beep(1000, 200)
        winsound.Beep(500, 1000)

def persistant_menu():
    while True:
        print("Order # of 10 -- cash: # -- Restocks left: #")
        print("1.view menu and recipes      2.option\n3.option      4.option\n5.option      6.option\n7.option      8.option\n9.option")
        chosen_option = int(input("choose 1-9: "))
        if chosen_option == 1:
            menu_and_recipe()
        elif chosen_option == 2:
            song()
            break
persistant_menu()