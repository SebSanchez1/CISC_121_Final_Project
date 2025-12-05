import gradio as gr
import random
import time
import re

# Possible characters to sort
valid_characters = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

class SortVisualizer: # [Used ChatGPT for most of animation: Used prompt "create animation for merge sort"]
    """
    Handles elements for the merge sort visualization

    Tracks multiple states for each item in the list thats being sorting. 
    Track things like depth, color and order. 
    Also controls HTML styling for objects, speed of animation, and stop button.
    
    Attributes:
        items (list): List of items to sort.
        state (dict): Visual state for each item.
        delay (float): Delay between animation frames.
        stop_signal (list): Shared stop signal to halt animation.
    """
    
    
    def __init__(self, items, speed=5, stop_signal=None):
        """
        Parameters:
            items (list): List of items to sort.
            speed (int): Speed of animation (1-10).
            stop_signal (list): Shared stop signal to halt animation.
        """

        # Wrap items to track them: {'val': value, 'id': unique_id}
        self.items = [{'val': x, 'id': i} for i, x in enumerate(items)]
        # Track visual state: {id: {'depth': d, 'color': c, 'shade_mod': 0}}
        self.state = {item['id']: {'depth': 0, 'color': 'black', 'shade_mod': 0} for item in self.items}
        # Speed 1 (slow) to 10 (fast). 
        # Base delay: 2.0s / speed
        self.delay = 2.0 / max(1, speed)
        # Initialize stop signal
        self.stop_signal = stop_signal if stop_signal is not None else [False]


    def check_stop(self):
        """
        Check if the stop signal has been triggered.

        Returns:
            bool: True if stop signal is triggered, False otherwise.
        """

        return self.stop_signal[0]


    def get_color(self, depth, shade_mod=0):
        """
        Determines the color of an item based on its depth and shade modification.

        Parameters:
            depth (int): Depth level of the item in the recursion.
            shade_mod (int): Shade modification (-1 for darker, +1 for lighter).

        Returns:
            str: RGB color string.
        
        """

        # Rainbow palette based on depth
        colors = [
            (0, 0, 0),       # Black (Initial)
            (255, 0, 0),     # Red
            (255, 127, 0),   # Orange
            (204, 204, 0),   # Darker Yellow
            (0, 128, 0),     # Green
            (0, 0, 255),     # Blue
            (75, 0, 130),    # Indigo
            (148, 0, 211)    # Violet
        ]
        
        # Color based on depth
        base_rgb = colors[min(depth, len(colors) - 1)]
        
        # Unpack
        r, g, b = base_rgb

        # Apply shade modification (lighter or darker)
        if shade_mod > 0:
            # Lighter: blend with white
            # Increased contrast factor
            factor = min(0.7, shade_mod * 0.25) 
            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)
        elif shade_mod < 0:
            # Darker: blend with black
            # Increased contrast factor
            factor = min(0.7, abs(shade_mod) * 0.25)
            r = int(r * (1 - factor))
            g = int(g * (1 - factor))
            b = int(b * (1 - factor))
            
        return f"rgb({r}, {g}, {b})"


    def render(self): # [ChatGPT used for most of HTML/CSS styling]
        """
        Uses HTML/CSS to render the current state of the items.

        Returns:
            str: HTML string representing the current state.
        """

        # Container for animation
        html = '<div class="animation-window" style="position:relative; height:600px; width:100%; background-color:#1a1a2e; border-radius:8px; overflow:hidden;">'
        
        # Responsive Layout using Percentages 
        n = len(self.items)
        if n == 0: return html + "</div>"
        item_width_pct = 100.0 / n
        
        for idx, item in enumerate(self.items):
            # Unpack states for each item
            props = self.state[item['id']]

            depth = props['depth']
            shade_mod = props.get('shade_mod', 0)
            
            # Force color black if merging left and right
            # Else set color based on depth and shade
            if props.get('force_color'):
                color = props['force_color']
            else:
                color = self.get_color(depth, shade_mod)
                
            val = item['val']
            
            # Height based on value
            if isinstance(val, int):
                height = max(20, val * 3)
            elif str(val).isdigit():
                height = max(20, int(val) * 3)
            else:
                height = 60
                
            # Calculate position of item    
            left_pct = idx * item_width_pct
            top = 20 + depth * 60
            
            # HTML style for each item
            # Each item displayed as a colored box with value inside
            html += f'''
            <div style="
                position: absolute;
                left: {left_pct}%;
                top: {top}px;
                width: {item_width_pct}%;
                height: {height}px;
                padding: 0 2px; /* Horizontal spacing */
                box-sizing: border-box;
                display: flex;
                justify-content: center;
                transition: all {self.delay}s ease;
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    background: {color};
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                    border: 1px solid rgba(255,255,255,0.1);
                ">
                    {val}
                </div>
            </div>
            '''

        html += "</div>"

        return html


    def update_depths(self, indices, depth, shade_delta=0):
        """
        Updates the depth beased on recursion level.
        And updates shade modification based on left or right side of the merge.

        Parameters:
            indices (iterable): Indices of items to update.
            depth (int): New depth level.
            shade_delta (int): Change in shade modification (-1, 0, +1).
        """

        for idx in indices:
            # Determine item ID
            item_id = self.items[idx]['id']

            # Update depth
            self.state[item_id]['depth'] = depth
            
            # Update shade modification
            if shade_delta != 0:
                self.state[item_id]['shade_mod'] = self.state[item_id].get('shade_mod', 0) + shade_delta
            
            # Remove force color if exists
            if 'force_color' in self.state[item_id]:
                del self.state[item_id]['force_color']


    def merge_sort(self, start, end, depth): # [ChatGPT used for time delays to create smooth animation]
        """
        Main merge sort algorithm with animation steps happening simultaneously.

        Parameters:
            start (int): Start index of the sublist to sort.
            end (int): End index of the sublist to sort.
            depth (int): Current depth level in recursion.
        """

        # Base Case
        if self.check_stop(): return
        if end - start < 2:
            return

        mid = (start + end) // 2
        
        # Update left recursion depth (Lighter)
        self.update_depths(range(start, mid), depth + 1, shade_delta=1)
        yield self.render()
        if self.check_stop(): return
        time.sleep(self.delay)
        
        # Left recursion
        yield from self.merge_sort(start, mid, depth + 1)
        if self.check_stop(): return
        
        # Update right recursion depth (Lighter)
        self.update_depths(range(mid, end), depth + 1, shade_delta=-1)
        yield self.render()
        if self.check_stop(): return
        time.sleep(self.delay)
        
        # Right recursion
        yield from self.merge_sort(mid, end, depth + 1)
        if self.check_stop(): return

        # Split list into two for merge logic
        left = self.items[start:mid]
        right = self.items[mid:end]
        
        # Initialize merge list and pointers
        merged = []
        i, j = 0, 0
        
        # Main Merge Loop
        while i < len(left) and j < len(right):
            if self.check_stop(): return
            # Compare
            val_l = left[i]['val']
            val_r = right[j]['val']
            
            # Determing if left or right is smaller
            if str(val_l).isdigit() and str(val_r).isdigit():
                cond = int(val_l) <= int(val_r)
            else:
                cond = str(val_l) <= str(val_r)

            # Pick smaller item
            if cond:
                picked = left[i]
                i += 1
            else:
                picked = right[j]
                j += 1
            
            # Move picked item to depth + 2 (merge zone)
            self.state[picked['id']]['depth'] = depth + 2
            # Black always while merging
            self.state[picked['id']]['force_color'] = 'black'
            
            merged.append(picked)
            
            # Update current items list
            current_window = merged + left[i:] + right[j:]
            self.items[start:end] = current_window
            
            yield self.render()
            time.sleep(self.delay) 

        # Append remaining left
        while i < len(left):
            if self.check_stop(): return
            picked = left[i]
            # Update depth to merge zone
            self.state[picked['id']]['depth'] = depth + 2
            # Black always while merging
            self.state[picked['id']]['force_color'] = 'black'
            merged.append(picked)
            i += 1

            # Update current items list
            self.items[start:end] = merged + left[i:] + right[j:]
            yield self.render()
            time.sleep(self.delay)

        # Append remaining right
        while j < len(right):
            if self.check_stop(): return
            picked = right[j]
            # Update depth to merge zone
            self.state[picked['id']]['depth'] = depth + 2
            # Black always while merging
            self.state[picked['id']]['force_color'] = 'black'
            merged.append(picked)
            j += 1

            # Update current items list
            self.items[start:end] = merged + left[i:] + right[j:]
            yield self.render()
            time.sleep(self.delay)

        # Delay before resetting
        time.sleep(self.delay * 0.5)
        
        # Reset shade modifiers
        for item in left:
             self.state[item['id']]['shade_mod'] -= 1
        for item in right:
             self.state[item['id']]['shade_mod'] += 1
             
        # Update depths back to current depth
        self.update_depths(range(start, end), depth, shade_delta=0)
        yield self.render()
        time.sleep(self.delay)


