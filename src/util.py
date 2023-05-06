import albumentations as albu
import argparse
import cv2
import extcolors
import json
import numpy as np
import os
import pandas as pd
import psutil
import torch

from collections import namedtuple
from colormap import rgb2hex
from datetime import datetime
from functools import cache
from PIL import Image, ImageFilter
from scipy.spatial import KDTree
from torch.utils import model_zoo
from webcolors import hex_to_rgb

from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image, rename_layers
from iglovikov_helper_functions.utils.image_utils import pad, unpad
from segmentation_models_pytorch import Unet

from src.numpy_encoder import NumpyArrayEncoder
from src.color_chart import color_chart
from src.config import *
from src.colors import BASIC_COLORS

# Set Cache to data directory so docker can keep weights file after first run
os.environ['TORCH_HOME'] = './data/model'

@cache
def cached_model():
    model = create_model("Unet_2020-10-30")
    model.eval()
    return model

def create_model(model_name):
    model = namedtuple("model", ["url", "model"])
    models = {
        "Unet_2020-10-30": model(
            url="https://github.com/ternaus/cloths_segmentation/releases/download/0.0.1/weights.zip",
            model=Unet(encoder_name="timm-efficientnet-b3", classes=1, encoder_weights=None),
        )
    }

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    model = models[model_name].model
    state_dict = model_zoo.load_url(models[model_name].url, progress=True, map_location=device.type)["state_dict"]
    state_dict = rename_layers(state_dict, {"model.": ""})
    model.load_state_dict(state_dict)

    if device.type == "cuda":
        with torch.cuda.device(device):
            return model

    if device.type == "cpu":
        return model

def crop_image(clipped_image):
    image = Image.fromarray(clipped_image)
    return image.crop(image.getbbox())

def extract_color(config):
    if config["debug"] is True:
        start_time = datetime.now()

    # Make sure file exists before processing
    if not os.path.exists(config["filename"].resolve()):
        return print("❌ Unable to locate file: {}".format(config["filename"].resolve()))

    # Make directory if it does not exist
    os.makedirs(config["dest"].resolve(), exist_ok=True)

    # STEP 1: Load Original Image
    original_image = load_image(config["filename"].resolve())

    if config["images"] is True:
        image = Image.fromarray(original_image.astype(np.uint8))
        image.save(os.path.join(config["dest"].resolve(), "original-image.png"))
        image.close()
        del image

    # STEP 2: Generate Mask Image & JSON
    mask = get_mask(original_image)

    if config["images"] is True:
        image = Image.fromarray((mask * 255).astype(np.uint8))
        image.save(os.path.join(config["dest"].resolve(), "mask.png"))
        image.close()
        del image

    if config["json"] is True:
        with open(os.path.join(config["dest"].resolve(), "mask.json"), "w") as outfile:
            outfile.write(get_mask_json(mask))

    # STEP 3: Generate Detected Product Image
    if config["images"] is True:
        overlay = get_overlay(original_image, mask)
        image = Image.fromarray(overlay.astype(np.uint8))
        image.save(os.path.join(config["dest"].resolve(), "overlay.png"))
        image.close()
        del image

    # STEP 4: Remove Background from Image
    processed_image = remove_image_background(original_image, mask)
    if config["images"] is True:
        image = Image.fromarray(processed_image.astype(np.uint8))
        image.save(os.path.join(config["dest"].resolve(), "processed-image.png"))
        image.close()
        del image

    # STEP 5: Trim Image to Remove Transparent Pixels
    cropped_image = crop_image(processed_image)
    if config["images"] is True:
        image = cropped_image.copy()
        image.save(os.path.join(config["dest"].resolve(), "cropped-image.png"))
        image.close()
        del image

    # STEP 6: Process Colors from Clipped Image for JSON
    colors = get_product_colors(cropped_image)

    if config["json"] is True:
        with open(os.path.join(config["dest"].resolve(), "colors.json"), "w") as outfile:
            outfile.write(colors.to_json())

    # STEP 7: Generate Color Chart
    if config["images"] is True and config["color_chart"] is True:
        product_color_chart = generate_color_chart(colors, cropped_image)
        product_color_chart.save(os.path.join(config["dest"].resolve(), "product-color-chart.png"))
        product_color_chart.close()

    if config["debug"] is True:
        time_elapsed = datetime.now() - start_time
        print("✅ Generated Assets: {} => {} | Processing Time: {} (hh:mm:ss.ms)".format(os.path.relpath(config["filename"].resolve()), os.path.relpath(config["dest"].resolve()), time_elapsed))

def generate_color_chart(colors, cropped_image):
    return color_chart(colors, cropped_image)

