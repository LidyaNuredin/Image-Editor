import customtkinter as ctk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont

# Default values
ROTATE_DEFAULT = 0
ZOOM_DEFAULT = 0
FLIP_OPTIONS = ['None', 'X', 'Y', 'Both']
BLUR_DEFAULT = 0
CONTRAST_DEFAULT = 0
EFFECT_OPTIONS = ['None', 'Emboss', 'Find edges', 'Contour', 'Edge enhance']
BRIGHTNESS_DEFAULT = 1
VIBRANCE_DEFAULT = 1
GRAYSCALE_DEFAULT = False
INVERT_DEFAULT = False
TEXT_DEFAULT = ""
FONT_SIZE_DEFAULT = 20
TEXT_COLOR_DEFAULT = "(255, 255, 255)"  # RGB tuple as a string
TEXT_X_DEFAULT = 0
TEXT_Y_DEFAULT = 0
BRUSH_SIZE_DEFAULT = 5
BRUSH_COLOR_DEFAULT = "(255, 0, 0)"  # RGB tuple as a string

# Colors
BACKGROUND_COLOR = '#242424'
WHITE = '#FFF'
GREY = 'grey'
BLUE = '#1f6aa5'
DARK_GREY = '#4a4a4a'
CLOSE_RED = '#8a0606'
SLIDER_BG = '#64686b'
DROPDOWN_MAIN_COLOR = '#444'
DROPDOWN_Hover_COLOR = '#333'
DROPDOWN_MENU_COLOR = '#666'

# Expanded Basic Colors for the Color Picker (20 colors)
BASIC_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 255),# White
    (0, 0, 0),      # Black
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (128, 0, 0),    # Maroon
    (0, 128, 0),    # Dark Green
    (0, 0, 128),    # Navy
    (128, 128, 128),# Gray
    (255, 165, 0),  # Orange
    (75, 0, 130),   # Indigo
    (238, 130, 238),# Violet
    (173, 216, 230),# Light Blue
    (255, 192, 203),# Pink
    (139, 69, 19),  # Brown
    (240, 230, 140),# Khaki
    (64, 224, 208)  # Turquoise
]

# Updated Color Picker Dialog Class (Scrollable)
class ColorPickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_color_rgb, callback):
        super().__init__(master=parent)
        self.title("Select Color")
        self.geometry("400x300")  # Fixed height, scrollable content
        self.resizable(False, False)
        self.callback = callback  # Function to call with the selected color

        # Ensure the dialog stays on top and grabs focus
        self.attributes('-topmost', True)
        self.grab_set()  # Make the dialog modal

        # Colors Section
        ctk.CTkLabel(self, text="Pick a Color:").pack(anchor="w", padx=10, pady=5)
        
        # Scrollable frame for colors
        self.color_frame = ctk.CTkScrollableFrame(self, width=360, height=220)  # Adjusted width and height
        self.color_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Arrange 20 colors in a 5-column grid, rows will extend as needed
        for i, color in enumerate(BASIC_COLORS):
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            btn = ctk.CTkButton(
                self.color_frame, text="", width=40, height=40, fg_color=hex_color,
                command=lambda r=r, g=g, b=b: self.select_color(r, g, b)
            )
            btn.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def select_color(self, r, g, b):
        self.callback(r, g, b)  # Immediately apply the color and close
        self.destroy()

# Image Widgets
class ImageImport(ctk.CTkFrame):
    def __init__(self, parent, import_func):
        super().__init__(master=parent)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.import_func = import_func
        ctk.CTkButton(self, text='Open Image',
                      command=self.open_dialog).pack(expand=True)

    def open_dialog(self):
        path = filedialog.askopenfile()
        if path:  # Check if a file was selected
            self.import_func(path.name)

class ImageOutput(Canvas):
    def __init__(self, parent, resize_image, paint_func):
        super().__init__(master=parent, background=BACKGROUND_COLOR,
                         bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.bind('<Configure>', resize_image)
        self.bind('<B1-Motion>', paint_func)
        self.bind('<ButtonRelease-1>', lambda event: self.clear_last_pos())
        self.last_x = None
        self.last_y = None

    def clear_last_pos(self):
        self.last_x = None
        self.last_y = None

class CloseOutput(ctk.CTkButton):
    def __init__(self, parent, close_func):
        super().__init__(master=parent, command=close_func, text='X', text_color=WHITE, fg_color='transparent',
                         width=40, height=40, corner_radius=0, hover_color=CLOSE_RED)
        self.place(relx=0.99, rely=0.01, anchor='ne')

# Panels
class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=DARK_GREY)
        self.pack(fill='x', pady='4', ipady='8')