def animate_sort(input_str, speed, stop_signal):
    """
    Activates the merge sort animation using object.

    Parameters:
        input_str (str): Input string of items to sort.
        speed (int): Speed of animation (1-10).
        stop_signal (list): Shared stop signal to halt animation.
    """

    # Return empty if no input
    if not input_str:
        return ""
    
    # Reset stop signal
    stop_signal[0] = False
    
    # Parse input
    items = input_str.split()
    
    # Convert to ints when possible for proper comparison
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)

    # Create visualizer object
    viz = SortVisualizer(parsed_items, speed, stop_signal)
    
    # Initial State
    yield viz.render()
    if viz.check_stop(): return
    time.sleep(1.0)
    
    # Start Sort
    yield from viz.merge_sort(0, len(parsed_items), 0)
    
    # Final 'Done' state
    if not viz.check_stop():
        yield viz.render()


def reset_sort(input_str, stop_signal):
    """
    Pauses/stops the current animation and resets the display.

    Parameters:
        input_str (str): Input string of items to sort.
        stop_signal (list): Shared stop signal to halt animation.
    """

    # Signal to stop the animation
    stop_signal[0] = True
    
    # Yield the initial state to match generator expectation
    if not input_str:
        yield ""
        return
    
    # Parse input
    items = input_str.split()

    # Convert to ints when possible for proper comparison
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)
            
    # Create visualizer object for reset state
    viz = SortVisualizer(parsed_items)
    yield viz.render()


