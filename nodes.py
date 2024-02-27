import os

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


class TextOverlay:
    """
    A node to overlay text on images with various customization options such as
    font size, font type, text color, stroke color, stroke thickness, padding,
    alignment, and position adjustments.
    """

    _horizontal_alignments = ["left", "center", "right"]
    _vertical_alignments = ["top", "middle", "bottom"]

    def __init__(self, device="cpu"):
        """
        Initializes the TextOverlay node.

        Parameters:
        - device (str): The computing device to use, default is 'cpu'.
        """

        self.device = device
        self._loaded_font = None
        self._full_text = None
        self._x = None
        self._y = None

    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the expected input parameters for the text overlay functionality.

        Returns:
        - dict: A dictionary specifying required inputs and their attributes.
        """

        return {
            "required": {
                "image": ("IMAGE",),  # Input image to overlay text on
                "text": (
                    "STRING",
                    {"multiline": True, "default": "Hello"},
                ),  # Text to overlay
                "font_size": (
                    "INT",
                    {"default": 32, "min": 1, "max": 256, "step": 1},
                ),  # Font size
                "font": (
                    "STRING",
                    {"default": "arial.ttf"},
                ),  # Font name (e.g. arial.ttf)
                "fill_color_hex": (
                    "STRING",
                    {"default": "#FFFFFF"},
                ),  # Text fill color in hex
                "stroke_color_hex": (
                    "STRING",
                    {"default": "#000000"},
                ),  # Text stroke color in hex
                "stroke_thickness": (
                    "FLOAT",
                    {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01},
                ),  # Stroke thickness
                "padding": (
                    "INT",
                    {"default": 16, "min": 0, "max": 128, "step": 1},
                ),  # Padding around text
                "horizontal_alignment": (
                    cls._horizontal_alignments,
                    {"default": "center"},
                ),  # Horizontal alignment
                "vertical_alignment": (
                    cls._vertical_alignments,
                    {"default": "bottom"},
                ),  # Vertical alignment
                "x_shift": (
                    "INT",
                    {"default": 0, "min": -128, "max": 128, "step": 1},
                ),  # Horizontal position adjustment
                "y_shift": (
                    "INT",
                    {"default": 0, "min": -128, "max": 128, "step": 1},
                ),  # Vertical position adjustment
            }
        }

    # Static attributes defining the return type, function name, and category for the class
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "batch_process"
    CATEGORY = "image/text"

    def hex_to_rgb(self, hex_color):
        """
        Converts a hex color string to an RGB tuple.

        Parameters:
        - hex_color (str): The color in hex format as a string.

        Returns:
        - tuple: The color converted to an (R, G, B) tuple.
        """

        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = hex_color * 2
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def draw_text(
        self,
        image,
        text,
        font_size,
        font,
        fill_color_hex,
        stroke_color_hex,
        stroke_thickness,
        padding,
        horizontal_alignment,
        vertical_alignment,
        x_shift,
        y_shift,
        use_cache=False,
    ):
        """
        Draws the specified text on the given image with the provided styling and alignment options.

        Parameters:
        - image (PIL.Image.Image): The image to draw text on.
        - text (str): The text to overlay on the image.
        - font_size (int): The font size of the text.
        - font (str): The font type of the text.
        - fill_color_hex (str): The fill color of the text in hex format.
        - stroke_color_hex (str): The stroke color of the text in hex format.
        - stroke_thickness (float): The thickness of the text stroke.
        - padding (int): The padding around the text.
        - horizontal_alignment (str): The horizontal alignment of the text ('left', 'center', 'right').
        - vertical_alignment (str): The vertical alignment of the text ('top', 'middle', 'bottom').
        - x_shift (int): Horizontal position adjustment for the text.
        - y_shift (int): Vertical position adjustment for the text.
        - use_cache (bool): Flag to use cached font and position calculations to improve performance.

        Returns:
        - PIL.Image.Image: The image with the text overlay applied.
        """

        # Load font from the fonts directory or use default if not found or specified to not use cache
        if self._loaded_font is None or use_cache is False:
            fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
            font_path = os.path.join(fonts_dir, font)

            # Check if the font file exists in the fonts directory
            if not os.path.exists(font_path):
                # If not, set path to font name directly - this will cause PIL to search for the font in the system
                font_path = font

            try:
                self._loaded_font = ImageFont.truetype(font_path, font_size)
            except Exception as e:
                print(f"Error loading font: {e}... Using default font")
                self._loaded_font = ImageFont.load_default()

        # Prepare to draw on the image
        draw = ImageDraw.Draw(image)

        # Process text for multiline support and fit within image dimensions
        words = text.replace("\n", "\n ").split(" ")
        if self._full_text is None or use_cache is False:
            text_lines, line = [], ""
            for word in words:
                extra_line = "\n" in word
                word = word.strip()
                if (
                    draw.textlength(line + word, font=self._loaded_font)
                    < image.width - 2 * padding
                ):
                    line += word + " "
                else:
                    text_lines.append(line.strip())
                    line = word + " "
                if extra_line:
                    text_lines.append(line.strip())
                    line = ""
            text_lines.append(line.strip())
            self._full_text = "\n".join(text_lines)

        # Calculate text position based on alignment and position adjustments
        if self._x is None or self._y is None or use_cache is False:
            left, top, right, bottom = draw.multiline_textbbox(
                (0, 0),
                self._full_text,
                font=self._loaded_font,
                stroke_width=int(font_size * stroke_thickness * 0.5),
                align=horizontal_alignment,
            )
            if horizontal_alignment == "left":
                self._x = padding
            elif horizontal_alignment == "center":
                self._x = (image.width - (right - left)) / 2
            elif horizontal_alignment == "right":
                self._x = image.width - (right - left) - padding
            self._x += x_shift
            if vertical_alignment == "middle":
                self._y = (image.height - (bottom - top)) / 2
            elif vertical_alignment == "top":
                self._y = padding
            elif vertical_alignment == "bottom":
                self._y = image.height - (bottom - top) - padding
            self._y += y_shift

        # Draw the processed text onto the image
        draw.text(
            (self._x, self._y),
            self._full_text,
            fill=self.hex_to_rgb(fill_color_hex),
            stroke_fill=self.hex_to_rgb(stroke_color_hex),
            stroke_width=int(font_size * stroke_thickness * 0.5),
            font=self._loaded_font,
            align=horizontal_alignment,
        )
        return image

    def batch_process(
        self,
        image,
        text,
        font_size,
        font,
        fill_color_hex,
        stroke_color_hex,
        stroke_thickness,
        padding,
        horizontal_alignment,
        vertical_alignment,
        x_shift,
        y_shift,
    ):
        """
        Processes a batch of images or a single image, adding the specified text overlay
        with the given styling and alignment options.

        Parameters:
        - image (torch.Tensor or numpy.ndarray): The image(s) to process.
        - text (str): The text to overlay on the image(s).
        - font_size (int): The font size of the text.
        - font (str): The font type of the text.
        - fill_color_hex (str): The fill color of the text in hex format.
        - stroke_color_hex (str): The stroke color of the text in hex format.
        - stroke_thickness (float): The thickness of the text stroke.
        - padding (int): The padding around the text.
        - horizontal_alignment (str): The horizontal alignment of the text.
        - vertical_alignment (str): The vertical alignment of the text.
        - x_shift (int): Horizontal position adjustment for the text.
        - y_shift (int): Vertical position adjustment for the text.

        Returns:
        - tuple: A tuple containing the processed image(s) as a torch.Tensor.
        """

        # Handles both single and batch image processing for text overlay
        if len(image.shape) == 3:  # Single image
            image_np = image.cpu().numpy()
            image = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))
            image = self.draw_text(
                image,
                text,
                font_size,
                font,
                fill_color_hex,
                stroke_color_hex,
                stroke_thickness,
                padding,
                horizontal_alignment,
                vertical_alignment,
                x_shift,
                y_shift,
            )
            image_tensor_out = torch.tensor(np.array(image).astype(np.float32) / 255.0)
            image_tensor_out = torch.unsqueeze(image_tensor_out, 0)
            return (image_tensor_out,)
        else:  # Batch of images
            image_np = image.cpu().numpy()
            images = [Image.fromarray((img * 255).astype(np.uint8)) for img in image_np]
            images_out, use_cache = [], False
            for img in images:
                img = self.draw_text(
                    img,
                    text,
                    font_size,
                    font,
                    fill_color_hex,
                    stroke_color_hex,
                    stroke_thickness,
                    padding,
                    horizontal_alignment,
                    vertical_alignment,
                    x_shift,
                    y_shift,
                    use_cache,
                )
                images_out.append(np.array(img).astype(np.float32) / 255.0)
                use_cache = True
            images_np = np.stack(images_out)
            images_tensor = torch.from_numpy(images_np)
            return (images_tensor,)


# Mapping of node class names to their respective classes
NODE_CLASS_MAPPINGS = {
    "Text Overlay": TextOverlay,
}
