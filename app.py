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


with gr.Blocks() as demo:
    with gr.Sidebar():
        numbers = gr.Textbox(label = "Numbers")
        random_amount = gr.Slider(1, 50, step=1, label = "Amount of Random Characters")
        chracter_type = gr.Radio(choices = ["Numbers", "Letters", "Both"], label = "Type of Characters", value = "Numbers")
        random_btn = gr.Button("Generate Random Chracters")

    sorted_list = gr.Textbox(label = "Sorted List")
    sort_btn = gr.Button("Sort")

    random_btn.click(fn = random_characters, inputs = (random_amount, chracter_type), outputs = numbers, api_name = "Generate Random Characters")
    sort_btn.click(fn = sort, inputs = numbers, outputs = sorted_list, api_name = "Sort")

demo.launch()