def update_display_and_sanitize(text):
    """
    Updates the display in real-time as user types.
    Also runs sanitizes function to enforce input constraints.

    Parameters:
        text (str): Current input text.

    Returns:
        tuple: Sanitized text and current visual display HTML.
    """

    # Sanitize first
    sanitized = sanitize_input(text)
    
    # If empty, return nothing to display
    if not sanitized:
        return sanitized, ""
        
    # Parse input
    items = sanitized.split()

    # Convert to ints when possible for proper comparison
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)
            
    # Create visualizer object for current state
    viz = SortVisualizer(parsed_items)
    return sanitized, viz.render()


def random_characters(amount, type_choice):
    """
    Generates a string of random characters based on user specifications.

    Parameters:
        amount (int): Number of characters to generate.
        type_choice (str): Type of characters to generate ("Numbers", "Letters", "Both").

    Returns:
        str: Generated string of random characters.
    """

    # Ensure amount is int and initialize
    amount = int(amount)
    characters = []

    # Crete random list of 1/2 digit number
    if type_choice == "Numbers":
        for i in range(amount):
            if random.randint(0,1) == 0:
                characters.append(random.randint(0,9))
            else:
                characters.append(random.randint(10, 99))

    # Create random list of letters
    elif type_choice == "Letters":
        for i in range(amount):
            characters.append(valid_characters[(random.randint(0,51)) + 10])

    # Create random list of 1/2 digit number and letters
    else:
        for i in range(amount):
            if random.randint(0,1) == 0:
                if random.randint(0,1) == 0:
                    characters.append(random.randint(0,9))
                else:
                    characters.append(random.randint(10, 99))
            else:
                characters.append(valid_characters[(random.randint(0,51)) + 10])

    # Return as space-separated string
    return " ".join(map(str, characters))


