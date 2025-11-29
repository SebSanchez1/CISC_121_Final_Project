import gradio as gr
import random

valid_characters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 
                    "a", "b", "c", "d", "e", "f", 
                    "g", "h", "i", "j", "k", "l", 
                    "m", "n", "o", "p", "q", "r", 
                    "s", "t", "u", "v", "w", "x", 
                    "y", "z", "A", "B", "C", "D", 
                    "E", "F", "G", "H", "I", "J", 
                    "K", "L", "M", "N", "O", "P", 
                    "Q", "R", "S", "T", "U", "V", 
                    "W", "X", "Y", "Z"]

def merge(list_1, list_2):
    list_m = []
    i = 0
    j = 0
    while i < len(list_1) and j < len(list_2):
        if list_1[i] <= list_2[j]:
            list_m.append(list_1[i])
            i += 1
        else:
            list_m.append(list_2[j])
            j += 1
    while i < len(list_1):
        list_m.append(list_1[i])
        i += 1
    while j < len(list_2):
        list_m.append(list_2[j])
        j += 1
    return list_m

def sort(a):
    n = len(a)
    if n < 2:
        return a
    else:
        left = a[:n//2]
        right = a[n//2:]
        return merge(sort(left), sort(right))
    
def convert_input():
    pass


def random_characters(amount, type):
    amount = int(amount)
    characters = []

    if type == "Numbers":
        for i in range(amount):
            if random.randint(0,1) == 0:
                characters.append(random.randint(0,9))
            else:
                characters.append(random.randint(10, 99))

    elif type == "Letters":
        for i in range(amount):
            characters.append(valid_characters[(random.randint(0,51)) + 10])

    else:
        for i in range(amount):
            if random.randint(0,1) == 0:
                if random.randint(0,1) == 0:
                    characters.append(random.randint(0,9))
                else:
                    characters.append(random.randint(10, 99))
            else:
                characters.append(valid_characters[(random.randint(0,51)) + 10])

    return " ".join(map(str, characters))


def handle_sort(input_str, show_bars=True):
    if not input_str:
        return ""
    
    items = input_str.split()
    
    # Check if all items are numbers
    all_numbers = True
    passed_items = []
    for item in items:
        if item.isdigit():
            passed_items.append(int(item))
        else:
            all_numbers = False
            passed_items.append(item)
            
    if all_numbers and show_bars:
        # Sort numbers and display as bars
        sorted_items = sort(passed_items)
        # Generate HTML blocks
        html = '<div style="display: flex; align-items: flex-end; justify-content: center; gap: 2px; height: 300px; overflow-x: auto;">'
        for num in sorted_items:
            height = num * 3  # Scale factor
            html += f'<div style="width: 15px; height: {height}px; background-color: #4CAF50;" title="{num}"></div>'
        html += '</div>'
        return html
    else:
        # Sort as text (for letters, mixed, or when bars is unchecked)
        if all_numbers:
            sorted_items = sort(passed_items)
        else:
            string_items = [str(x) for x in passed_items]
            sorted_items = sort(string_items)
        
        # Display as squares that fit in one view without scrolling
        num_items = len(sorted_items)
        # Calculate size based on number of items (max 20 items, so we can fit them nicely)
        # Use CSS to make them responsive
        html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; justify-content: center;">'
        for item in sorted_items:
            # Use flex-basis with calc to make squares responsive
            html += f'<div style="flex: 0 0 calc((100% - {(num_items-1)*8}px) / {min(num_items, 10)}); min-width: 40px; max-width: 80px; aspect-ratio: 1; background-color: #2196F3; color: white; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; font-size: 16px;">{item}</div>'
        html += '</div>'
        return html

def update_button_text(choice):
    if choice == "Numbers":
        return gr.Button("Generate Random Numbers")
    elif choice == "Letters":
        return gr.Button("Generate Random Letters")
    else:
        return gr.Button("Generate Random Characters")

import re

def sanitize_input(text):
    if not text:
        return ""
    
    # Allow only alphanumeric and space
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    # No double spaces
    text = re.sub(r'\s+', ' ', text)
    
    tokens = text.split(' ')
    
    # Limit to 20 items
    if len(tokens) > 20:
        tokens = tokens[:20]
    
    processed_tokens = []
    
    for token in tokens:
        if not token:
            processed_tokens.append("")
            continue
            
        if token[0].isdigit():
            # It's a number, keep only digits, max 2 chars
            num_str = "".join(filter(str.isdigit, token))
            processed_tokens.append(num_str[:2])
        elif token[0].isalpha():
            # It's a letter, keep only letters, max 1 char
            let_str = "".join(filter(str.isalpha, token))
            processed_tokens.append(let_str[:1])
        else:
            # Should not happen due to regex above, but safe fallback
            processed_tokens.append(token)
            
    return " ".join(processed_tokens)

def toggle_bars_visibility(choice):
    if choice == "Numbers":
        return gr.Checkbox(visible=True)
    else:
        return gr.Checkbox(visible=False)

with gr.Blocks() as demo:
    with gr.Sidebar():
        characters = gr.Textbox(label = "Characters", lines=4)
        random_amount = gr.Slider(1, 20, step=1, label = "Amount of Random Characters")
        chracter_type = gr.Radio(choices = ["Numbers", "Letters", "Both"], label = "Type of Characters", value = "Numbers")
        bars_checkbox = gr.Checkbox(label="Bars", value=True, visible=True)
        random_btn = gr.Button("Generate Random Characters")

    sorted_list = gr.HTML(label = "Sorted List")
    sort_btn = gr.Button("Sort")

    random_btn.click(fn = random_characters, inputs = (random_amount, chracter_type), outputs = characters, api_name = "Generate Random Characters")
    sort_btn.click(fn = handle_sort, inputs = [characters, bars_checkbox], outputs = sorted_list, api_name = "Sort")

    chracter_type.change(fn = update_button_text, inputs = chracter_type, outputs = random_btn)
    chracter_type.change(fn = toggle_bars_visibility, inputs = chracter_type, outputs = bars_checkbox)
    characters.change(fn = sanitize_input, inputs = characters, outputs = characters)

demo.launch()