class SliderPanel(Panel):
    def __init__(self, parent, text, data_var, min_value, max_value):
        super().__init__(parent=parent)
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)
        self.data_var = data_var
        self.data_var.trace_add('write', self.update_text)
        ctk.CTkLabel(self, text=text).grid(column=0, row=0, sticky='W', padx=5)
        self.num_label = ctk.CTkLabel(self, text=data_var.get())
        self.num_label.grid(column=1, row=0, sticky='E', padx=5)
        ctk.CTkSlider(self, fg_color=SLIDER_BG, variable=self.data_var, from_=min_value, to=max_value).grid(
            row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

    def update_text(self, *args):
        self.num_label.configure(text=f'{round(self.data_var.get(), 2)}')

class SegmentedPanel(Panel):
    def __init__(self, parent, text, data_var, options):
        super().__init__(parent=parent)
        ctk.CTkLabel(self, text=text).pack()
        ctk.CTkSegmentedButton(self, variable=data_var, values=options).pack(
            expand=True, fill='both', padx=4, pady=4)

class SwitchPanel(Panel):
    def __init__(self, parent, *args):
        super().__init__(parent=parent)
        for var, text in args:
            switch = ctk.CTkSwitch(
                self, text=text, variable=var, button_color=BLUE, fg_color=SLIDER_BG)
            switch.pack(side='left', expand=True, fill='both', padx=5, pady=5)

class FileNamePanel(Panel):
    def __init__(self, parent, name_string, file_string):
        super().__init__(parent=parent)
        self.name_string = name_string
        self.name_string.trace_add('write', self.update_text)
        self.file_string = file_string
        ctk.CTkEntry(self, textvariable=self.name_string).pack(
            fill='x', padx=20, pady=5)
        frame = ctk.CTkFrame(self, fg_color='transparent')
        jpg_check = ctk.CTkCheckBox(frame, text='jpg', variable=self.file_string,
                                    command=lambda: self.click('jpg'), onvalue='jpg', offvalue='png')
        png_check = ctk.CTkCheckBox(frame, text='png', variable=self.file_string,
                                    command=lambda: self.click('png'), onvalue='png', offvalue='jpg')
        jpg_check.pack(side='left', fill='x', expand=True)
        png_check.pack(side='left', fill='x', expand=True)
        frame.pack(expand=True, fill='x', padx=20)
        self.output = ctk.CTkLabel(self, text='')
        self.output.pack()

    def click(self, value):
        self.file_string.set(value)
        self.update_text()

    def update_text(self, *args):
        if self.name_string.get():
            text = self.name_string.get().replace(' ', '_') + '.' + self.file_string.get()
            self.output.configure(text=text)

class FilePathPanel(Panel):
    def __init__(self, parent, path_string):
        super().__init__(parent=parent)
        self.path_string = path_string
        ctk.CTkButton(self, text='Open Explorer',
                      command=self.open_file_dialog).pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.path_string).pack(expand=True, fill='both', padx=5, pady=5)
        
    def open_file_dialog(self):
        self.path_string.set(filedialog.askdirectory())

class DropDownPanel(ctk.CTkOptionMenu):
    def __init__(self, parent, data_var, options):
        super().__init__(master=parent, values=options, fg_color=DARK_GREY, button_color=DROPDOWN_MAIN_COLOR,
                         button_hover_color=DROPDOWN_Hover_COLOR, dropdown_fg_color=DROPDOWN_MENU_COLOR, variable=data_var)
        self.pack(fill='x', pady=4)

class TextPanel(Panel):
    def __init__(self, parent, text_var, size_var, color_var, x_var, y_var, app):
        super().__init__(parent=parent)
        self.app = app  # Reference to the main App instance
        ctk.CTkLabel(self, text="Text").pack(pady=2)
        ctk.CTkEntry(self, textvariable=text_var).pack(fill='x', padx=5, pady=2)
        SliderPanel(self, "Font Size", size_var, 10, 1000)
        SliderPanel(self, "X Position", x_var, -1500, 1500)
        SliderPanel(self, "Y Position", y_var, -1500, 1500)
        frame = ctk.CTkFrame(self, fg_color='transparent')
        ctk.CTkLabel(frame, text="Color").pack(side='left', padx=5)
        # Initialize the preview with the current color
        if color_var.get().startswith("("):
            r, g, b = map(int, color_var.get().strip("()").split(","))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            hex_color = color_var.get()
        self.color_preview = ctk.CTkFrame(frame, width=30, height=30, fg_color=hex_color)
        self.color_preview.pack(side='left', padx=5)
        ctk.CTkButton(frame, text="Select Color", command=lambda: self.open_color_picker(color_var)).pack(side='left', padx=5)
        frame.pack(fill='x', pady=2)

    def open_color_picker(self, color_var):
        def callback(r, g, b):
            # Update the color variable and preview immediately
            color_var.set(f"({r}, {g}, {b})")
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_preview.configure(fg_color=hex_color)
            # Trigger image update
            self.app.manipulate_image()

        ColorPickerDialog(self.app, color_var.get(), callback)