def get_device_info():
    # Define if we are detected CUDA or if we should use CPU
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    if device.type == "cuda":
        return f"""
            **Device Info:**
            - CUDA Device: `{torch.cuda.get_device_name(0)}`
            - CPU Count: `{psutil.cpu_count()}`
            ---
            **Memory Usage:**
            - Allocated: `{round(torch.cuda.memory_allocated(0)/1024**3,1)} GB`
            - Cached: `{round(torch.cuda.memory_reserved(0)/1024**3,1)} GB`
        """

    # Additional Info when using CPU
    if device.type == "cpu":
        memory = psutil.virtual_memory()
        return f"""
            **Device Info:**
            - CUDA Device: `N/A`
            - CPU Count: `{psutil.cpu_count()}`
            ---
            **Memory Usage:**
            - Total: `{round(memory.total/1024**3,1)} GB`
            - Available: `{round(memory.available/1024**3,1)} GB`
            - Used: `{round(memory.used/1024**3,1)} GB`
            - Percent: `{round(memory.percent)}%`
        """

def get_color_json(colors):
    return json.dumps(colors)

def get_color_name(color):
    names = []
    rgb_values = []

    for color_hex, color_name in BASIC_COLORS.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(color)

    return names[index]

def get_mask_json(mask):
    return json.dumps(mask, cls=NumpyArrayEncoder)

def get_mask(original_image):
    model = cached_model()
    transform = albu.Compose(
        [albu.LongestMaxSize(max_size=MAX_IMAGE_SIZE), albu.Normalize(p=1)], p=1
    )

    # Detect Image Segments
    original_height, original_width = original_image.shape[:2]
    image = transform(image=original_image)["image"]
    padded_image, pads = pad(image, factor=MAX_IMAGE_SIZE, border=cv2.BORDER_CONSTANT)

    x = torch.unsqueeze(tensor_from_rgb_image(padded_image), 0)

    with torch.no_grad():
        prediction = model(x)[0][0]

    mask = (prediction > 0).cpu().numpy().astype(np.uint8)
    mask = unpad(mask, pads)
    mask = cv2.resize(
        mask, (original_width, original_height), interpolation=cv2.INTER_NEAREST
    )

    return mask

def get_overlay(original_image, mask):
    mask_channels = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    return cv2.addWeighted(
        original_image, 1, (mask_channels * (0, 255, 0)).astype(np.uint8), 0.5, 0
    )

def get_product_colors(clipped_image, tolerance = COLOR_TOLERANCE, limit = COLOR_LIMIT):
    colors = extcolors.extract_from_image(clipped_image, tolerance, (limit + 1))
    colors_pre_list = str(colors).replace('([(','').split(', (')[0:-1]
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_occurrences = [int(i.split('), ')[1].replace(')','')) for i in colors_pre_list]

    total = sum(df_occurrences)

    # Calculate Percentages
    df_percents = []
    for i in df_occurrences:
        df_percents += [i / total]

    # Get color names from kex
    color_names = []
    for i in df_rgb:
        color_rgb = int(i.split(", ")[0].replace("(","")), int(i.split(", ")[1]), int(i.split(", ")[2].replace(")",""))
        color_names += [get_color_name(color_rgb)]

    # Convert RGB to HEX code
    df_hex = [rgb2hex(int(i.split(", ")[0].replace("(","")), int(i.split(", ")[1]), int(i.split(", ")[2].replace(")",""))) for i in df_rgb]
    df = pd.DataFrame(zip(df_hex, color_names, df_occurrences, df_percents), columns = ["hex", "color", "occurrence", "percent"])

    return df[df.percent >= MIN_COLOR_PERCENT]

def load_image(img_file):
    img = Image.open(img_file).convert('RGB')
    size = img.size

    if size[0] > MAX_IMAGE_SIZE or size[1] > MAX_IMAGE_SIZE:
        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.ANTIALIAS)

    # Resize Image if Larger than
    return np.array(img)

def max_image_size(min_value, max_value):
    def check_valid(arg: str):
        try:
            val = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f'must be a valid `int`')
        if val < min_value or val > max_value:
            raise argparse.ArgumentTypeError(f'must be within [{min_value}, {max_value}]')
        if val%32:
            raise argparse.ArgumentTypeError(f'must be divisible by 32')
        return val

    return check_valid

def ranged_int(min_value, max_value):
    def check_valid(arg: str):
        try:
            val = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f'must be a valid `int`')
        if val < min_value or val > max_value:
            raise argparse.ArgumentTypeError(f'must be within [{min_value}, {max_value}]')
        return val

    return check_valid

def remove_image_background(original_image, mask):
    mask_channels = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    # Apply Mask to Images
    masked_image = original_image * mask_channels
    masked_image = Image.fromarray(masked_image.astype(np.uint8))
    temp_image = masked_image.filter(ImageFilter.ModeFilter(size=MASK_SMOOTH_SIZE))

    temp_channels = cv2.cvtColor(np.asarray(temp_image), cv2.COLOR_BGR2GRAY)

    # Applying thresholding technique
    _, alpha = cv2.threshold(temp_channels, 0, 255, cv2.THRESH_BINARY)

    # Using cv2.split() to split channels of coloured image
    b, g, r = cv2.split(np.asarray(masked_image))

    # Making list of Red, Green, Blue # Channels and alpha
    rgba = [b, g, r, alpha]

    # Using cv2.merge() to merge rgba into a coloured/multi-channeled image
    return cv2.merge(rgba, 4)
