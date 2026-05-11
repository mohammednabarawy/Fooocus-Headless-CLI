# -*- coding: utf-8 -*-
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath('d:/Fooocus_win64_2-5-0'))
import arabic_poster_pipeline
from argparse import Namespace

def copy_to_artifacts(source, name):
    dest = f"C:/Users/moham/.gemini/antigravity/brain/38fe042e-1503-4a04-8c58-bce4907c2b0b/{name}"
    shutil.copy2(source, dest)
    print(f"Copied {source} to {dest}")

def run_test_1():
    print("--- Running Test 1: Neon Sign ---")
    args = Namespace(
        arabic_text='مستقبل الذكاء الاصطناعي',
        scene_prompt='cyberpunk city street at night, neon lights, glowing signs, rainy, highly detailed',
        output='outputs/test1_neon.png',
        width=1152,
        height=896,
        font_style='default',
        font=None,
        text_effect='glow',
        text_position='top',
        font_size=None,
        opacity=0.9,
        darken=0.2,
        padding=80,
        text_color='0,255,255', # Cyan text
        negative_prompt='ugly, blurry, low res',
        seed=101,
        performance='Speed',
        styles=['Fooocus V2', 'SAI Neonpunk'],
        base_model=None,
        cfg_scale=7.0,
        image_number=1,
        lora=None,
        harmonize=0.45 # High harmonize to blend into neon environment
    )
    result = arabic_poster_pipeline.run_full_pipeline(args)
    if result:
        copy_to_artifacts(result[0], "test1_neon.png")

def run_test_2():
    print("--- Running Test 2: Historical/Calligraphy ---")
    args = Namespace(
        arabic_text='تاريخ الأندلس\nالمجد المفقود',
        scene_prompt='ancient library interior, dusty sunbeams, old books, warm sunlight, historical, masterpiece',
        output='outputs/test2_history.png',
        width=896,
        height=1152,
        font_style='naskh',
        font=None,
        text_effect='shadow',
        text_position='center',
        font_size=None,
        opacity=0.85,
        darken=0.4,
        padding=60,
        text_color='240,230,200', # Warm paper color
        negative_prompt='',
        seed=202,
        performance='Speed',
        styles=['Fooocus V2', 'Fooocus Enhance'],
        base_model=None,
        cfg_scale=7.0,
        image_number=1,
        lora=None,
        harmonize=0.35
    )
    result = arabic_poster_pipeline.run_full_pipeline(args)
    if result:
        copy_to_artifacts(result[0], "test2_history.png")

def run_test_3():
    print("--- Running Test 3: Modern Tech ---")
    args = Namespace(
        arabic_text='تطبيقك الجديد\nأسرع، أذكى، أفضل',
        scene_prompt='abstract modern technology background, clean design, gradient blue and white, minimal, sleek',
        output='outputs/test3_tech.png',
        width=1152,
        height=896,
        font_style='default',
        font=None,
        text_effect='none',
        text_position='center',
        font_size=None,
        opacity=1.0,
        darken=0.0,
        padding=100,
        text_color='20,20,40', # Dark blue/black text
        negative_prompt='',
        seed=303,
        performance='Speed',
        styles=['Fooocus V2'],
        base_model=None,
        cfg_scale=7.0,
        image_number=1,
        lora=None,
        harmonize=0.25 # Low harmonize for clean graphics
    )
    result = arabic_poster_pipeline.run_full_pipeline(args)
    if result:
        copy_to_artifacts(result[0], "test3_tech.png")

if __name__ == '__main__':
    run_test_1()
    run_test_2()
    run_test_3()
