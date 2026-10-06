import json 
from pathlib import Path #paths for json to connect also \n is really nice and so efficient

# reads and opens json file to put into one place so i can easily put individual things in lists to make it easier also no write function so the base data can stay the same
file_path = Path(__file__).resolve().parent / "starter_data.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# current stat of the game in lists so it can be easily updated mid game and reset in a new game
current_order_index = 0
cash = data["starting_cash"]
restocks_left = data["restock_limit"]

# puts individual data points into lists as a shortcut so i can pull the data easier
ingredients = data["ingredients"]
menu = data["menu"]
orders = data["orders"]

# Live inventory starts at JSON stock values
live_inventory = {ing_id: info["stock"] for ing_id, info in ingredients.items()}

def end_of_game():#ends the game but its fancy because its persistant until it recieves a valid input
    print("\nShift complete")
    print("You finished all 10 orders!")
    print(f"Final cash: ${cash:.2f}")

    while True:
        choice = input("Restart game? (y/n): ").lower()
        if choice == "y":
            restart_game()
            return
        elif choice == "n":
            print("Goodbye!")
            exit()
        else:
            print("Please type y or n.")

def restart_game():#resets everything back to its starting data from json and puts it in live updatable and readable data without intereferring with base data
    global current_order_index, cash, restocks_left, live_inventory #global makes this viewable by every function 
#if the game is not restarted it will still end the program but when you resume it it will load the file of the last save file
    current_order_index = 0
    cash = data["starting_cash"]
    restocks_left = data["restock_limit"]
    live_inventory = {ing_id: info["stock"] for ing_id, info in ingredients.items()}

    print("\nGame restarted!\n")


def see_options_again():
    input("\nPress ENTER to see options") #ease of life factor that makes it so that when you ask for some data you can view it without the menu pop up until you press enter


def menu_and_recipe(): #biggest part of this code that i use a lot is the block that calculates how to divide everything into 2 even columns based on how much space the items take
    blocks = [] # besides the blocks it also allows us to view the menu and the recipes and prices of items on the menu
    for item_id, item in menu.items():
        block = []
        name = item["name"] #use  of the list shortcut
        price = item["price"]
        block.append(f"{item_id}: {name} - ${price}")
        block.append("Recipe:")
        for ingredient_id, amount in item["recipe"].items():
            ingredient_name = ingredients[ingredient_id]["name"]
            block.append(f"  {ingredient_name} ({ingredient_id}): {amount}")
        blocks.append(block)

    for i in range(0, len(blocks), 2): #this is where the actual calculations for the blocks exist
        left = blocks[i]
        right = blocks[i+1] if i+1 < len(blocks) else []
        max_lines = max(len(left), len(right))
        for line_index in range(max_lines):
            l = left[line_index] if line_index < len(left) else ""
            r = right[line_index] if line_index < len(right) else ""
            print(f"{l:<45} {r}")
        print()

    see_options_again()


def View_stock_and_cash(): #viewing data pretty much 
    lines = []
    for ing_id, info in ingredients.items():
        name = info["name"]
        stock = live_inventory[ing_id]
        cost = info["cost"]
        line = f"{ing_id}: {name} | stock: {stock} | cost: ${cost}"
        lines.append(line)

    for i in range(0, len(lines), 2): #block calculation again 
        left = lines[i]
        right = lines[i+1] if i+1 < len(lines) else ""
        print(f"{left:<55} {right}")

    see_options_again()


def Inspect_current_order(): #the order number and what in it are also put into individual lists so this is where we access them 
    order = orders[current_order_index]
    items = order["items"]
    blocks = []
    total_order_cost = 0

    for item_id, quantity in items.items():
        smoothie = menu[item_id]
        name = smoothie["name"]
        price = smoothie["price"]
        total_order_cost += price * quantity #order price based on the items and amount of items in the order 

        block = [
            f"{item_id}: {name}", #block calc again 
            f"Quantity: {quantity}",
            f"Price each: ${price}"
        ]
        blocks.append(block)

    for i in range(0, len(blocks), 2):
        left = blocks[i]
        right = blocks[i+1] if i+1 < len(blocks) else []
        max_lines = max(len(left), len(right))
        for line_index in range(max_lines):
            l = left[line_index] if line_index < len(left) else ""
            r = right[line_index] if line_index < len(right) else ""
            print(f"{l:<45} {r}")
        print()

    print(f"Total: ${total_order_cost:.2f}") #puts it all in one nice space 
    see_options_again()


def use_ingredient(ing_id, amount): #subtracts/checks the used ingredients and current amount of ingredients and makes decisions depending on each 
    if live_inventory[ing_id] >= amount: #we have enough subtract 
        live_inventory[ing_id] -= amount
    else:
        print(f"Not enough {ingredients[ing_id]['name']}.") #we dont have enough 