class PaintPanel(Panel):
    def __init__(self, parent, size_var, color_var, app):
        super().__init__(parent=parent)
        self.app = app  # Reference to the main App instance
        ctk.CTkLabel(self, text="Paint").pack(pady=2)
        SliderPanel(self, "Brush Size", size_var, 1, 50)
        frame = ctk.CTkFrame(self, fg_color='transparent')
        ctk.CTkLabel(frame, text="Brush Color").pack(side='left', padx=5)
        # Initialize the preview with the current color
        if color_var.get().startswith("("):
            r, g, b = map(int, color_var.get().strip("()").split(","))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            hex_color = color_var.get()
        self.color_preview = ctk.CTkFrame(frame, width=30, height=30, fg_color=hex_color)
        self.color_preview.pack(side='left', padx=5)
        ctk.CTkButton(frame, text="Select Color", command=lambda: self.open_color_picker(color_var)).pack(side='left', padx=5)
        frame.pack(fill='x', pady=2)

    def open_color_picker(self, color_var):
        def callback(r, g, b):
            # Update the color variable and preview immediately
            color_var.set(f"({r}, {g}, {b})")
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_preview.configure(fg_color=hex_color)
            # Trigger image update
            self.app.manipulate_image()

        ColorPickerDialog(self.app, color_var.get(), callback)

class RevertButton(ctk.CTkButton):
    def __init__(self, parent, *args):
        super().__init__(master=parent, text='Revert', command=self.revert)
        self.pack(side='bottom', pady=10)
        self.args = args
    
    def revert(self):
        for var, value in self.args:
            var.set(value)

class SaveButton(ctk.CTkButton):
    def __init__(self, parent, export_image, name_string, file_string, path_string):
        super().__init__(master=parent, text='save', command=self.save)
        self.pack(side='bottom', pady=10)
        self.export_image = export_image
        self.name_string = name_string
        self.file_string = file_string
        self.path_string = path_string
        
    def save(self):
        self.export_image(
            self.name_string.get(),
            self.file_string.get(),
            self.path_string.get()
        )

# Menu
class Menu(ctk.CTkTabview):
    def __init__(self, parent, pos_vars, color_vars, effect_vars, export_image):
        super().__init__(master=parent)
        self.grid(row=0, column=0, sticky='nsew', pady=10, padx=10)
        self.add('Position')
        self.add('Color')
        self.add('Effects')
        self.add('Export')
        PositionFrame(self.tab('Position'), pos_vars)
        ColorFrame(self.tab('Color'), color_vars)
        EffectFrame(self.tab('Effects'), effect_vars, parent)
        ExportFrame(self.tab('Export'), export_image)

class PositionFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both', padx=5, pady=5)
        SliderPanel(self, 'Rotation', pos_vars['rotate'], 0, 360)
        SliderPanel(self, 'Zoom', pos_vars['zoom'], 0, 1000)
        SegmentedPanel(self, 'Invert', pos_vars['flip'], FLIP_OPTIONS)
        RevertButton(self,
                     (pos_vars['rotate'], ROTATE_DEFAULT),
                     (pos_vars['zoom'], ZOOM_DEFAULT),
                     (pos_vars['flip'], FLIP_OPTIONS[0]))

class ColorFrame(ctk.CTkFrame):
    def __init__(self, parent, color_vars):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        SwitchPanel(self, (color_vars['grayscale'], 'B/W'), (color_vars['invert'], 'Invert'))
        SliderPanel(self, 'Brightness', color_vars['brightness'], 0, 5)
        SliderPanel(self, 'Vibrance', color_vars['vibrance'], 0, 5)
        RevertButton(self,
                     (color_vars['brightness'], BRIGHTNESS_DEFAULT),
                     (color_vars['grayscale'], GRAYSCALE_DEFAULT),
                     (color_vars['invert'], INVERT_DEFAULT),
                     (color_vars['vibrance'], VIBRANCE_DEFAULT))

class EffectFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, effect_vars, app):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        DropDownPanel(self, effect_vars['effect'], EFFECT_OPTIONS)
        SliderPanel(self, 'Blur', effect_vars['blur'], 0, 30)
        SliderPanel(self, 'Contrast', effect_vars['contrast'], 0, 10)
        TextPanel(self, 
                 effect_vars['text'],
                 effect_vars['font_size'],
                 effect_vars['text_color'],
                 effect_vars['text_x'],
                 effect_vars['text_y'],
                 app)
        PaintPanel(self,
                  effect_vars['brush_size'],
                  effect_vars['brush_color'],
                  app)
        RevertButton(self,
                    (effect_vars['blur'], BLUR_DEFAULT),
                    (effect_vars['contrast'], CONTRAST_DEFAULT),
                    (effect_vars['effect'], EFFECT_OPTIONS[0]),
                    (effect_vars['text'], TEXT_DEFAULT),
                    (effect_vars['font_size'], FONT_SIZE_DEFAULT),
                    (effect_vars['text_color'], TEXT_COLOR_DEFAULT),
                    (effect_vars['text_x'], TEXT_X_DEFAULT),
                    (effect_vars['text_y'], TEXT_Y_DEFAULT),
                    (effect_vars['brush_size'], BRUSH_SIZE_DEFAULT),
                    (effect_vars['brush_color'], BRUSH_COLOR_DEFAULT))

class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, export_image):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.name_string = ctk.StringVar()
        self.file_string = ctk.StringVar(value='jpg')
        self.path_string = ctk.StringVar()
        FileNamePanel(self, self.name_string, self.file_string)
        FilePathPanel(self, self.path_string)
        SaveButton(self, export_image, self.name_string, self.file_string, self.path_string)