def update_button_text(choice):
    """
    Changes the random generation button text based on character type choice.

    Parameters:
        choice (str): Type of characters to generate ("Numbers", "Letters", "Both").

    Returns:
        gr.Button: Updated button with new text.
    """

    # Update button text based on choice
    if choice == "Numbers":
        return gr.Button("Generate Random Numbers")
    elif choice == "Letters":
        return gr.Button("Generate Random Letters")
    else:
        return gr.Button("Generate Random Characters")


def sanitize_input(text): # [Used ChatGPT for re library]
    """
    Sanitizes user input to enforce constraints:
        - Only alphanumeric characters and spaces allowed.
        - No double spaces.
        - Max 20 items.
        - Numbers truncated to 2 digits, letters to 1 character.

    Parameters:
        text (str): Input text to sanitize.

    Returns:
        str: Sanitized text.
    """

    # Return empty if no input
    if not text:
        return ""
    
    # Allow only alphanumeric and space
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    # No double spaces
    text = re.sub(r'\s+', ' ', text)
    
    tokens = text.split(' ')
    
    # Enforce strict 20 item limit
    if len(tokens) > 20:
        tokens = tokens[:20]
        return " ".join(tokens)
    
    # Limit numbers to 2 digits, letters to 1 character
    processed_tokens = []
    for token in tokens:
        if not token:
            continue
        if token[0].isdigit():
            num_str = "".join(filter(str.isdigit, token))
            processed_tokens.append(num_str[:2])
        elif token[0].isalpha():
            let_str = "".join(filter(str.isalpha, token))
            processed_tokens.append(let_str[:1])
        else:
            processed_tokens.append(token)
            
    # Reconstruct sanitized string
    result = " ".join(processed_tokens)
    
    # Preserve trailing space if we are under the limit
    if len(processed_tokens) < 20 and text.endswith(' '):
        result += " "
        
    return result


# Gradio Interface
with gr.Blocks() as merge_sort_visualizer:

    # State to manage stop signal [False]
    stop_signal = gr.State([False])
    
    # Sidebar for inputs
    with gr.Sidebar():
        characters = gr.Textbox(label = "Characters", lines=4)
        random_amount = gr.Slider(1, 20, step=1, label = "Amount of Random Characters")
        chracter_type = gr.Radio(choices = ["Numbers", "Letters", "Both"], label = "Type of Characters", value = "Numbers")
        random_btn = gr.Button("Generate Random Characters", variant="primary")
        speed_slider = gr.Slider(1, 10, value=5, step=1, label="Animation Speed (1=Slow, 10=Fast)")

    # Main display area
    sorted_list = gr.HTML(label = "Sorted List")

    # Sorting control buttons
    sort_btn = gr.Button("Sort", variant="primary")
    reset_btn = gr.Button("Reset / Stop", variant="secondary")

    # Create ramdom characters
    random_btn.click(fn = random_characters, inputs = (random_amount, chracter_type), outputs = characters, api_name = "Generate Random Characters")
    
    # Start sort animation
    sort_event = sort_btn.click(fn = animate_sort, inputs = [characters, speed_slider, stop_signal], outputs = sorted_list)
    
    # Reset / Stop animation
    reset_btn.click(fn = reset_sort, inputs = [characters, stop_signal], outputs = sorted_list)

    # Update random button text based on character type
    chracter_type.change(fn = update_button_text, inputs = chracter_type, outputs = random_btn)
    
    # Real-time updates to dispay and sanitization
    characters.change(fn = update_display_and_sanitize, inputs = characters, outputs = [characters, sorted_list])

# Launch the Gradio app
merge_sort_visualizer.launch()