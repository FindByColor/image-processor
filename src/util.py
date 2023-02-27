import albumentations as albu
import cv2
import extcolors
import json
import numpy as np
import pandas as pd
import psutil
import torch

from collections import namedtuple
from colormap import rgb2hex
from json import JSONEncoder
from PIL import Image, ImageFilter
from torch.utils import model_zoo

from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image, rename_layers
from iglovikov_helper_functions.utils.image_utils import pad, unpad
from segmentation_models_pytorch import Unet

from src.numpy_encoder import NumpyArrayEncoder
from src.color_chart import *
from src.config import *

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

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = models[model_name].model
    state_dict = model_zoo.load_url(models[model_name].url, progress=True, map_location=device.type)["state_dict"]
    state_dict = rename_layers(state_dict, {"model.": ""})
    model.load_state_dict(state_dict)
    return model

def crop_image(clipped_image):
    image = Image.fromarray(clipped_image)
    return image.crop(image.getbbox())

def generate_color_chart(colors, cropped_image):
    return color_chart(colors, cropped_image)

def get_device_info():
    # Define if we are detected CUDA or if we should use CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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
    
    # Convert RGB to HEX code
    df_hex = [rgb2hex(int(i.split(", ")[0].replace("(","")), int(i.split(", ")[1]), int(i.split(", ")[2].replace(")",""))) for i in df_rgb]
    df = pd.DataFrame(zip(df_hex, df_occurrences, df_percents), columns = ["hex", "occurrence", "percent"])

    return df[df.percent >= MIN_COLOR_PERCENT]

def load_image(img_file):
    img = Image.open(img_file).convert('RGB')
    size = img.size

    if size[0] > MAX_IMAGE_SIZE or size[1] > MAX_IMAGE_SIZE:
        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.ANTIALIAS)

    # Resize Image if Larger than
    return np.array(img)

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