# Main App
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.geometry('1000x600')
        self.title('Image-Editor')
        self.minsize(800, 500)
        self.init_parameters()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
        self.image_import = ImageImport(self, self.import_image)
        self.mainloop()

    def init_parameters(self):
        self.pos_vars = {
            'rotate': ctk.DoubleVar(value=ROTATE_DEFAULT),
            'zoom': ctk.DoubleVar(value=ZOOM_DEFAULT),
            'flip': ctk.StringVar(value=FLIP_OPTIONS[0])
        }
        self.color_vars = {
            'brightness': ctk.DoubleVar(value=BRIGHTNESS_DEFAULT),
            'grayscale': ctk.BooleanVar(value=GRAYSCALE_DEFAULT),
            'invert': ctk.BooleanVar(value=INVERT_DEFAULT),
            'vibrance': ctk.DoubleVar(value=VIBRANCE_DEFAULT)
        }
        self.effect_vars = {
            'blur': ctk.DoubleVar(value=BLUR_DEFAULT),
            'contrast': ctk.IntVar(value=CONTRAST_DEFAULT),
            'effect': ctk.StringVar(value=EFFECT_OPTIONS[0]),
            'text': ctk.StringVar(value=TEXT_DEFAULT),
            'font_size': ctk.IntVar(value=FONT_SIZE_DEFAULT),
            'text_color': ctk.StringVar(value=TEXT_COLOR_DEFAULT),
            'text_x': ctk.IntVar(value=TEXT_X_DEFAULT),
            'text_y': ctk.IntVar(value=TEXT_Y_DEFAULT),
            'brush_size': ctk.IntVar(value=BRUSH_SIZE_DEFAULT),
            'brush_color': ctk.StringVar(value=BRUSH_COLOR_DEFAULT)
        }
        combined_var = list(self.pos_vars.values()) + list(self.color_vars.values()) + list(self.effect_vars.values())
        for var in combined_var:
            var.trace_add('write', self.manipulate_image)

    def manipulate_image(self, *args):
        self.image = self.original.copy()  # Use copy to preserve original
        if self.pos_vars['rotate'].get() != ROTATE_DEFAULT:
            self.image = self.image.rotate(self.pos_vars['rotate'].get())
        if self.pos_vars['zoom'].get() != ZOOM_DEFAULT:
            self.image = ImageOps.crop(
                image=self.image, border=self.pos_vars['zoom'].get())
        if self.pos_vars['flip'].get() != FLIP_OPTIONS[0]:
            if self.pos_vars['flip'].get() == 'X':
                self.image = ImageOps.mirror(self.image)
            if self.pos_vars['flip'].get() == 'Y':
                self.image = ImageOps.flip(self.image)
            if self.pos_vars['flip'].get() == 'Both':
                self.image = ImageOps.mirror(self.image)
                self.image = ImageOps.flip(self.image)
        if self.color_vars['brightness'].get() != BRIGHTNESS_DEFAULT:
            brightness_enhancer = ImageEnhance.Brightness(self.image)
            self.image = brightness_enhancer.enhance(
                self.color_vars['brightness'].get())
        if self.color_vars['vibrance'].get() != VIBRANCE_DEFAULT:
            vibrance_enhancer = ImageEnhance.Color(self.image)
            self.image = vibrance_enhancer.enhance(
                self.color_vars['vibrance'].get())
        if self.color_vars['grayscale'].get():
            self.image = ImageOps.grayscale(self.image)
        if self.color_vars['invert'].get():
            if self.color_vars['grayscale'].get():
                self.image = ImageOps.invert(self.image)
            else:
                self.image = ImageOps.invert(self.image.convert('RGB'))
        if self.effect_vars['blur'].get() != BLUR_DEFAULT:
            self.image = self.image.filter(
                ImageFilter.GaussianBlur(self.effect_vars['blur'].get()))
        if self.effect_vars['contrast'].get() != CONTRAST_DEFAULT:
            self.image = self.image.filter(
                ImageFilter.UnsharpMask(self.effect_vars['contrast'].get()))
        match self.effect_vars['effect'].get():
            case 'Emboss': self.image = self.image.filter(ImageFilter.EMBOSS)
            case 'Find edges': self.image = self.image.filter(ImageFilter.FIND_EDGES)
            case 'Contour': self.image = self.image.filter(ImageFilter.CONTOUR)
            case 'Edge enhance': self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Add text if present
        if self.effect_vars['text'].get():
            self.image = self.image.convert('RGBA')
            draw = ImageDraw.Draw(self.image)
            try:
                font = ImageFont.truetype("arial.ttf", self.effect_vars['font_size'].get())
            except:
                font = ImageFont.load_default()
            
            text = self.effect_vars['text'].get()
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.image.width - text_width) / 2 + self.effect_vars['text_x'].get()
            y = (self.image.height - text_height) / 2 + self.effect_vars['text_y'].get()
            
            text_color_str = self.effect_vars['text_color'].get()
            if text_color_str.startswith("("):
                r, g, b = map(int, text_color_str.strip("()").split(","))
                text_color = (r, g, b)
            else:
                text_color = text_color_str
            
            draw.text((x, y), text, font=font, fill=text_color)

        self.place_image()

    def import_image(self, path):
        self.original = Image.open(path)
        self.image = self.original.copy()
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_import.grid_forget()
        self.image_output = ImageOutput(self, self.resize_image, self.paint)
        self.close_button = CloseOutput(self, self.close_edit)
        self.menu = Menu(self, self.pos_vars,
                         self.color_vars, self.effect_vars, self.export_image)

    def close_edit(self):
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.menu.grid_forget()
        self.image_import = ImageImport(self, self.import_image)

    def resize_image(self, event):
        canvas_ratio = event.width / event.height
        self.canvas_width = event.width
        self.canvas_height = event.height
        if canvas_ratio > self.image_ratio:
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else:
            self.image_width = int(event.width)
            self.image_height = int(self.image_width / self.image_ratio)
        self.place_image()

    def place_image(self):
        self.image_output.delete('all')
        resized_image = self.image.resize(
            (self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(
            self.canvas_width / 2, self.canvas_height / 2, image=self.image_tk)

    def paint(self, event):
        canvas_x = event.x
        canvas_y = event.y
        scale_x = self.image.width / self.image_width
        scale_y = self.image.height / self.image_height
        img_x = int((canvas_x - (self.canvas_width - self.image_width) / 2) * scale_x)
        img_y = int((canvas_y - (self.canvas_height - self.image_height) / 2) * scale_y)
        
        if (0 <= img_x < self.image.width and 0 <= img_y < self.image.height):
            self.image = self.image.convert('RGBA')
            draw = ImageDraw.Draw(self.image)
            color_str = self.effect_vars['brush_color'].get()
            if color_str.startswith("("):
                r, g, b = map(int, color_str.strip("()").split(","))
                brush_color = (r, g, b)
            else:
                brush_color = color_str
            
            if self.image_output.last_x is not None and self.image_output.last_y is not None:
                draw.line(
                    [(self.image_output.last_x, self.image_output.last_y), (img_x, img_y)],
                    fill=brush_color,
                    width=self.effect_vars['brush_size'].get()
                )
            
            self.image_output.last_x = img_x
            self.image_output.last_y = img_y
            self.place_image()

    def export_image(self, name, file, path):
        export_string = f'{path}/{name}.{file}'
        self.image.save(export_string)

if __name__ == "__main__":
    App()