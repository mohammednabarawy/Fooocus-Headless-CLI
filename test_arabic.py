# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath('d:/Fooocus_win64_2-5-0'))
import arabic_poster_pipeline
from argparse import Namespace

args = Namespace(
    arabic_text='بسم الله الرحمن الرحيم',
    scene_prompt='elegant Islamic geometric pattern background, dark blue and gold, arabesque, ornate',
    output='arabic_harmonized_test_clean.png',
    width=1152,
    height=896,
    font_style='naskh',
    font=None,
    text_effect='shadow',
    text_position='center',
    font_size=None,
    opacity=1.0,
    darken=0.35,
    padding=60,
    text_color='255,255,255',
    negative_prompt='',
    seed=42,
    performance='Speed',
    styles=['Fooocus V2'],
    base_model=None,
    cfg_scale=7.0,
    image_number=1,
    lora=None,
    harmonize=0.35
)

arabic_poster_pipeline.run_full_pipeline(args)
