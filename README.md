# TextOverlay Node for ComfyUI

The TextOverlay node allows users to overlay text on images. The node supports adjustments for font size, type, color, alignment, and position, making it versatile for various applications.

Originally inspired by the [Text Overlay Plugin by mikkel](https://github.com/mikkel/ComfyUI-text-overlay), this node has been rebuilt and expanded to include additional features and improvements.

## Features

- **Font Customization**: Choose from different font sizes and types to match your design.
- **Color Selection**: Specify text and stroke colors in hex format for perfect matching.
- **Alignment and Positioning**: Align your text horizontally and vertically, with options for precise position adjustments.
- **Stroke Customization**: Add a stroke to your text with customizable color and thickness.
- **Supports Single and Batch Processing**: Process single images or multiple images in a batch.

## Installation

To use the TextOverlay node, ensure this repo is included in your ComfyUI `custom_nodes` directory.

1. Find the `custom_nodes` directory in your ComfyUI installation.
2. Clone this repository into the `custom_nodes` directory using the following command:

```bash
git clone https://github.com/Munkyfoot/ComfyUI-TextOverlay
```

## Usage

After installation, the TextOverlay node will be available in the ComfyUI interface under the `image/text` category. To use the node:

1. Add the TextOverlay node to your workflow.
2. Connect an image source to the node's image input.
3. Configure the node parameters in the UI, including text content, font specifications, color, alignment, and positioning adjustments.
4. Connect the node's output to your desired destination in the workflow.

### Custom Fonts

To use a custom font, ensure the font file is included in the `fonts` directory within this directory. Then, specify the font file name (e.g., `arial.ttf`) in the `font` parameter of the TextOverlay node. If using a system-installed font, you can specify the font name directly without the file path. If the font file is not found, the node will default to a system-installed font.

## Input Parameters

The TextOverlay node requires the following inputs:

- `image`: The input image(s) to overlay text on.
- `text`: The text content to overlay.
- `font_size`: Size of the font.
- `font`: Name of the font file (e.g., `arial.ttf`).
- `fill_color_hex`: Hex code for the text color.
- `stroke_color_hex`: Hex code for the text stroke color.
- `stroke_thickness`: Thickness of the stroke.
- `padding`: Padding around the text.
- `horizontal_alignment`: Horizontal text alignment (`left`, `center`, `right`).
- `vertical_alignment`: Vertical text alignment (`top`, `middle`, `bottom`).
- `x_shift`, `y_shift`: Adjustments for text positioning.

## Output

The node overlays the specified text according to the configured parameters and output the modified input image(s).
