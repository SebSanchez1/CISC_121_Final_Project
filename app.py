import gradio as gr
import random
import time
import re

valid_characters = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

class SortVisualizer:
    def __init__(self, items, speed=5, stop_signal=None):
        # Wrap items to track them: {'val': value, 'id': unique_id}
        self.items = [{'val': x, 'id': i} for i, x in enumerate(items)]
        # Track visual state: {id: {'depth': d, 'color': c, 'shade_mod': 0}}
        self.state = {item['id']: {'depth': 0, 'color': 'black', 'shade_mod': 0} for item in self.items}
        self.history = []
        # Speed 1 (slow) to 10 (fast). 
        # Base delay: 2.0s / speed
        self.delay = 2.0 / max(1, speed)
        self.stop_signal = stop_signal if stop_signal is not None else [False]

    def check_stop(self):
        return self.stop_signal[0]

    def get_color(self, depth, shade_mod=0):
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
        
        base_rgb = colors[min(depth, len(colors) - 1)]
        
        # Apply shade modification (lighter or darker)
        r, g, b = base_rgb
        
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

    def render(self):
        # Increased height to 600px
        # Added class for styling hook, though inline styles dominate
        html = '<div class="animation-window" style="position:relative; height:600px; width:100%; background-color:#1a1a2e; border-radius:8px; overflow:hidden;">'
        
        n = len(self.items)
        if n == 0: return html + "</div>"
        
        # Responsive Layout using Percentages
        item_width_pct = 100.0 / n
        
        for idx, item in enumerate(self.items):
            props = self.state[item['id']]
            depth = props['depth']
            shade_mod = props.get('shade_mod', 0)
            
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
                
            left_pct = idx * item_width_pct
            top = 20 + depth * 60
            
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
        for idx in indices:
            item_id = self.items[idx]['id']
            self.state[item_id]['depth'] = depth
            
            if shade_delta != 0:
                self.state[item_id]['shade_mod'] = self.state[item_id].get('shade_mod', 0) + shade_delta
            
            if 'force_color' in self.state[item_id]:
                del self.state[item_id]['force_color']
            
    def merge_sort(self, start, end, depth):
        if self.check_stop(): return
        if end - start < 2:
            return

        mid = (start + end) // 2
        
        # Recurse Left (Lighter)
        self.update_depths(range(start, mid), depth + 1, shade_delta=1)
        yield self.render()
        if self.check_stop(): return
        time.sleep(self.delay)
        
        yield from self.merge_sort(start, mid, depth + 1)
        if self.check_stop(): return
        
        # Recurse Right (Darker)
        self.update_depths(range(mid, end), depth + 1, shade_delta=-1)
        yield self.render()
        if self.check_stop(): return
        time.sleep(self.delay)
        
        yield from self.merge_sort(mid, end, depth + 1)
        if self.check_stop(): return

        # Merge Logic
        left = self.items[start:mid]
        right = self.items[mid:end]
        
        merged = []
        i, j = 0, 0
        
        while i < len(left) and j < len(right):
            if self.check_stop(): return
            # Compare
            val_l = left[i]['val']
            val_r = right[j]['val']
            
            if str(val_l).isdigit() and str(val_r).isdigit():
                cond = int(val_l) <= int(val_r)
            else:
                cond = str(val_l) <= str(val_r)

            if cond:
                picked = left[i]
                i += 1
            else:
                picked = right[j]
                j += 1
            
            # Move picked item to depth + 2 (merge zone)
            self.state[picked['id']]['depth'] = depth + 2
            self.state[picked['id']]['force_color'] = 'black'
            
            merged.append(picked)
            
            current_window = merged + left[i:] + right[j:]
            self.items[start:end] = current_window
            
            yield self.render()
            time.sleep(self.delay) 

        # Append remaining
        while i < len(left):
            if self.check_stop(): return
            picked = left[i]
            self.state[picked['id']]['depth'] = depth + 2
            self.state[picked['id']]['force_color'] = 'black'
            merged.append(picked)
            i += 1
            self.items[start:end] = merged + left[i:] + right[j:]
            yield self.render()
            time.sleep(self.delay)

        while j < len(right):
            if self.check_stop(): return
            picked = right[j]
            self.state[picked['id']]['depth'] = depth + 2
            self.state[picked['id']]['force_color'] = 'black'
            merged.append(picked)
            j += 1
            self.items[start:end] = merged + left[i:] + right[j:]
            yield self.render()
            time.sleep(self.delay)

        # Merge complete. Move back up to 'depth'
        time.sleep(self.delay * 0.5)
        
        # Reset shade modifiers
        for item in left:
             self.state[item['id']]['shade_mod'] -= 1
        for item in right:
             self.state[item['id']]['shade_mod'] += 1
             
        self.update_depths(range(start, end), depth, shade_delta=0)
        yield self.render()
        time.sleep(self.delay)


