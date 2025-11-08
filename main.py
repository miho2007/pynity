import tkinter as tk
from tkinter import simpledialog, filedialog
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("Pynity Engine")
root.configure(background="gray")
root.geometry("1000x500+50+50")
root.minsize(1000, 500)
root.maxsize(1000, 500)

# --- Layout ---
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=1)

# --- Scene ---
scene_frame = tk.Frame(root, bg="black")
scene_frame.grid(row=0, column=0, sticky="nsew")

scene_canvas = tk.Canvas(scene_frame, bg="gray20", highlightthickness=0)
scene_canvas.pack(fill="both", expand=True)

# --- Manager ---
manager_frame = tk.Frame(root, bg="gray", width=200)
manager_frame.grid(row=0, column=1, sticky="nsew")

# --- Assets ---
assets_frame = tk.Frame(root, bg="gray", height=150)
assets_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
assets_frame.grid_propagate(False)

# --- Variables ---
offset_x = 0
offset_y = 0
drag_start = None
scene_objects = []
selected_object = None
selected_offset = (0, 0)

# --- Grid ---
def draw_grid(spacing=25):
    scene_canvas.delete("grid_line")
    w = scene_canvas.winfo_width()
    h = scene_canvas.winfo_height()
    for x in range(0, w, spacing):
        scene_canvas.create_line(x, 0, x, h, fill="gray40", tags="grid_line")
    for y in range(0, h, spacing):
        scene_canvas.create_line(0, y, w, y, fill="gray40", tags="grid_line")

scene_canvas.bind("<Configure>", lambda e: draw_grid())

# --- Camera pan & object selection ---
def on_drag_start(event):
    global drag_start, selected_object, selected_offset
    clicked = scene_canvas.find_closest(event.x, event.y)
    for obj in scene_objects:
        if obj["id"] == clicked[0]:
            selected_object = obj
            selected_offset = (event.x - (obj["x"] + offset_x),
                               event.y - (obj["y"] + offset_y))
            return
    selected_object = None
    drag_start = (event.x, event.y)

def on_drag_move(event):
    global offset_x, offset_y, drag_start
    if selected_object:
        new_x = event.x - selected_offset[0] - offset_x
        new_y = event.y - selected_offset[1] - offset_y
        selected_object["x"] = new_x
        selected_object["y"] = new_y
        update_scene_objects()
    elif drag_start:
        dx = event.x - drag_start[0]
        dy = event.y - drag_start[1]
        offset_x += dx
        offset_y += dy
        drag_start = (event.x, event.y)
        update_scene_objects()

def on_drag_end(event):
    global drag_start, selected_object
    drag_start = None

scene_canvas.bind("<ButtonPress-1>", on_drag_start)
scene_canvas.bind("<B1-Motion>", on_drag_move)
scene_canvas.bind("<ButtonRelease-1>", on_drag_end)

# --- Drag & Drop from Assets ---
drag_data = {"widget": None, "preview": None, "x": 0, "y": 0}

def start_drag_asset(event, asset_widget):
    drag_data["widget"] = asset_widget
    drag_data["x"] = event.x
    drag_data["y"] = event.y
    w, h = 50, 50
    x, y = scene_canvas.winfo_width()//2, scene_canvas.winfo_height()//2
    if hasattr(asset_widget, "image_obj"):
        drag_data["preview"] = scene_canvas.create_image(x, y, image=asset_widget.image_obj, anchor="nw")
        drag_data["preview_type"] = "image"
    else:
        drag_data["preview"] = scene_canvas.create_rectangle(
            x, y, x + w, y + h, fill=asset_widget["bg"], stipple="gray50"
        )
        drag_data["preview_type"] = "rect"

    asset_widget.bind("<B1-Motion>", drag_asset_motion)
    asset_widget.bind("<ButtonRelease-1>", drop_asset_on_scene)

def drag_asset_motion(event):
    widget = drag_data["widget"]
    if widget and drag_data["preview"]:
        x_root = widget.winfo_rootx() + event.x
        y_root = widget.winfo_rooty() + event.y
        scene_x = scene_canvas.winfo_rootx()
        scene_y = scene_canvas.winfo_rooty()
        canvas_x = x_root - scene_x - offset_x
        canvas_y = y_root - scene_y - offset_y
        if drag_data["preview_type"] == "rect":
            scene_canvas.coords(drag_data["preview"],
                                canvas_x,
                                canvas_y,
                                canvas_x + 50,
                                canvas_y + 50)
        elif drag_data["preview_type"] == "image":
            scene_canvas.coords(drag_data["preview"], canvas_x, canvas_y)

