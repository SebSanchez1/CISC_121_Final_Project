import gradio as gr

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
    

demo = gr.Interface(
    fn=sort,
    inputs=["text"],
    outputs=["text"],
    api_name="predict"
)

demo.launch()