def serve_current_order():
    global current_order_index, cash

    order = orders[current_order_index]
    items = order["items"]


    for smoothie_id, qty in items.items(): #checks ingredient availability
        recipe = menu[smoothie_id]["recipe"]
        for ing_id, amount in recipe.items():
            if live_inventory[ing_id] < amount * qty:
                print(f"Not enough {ingredients[ing_id]['name']} to serve this order.")
                return

    for smoothie_id, qty in items.items(): #deducts ingredients and adds money
        recipe = menu[smoothie_id]["recipe"]
        price = menu[smoothie_id]["price"]
        cash += price * qty

        for ing_id, amount in recipe.items():
            use_ingredient(ing_id, amount * qty)

    print("Order served")
    current_order_index += 1
    if current_order_index >= len(orders):
        end_of_game()


def buy_supplies():
    global cash, restocks_left #buys supplies based on how many we have and how many we need to max out inventory then subtracts the amount of money calculated for how much the player bought 

    if restocks_left <= 0: #blocks from use if the player doesnt have any restocks left 
        print("No restocks left for this shift.")
        return

    total_cost = 0
    refill_amounts = {}

    for ing_id, ing_data in ingredients.items():
        max_amount = ing_data["stock"]
        current_amount = live_inventory[ing_id]
        missing = max_amount - current_amount

        if missing > 0:
            cost = missing * ing_data["cost"]
            total_cost += cost
            refill_amounts[ing_id] = missing

    if total_cost == 0:
        print("\nAll supplies are already full.\n")#already full
        return

    if cash < total_cost:
        print(f"Not enough cash. Need ${total_cost:.2f}, but you have ${cash:.2f}.")#youre too poor 
        return

    cash -= total_cost
    restocks_left -= 1

    for ing_id, amount in refill_amounts.items():
        live_inventory[ing_id] += amount

    print(f"Supplies refilled for ${total_cost:.2f}. Remaining cash: ${cash:.2f}.")
    print(f"Restocks left: {restocks_left}")


def view_shift_progress(): #recieves all shift progress and puts it all neetly in one printout 
    completed = current_order_index
    total_orders = len(orders)
    remaining = total_orders - completed

    print("\nShift Progress")
    print(f"Orders completed: {completed}")
    print(f"Orders remaining: {remaining}")
    print(f"Current cash: ${cash:.2f}")
    print(f"Restocks left: {restocks_left}")
    print("\n")

    see_options_again()


def save_progress(): #takes in all the current data stored in the lists that get updated mid game into a json format to create a new json file so the game can be resumed 
    save_data = { #putting it all together 
        "current_order_index": current_order_index,
        "cash": cash,
        "restocks_left": restocks_left,
        "live_inventory": live_inventory
    }

    with open("save_file.json", "w") as save_file: #writing the new file 
        json.dump(save_data, save_file, indent=4)

    print("\nProgress saved!\n")

def load_progress(): #checks for a savefile json file if there is itll open everything in it to update all live updated lists with the save file data 
    global current_order_index, cash, restocks_left, live_inventory #if there is no save file it start a fresh game with all the base data

    save_path = Path("save_file.json")
    if not save_path.exists():
        return  

    with open(save_path, "r") as save_file:
        save_data = json.load(save_file)

    current_order_index = save_data["current_order_index"]
    cash = save_data["cash"]
    restocks_left = save_data["restocks_left"]
    live_inventory = save_data["live_inventory"]

    print("\nSave file loaded! Resuming your shift...\n")

load_progress()

def persistant_menu(): #menu that never ends unless told to itll keep asking what the player wants to do until instructed not to but will only take valid inputs
    global current_order_index, cash, restocks_left
    while True:
        print(f"Order {current_order_index+1} of 10 -- cash: ${cash} -- Restocks left: {restocks_left}")
        print("1.View menu and recipes      2.View stock and cash\n3.Inspect current order      4.Buy supplies\n5.Serve current order        6.Decline current order\n7.View shift progress        8.Save progress\n9.Save and quit")
        
        try:
            chosen_option = int(input("choose 1-9: "))
            if chosen_option == 1:
                menu_and_recipe()
            elif chosen_option == 2:
                View_stock_and_cash()
            elif chosen_option == 3:
                Inspect_current_order()
            elif chosen_option == 4:
                buy_supplies()
            elif chosen_option == 5:
                serve_current_order()
            elif chosen_option == 6:
                print("Order declined.")
                current_order_index += 1
                if current_order_index >= len(orders):
                    end_of_game()
            elif chosen_option == 7:
                view_shift_progress()
            elif chosen_option == 8:
                save_progress()
            elif chosen_option == 9:
                save_progress()
                print("Game saved. Goodbye!")
                break
            else:
                print("please give a valid number (1-9)")
                continue
        except ValueError:
            print("Please enter a valid number")

persistant_menu()
