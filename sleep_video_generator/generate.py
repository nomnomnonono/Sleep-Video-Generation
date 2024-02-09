import math
import os
import shutil
from io import BytesIO

import cv2
import numpy as np
import requests
from moviepy.editor import ImageClip
from omegaconf import OmegaConf
from openai import OpenAI
from PIL import Image
from pydub import AudioSegment

IMAGE_OUTPUT_PATH = "output/image.png"
THUMBNAIL_OUTPUT_PATH = "output/thumbnail.png"
AUDIO_OUTPUT_PATH = "output/audio.mp3"
VIDEO_OUTPUT_PATH = "output/video.mp4"

config = OmegaConf.load("config.yaml")
os.environ["OPENAI_API_KEY"] = config.api_key


def generate_image(prompt: str) -> np.ndarray:
    client = OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1,
    )

    response = requests.get(response.data[0].url)
    generated_image = np.array(Image.open(BytesIO(response.content)))
    generated_image = cv2.cvtColor(generated_image, cv2.COLOR_RGBA2BGRA)
    generated_image = cv2.resize(
        generated_image, (1280, 720), interpolation=cv2.INTER_AREA
    )

    cv2.imwrite(IMAGE_OUTPUT_PATH, generated_image)
    return cv2.cvtColor(generated_image, cv2.COLOR_BGRA2RGBA)


def generate_thumbnail(
    texts: str,
    fontstyle: str,
    fontsize: float,
    fontcolor: str,
    thickness: int,
    linetype: str,
) -> np.ndarray:
    image = cv2.imread(IMAGE_OUTPUT_PATH)

    # Convert hex color to BGR
    fontcolor = tuple(int(fontcolor.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    fontcolor = (fontcolor[2], fontcolor[1], fontcolor[0])

    if len(texts.split("\\n")) == 1:
        main_text, sub_text = texts, ""
    elif len(texts.split("\\n")) == 2:
        main_text, sub_text = texts.split("\\n")
    else:
        split_text = texts.split("\\n")
        main_text, sub_text = split_text[0], split_text[1]

    image = _write_text_on_image(
        image,
        main_text,
        sub_text,
        fontstyle,
        fontsize,
        fontcolor,
        thickness,
        linetype,
    )

    cv2.imwrite(THUMBNAIL_OUTPUT_PATH, image)
    return cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA), THUMBNAIL_OUTPUT_PATH


def _write_text_on_image(
    image: np.ndarray,
    main_text: str,
    sub_text: str,
    fontstyle: str,
    fontsize: float,
    fontcolor: str,
    thickness: int,
    linetype: str,
) -> np.ndarray:
    height, width, _ = image.shape

    # Calculate text cente position from fontsize, image width and height, text lenght
    main_textsize = cv2.getTextSize(
        main_text, eval("cv2." + fontstyle), fontsize, thickness
    )[0]
    main_text_x, main_text_y = (width - main_textsize[0]) // 2, (
        height + main_textsize[1]
    ) // 2

    image = cv2.putText(
        image,
        main_text,
        (main_text_x, main_text_y),
        eval("cv2." + fontstyle),
        fontsize,
        fontcolor,
        thickness,
        eval("cv2." + linetype),
    )

    if sub_text:
        fontsize /= 1.5
        thickness -= 1
        sub_textsize = cv2.getTextSize(
            sub_text, eval("cv2." + fontstyle), fontsize, thickness
        )[0]
        sub_text_x, sub_text_y = (
            width - sub_textsize[0]
        ) // 2, main_text_y + sub_textsize[1] + 50
        image = cv2.putText(
            image,
            sub_text,
            (sub_text_x, sub_text_y),
            eval("cv2." + fontstyle),
            fontsize,
            fontcolor,
            thickness,
            eval("cv2." + linetype),
        )

    return image


def generate_video(audio_path: str, duration: int) -> str:
    duration_seconds = _preprocess_audio(audio_path, duration)

    video = ImageClip(IMAGE_OUTPUT_PATH).set_duration(duration_seconds)
    video.write_videofile(VIDEO_OUTPUT_PATH, fps=1, audio=AUDIO_OUTPUT_PATH)
    return VIDEO_OUTPUT_PATH


def _preprocess_audio(audio_path: str, duration: int) -> int:
    audio = AudioSegment.from_file(audio_path, "mp3")

    # Repeat audio to match video duration
    audio *= math.ceil(duration / (audio.duration_seconds / 60))

    # Fade out audio
    audio = audio.fade_out(1000 * 10)

    audio.export(AUDIO_OUTPUT_PATH, format="mp3")

    return audio.duration_seconds


def archive_files(folder_name: str) -> None:
    folder_name = os.path.join("output", folder_name)
    os.makedirs(folder_name, exist_ok=True)
    for file in [
        IMAGE_OUTPUT_PATH,
        THUMBNAIL_OUTPUT_PATH,
        AUDIO_OUTPUT_PATH,
        VIDEO_OUTPUT_PATH,
    ]:
        shutil.move(file, folder_name)