def animate_sort(input_str, speed, stop_signal):
    if not input_str:
        return ""
    
    # Reset stop signal
    stop_signal[0] = False
    
    items = input_str.split()
    
    # Convert to ints when possible for proper comparison
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)

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
    # Signal to stop the animation
    stop_signal[0] = True
    
    # Yield the initial state to match generator expectation
    if not input_str:
        yield ""
        return
    
    items = input_str.split()
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)
            
    viz = SortVisualizer(parsed_items)
    yield viz.render()

def update_display_and_sanitize(text):
    # Sanitize first
    sanitized = sanitize_input(text)
    
    # Render initial state
    if not sanitized:
        return sanitized, ""
        
    items = sanitized.split()
    parsed_items = []
    for item in items:
        if item.isdigit():
            parsed_items.append(int(item))
        else:
            parsed_items.append(item)
            
    viz = SortVisualizer(parsed_items)
    return sanitized, viz.render()

def random_characters(amount, type_choice):
    amount = int(amount)
    characters = []

    if type_choice == "Numbers":
        for i in range(amount):
            if random.randint(0,1) == 0:
                characters.append(random.randint(0,9))
            else:
                characters.append(random.randint(10, 99))

    elif type_choice == "Letters":
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


def update_button_text(choice):
    if choice == "Numbers":
        return gr.Button("Generate Random Numbers")
    elif choice == "Letters":
        return gr.Button("Generate Random Letters")
    else:
        return gr.Button("Generate Random Characters")


def sanitize_input(text):
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
        # If we truncated, we definitely shouldn't allow a trailing space
        # to start a 21st item.
        return " ".join(tokens)
    
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
            
    result = " ".join(processed_tokens)
    
    # Preserve trailing space ONLY if we are under the limit
    # and the user actually typed a space at the end
    if len(processed_tokens) < 20 and text.endswith(' '):
        result += " "
        
    return result


with gr.Blocks() as merge_sort_visualizer:
    # State to manage stop signal [False]
    stop_signal = gr.State([False])
    
    with gr.Sidebar():
        characters = gr.Textbox(label = "Characters", lines=4)
        random_amount = gr.Slider(1, 20, step=1, label = "Amount of Random Characters")
        chracter_type = gr.Radio(choices = ["Numbers", "Letters", "Both"], label = "Type of Characters", value = "Numbers")
        random_btn = gr.Button("Generate Random Characters", variant="primary")
        
        speed_slider = gr.Slider(1, 10, value=5, step=1, label="Animation Speed (1=Slow, 10=Fast)")

    sorted_list = gr.HTML(label = "Sorted List")
    sort_btn = gr.Button("Sort", variant="primary")
    reset_btn = gr.Button("Reset / Stop", variant="secondary")

    random_btn.click(fn = random_characters, inputs = (random_amount, chracter_type), outputs = characters, api_name = "Generate Random Characters")
    
    # Pass stop_signal to animate_sort
    sort_event = sort_btn.click(fn = animate_sort, inputs = [characters, speed_slider, stop_signal], outputs = sorted_list)
    
    # Pass stop_signal to reset_sort. REMOVED cancels=[sort_event] to avoid error.
    reset_btn.click(fn = reset_sort, inputs = [characters, stop_signal], outputs = sorted_list)

    chracter_type.change(fn = update_button_text, inputs = chracter_type, outputs = random_btn)
    
    # Real-time updates: update display AND sanitize
    characters.change(fn = update_display_and_sanitize, inputs = characters, outputs = [characters, sorted_list])

merge_sort_visualizer.launch()