def drop_asset_on_scene(event):
    widget = drag_data["widget"]
    if widget and drag_data["preview"]:
        if drag_data["preview_type"] == "rect":
            x1, y1, x2, y2 = scene_canvas.coords(drag_data["preview"])
            scene_x = x1 - offset_x
            scene_y = y1 - offset_y
            obj = {
                "id": scene_canvas.create_rectangle(x1, y1, x2, y2, fill=widget["bg"]),
                "color": widget["bg"],
                "x": scene_x,
                "y": scene_y,
                "width": x2 - x1,
                "height": y2 - y1,
                "scripts": [],
                "type": "rect"
            }
        else:
            x, y = scene_canvas.coords(drag_data["preview"])
            scene_x = x - offset_x
            scene_y = y - offset_y
            obj = {
                "id": scene_canvas.create_image(x, y, image=widget.image_obj, anchor="nw"),
                "x": scene_x,
                "y": scene_y,
                "width": widget.image_width,
                "height": widget.image_height,
                "scripts": [],
                "type": "image",
                "image_path": widget.image_path
            }
        scene_objects.append(obj)

        scene_canvas.delete(drag_data["preview"])
        drag_data["preview"] = None
        widget.place_forget()
        widget.pack(side="left", padx=5, pady=5)
        widget.unbind("<B1-Motion>")
        widget.unbind("<ButtonRelease-1>")
        drag_data["widget"] = None

# --- Assets ---
def create_asset(color=None, image_path=None):
    if image_path:
        img = Image.open(image_path)
        img.thumbnail((50, 50))
        img_tk = ImageTk.PhotoImage(img)
        asset = tk.Label(assets_frame, image=img_tk, bd=2, relief="raised")
        asset.image_obj = img_tk
        asset.image_path = image_path
        asset.image_width, asset.image_height = img.size
    else:
        asset = tk.Canvas(assets_frame, width=50, height=50, bg=color, bd=2, relief="raised")
    asset.pack(side="left", padx=5, pady=5)
    asset.bind("<ButtonPress-1>", lambda e, a=asset: start_drag_asset(e, a))
    return asset

assets = []
assets.append(create_asset(color="red"))
assets.append(create_asset(color="blue"))
assets.append(create_asset(color="yellow"))

# --- Delete object ---
def delete_selected(event):
    global selected_object
    if selected_object:
        scene_canvas.delete(selected_object["id"])
        scene_objects.remove(selected_object)
        selected_object = None

root.bind("<Delete>", delete_selected)

# --- Update objects ---
def update_scene_objects():
    for obj in scene_objects:
        x1 = obj["x"] + offset_x
        y1 = obj["y"] + offset_y
        x2 = x1 + obj["width"]
        y2 = y1 + obj["height"]
        if obj["type"] == "rect":
            scene_canvas.coords(obj["id"], x1, y1, x2, y2)
        elif obj["type"] == "image":
            scene_canvas.coords(obj["id"], x1, y1)

# --- Assign scripts ---
def assign_script():
    global selected_object
    if selected_object:
        script_name = simpledialog.askstring("Assign Script", "Enter script filename (without .py):")
        if script_name:
            if "scripts" not in selected_object:
                selected_object["scripts"] = []
            if script_name not in selected_object["scripts"]:
                selected_object["scripts"].append(script_name)
            print(f"Assigned {script_name} to object")

assign_btn = tk.Button(manager_frame, text="Assign Script", command=assign_script)
assign_btn.pack(padx=5, pady=5, fill="x")

# --- Import Image Button ---
def import_image():
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if file_path:
        create_asset(image_path=file_path)

import_btn = tk.Button(manager_frame, text="Import Image", command=import_image)
import_btn.pack(padx=5, pady=5, fill="x")

# --- Export Scene ---
def export_scene():
    scene_data_export = []
    for obj in scene_objects:
        data = {
            "type": obj["type"],
            "x": obj["x"],
            "y": obj["y"],
            "width": obj["width"],
            "height": obj["height"],
            "scripts": obj.get("scripts", [])
        }
        if obj["type"] == "rect":
            color = obj["color"]
            if isinstance(color, str):
                rgb = root.winfo_rgb(color)
                color = tuple(c // 256 for c in rgb)
            data["color"] = list(color)
        elif obj["type"] == "image":
            data["image_path"] = obj["image_path"]
        scene_data_export.append(data)

    with open("scene_data.py", "w") as f:
        f.write("scene_data = " + repr(scene_data_export))
    print("Scene exported as scene_data.py")

export_btn = tk.Button(assets_frame, text="Export Scene", command=export_scene)
export_btn.pack(side="right", padx=5, pady=5, fill="y")

root.mainloop()
