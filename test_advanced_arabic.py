# -*- coding: utf-8 -*-
import subprocess
import shutil
import os
import sys

def copy_to_artifacts(source, name):
    dest = f"C:/Users/moham/.gemini/antigravity/brain/38fe042e-1503-4a04-8c58-bce4907c2b0b/{name}"
    if os.path.exists(source):
        shutil.copy2(source, dest)
        print(f"Copied {source} to artifacts as {name}")
    else:
        print(f"File not found: {source}")

def run_advanced_tests():
    python_exe = r".\python_embeded\python.exe"
    script = "arabic_poster_pipeline.py"

    # Test 1: Long wrapped text with pro_text
    print("\n--- Test 1: Wrapped Paragraph (Pro Text) ---")
    out1 = "outputs/advanced_1_wrap.png"
    cmd1 = [
        python_exe, script,
        "--preset", "pro_text",
        "--arabic-text", "رحلة الألف ميل تبدأ بخطوة واحدة. استمر في السعي نحو أهدافك مهما كانت التحديات، فالنجاح لا يأتي إلا لمن لا يستسلم.",
        "--scene-prompt", "cinematic epic mountain landscape at sunrise, adventurer standing on peak, breathtaking view, highly detailed masterpiece",
        "--font-style", "naskh",
        "--font-size", "80", 
        "--padding", "80",
        "--output", out1
    ]
    subprocess.run(cmd1)
    copy_to_artifacts(out1, "advanced_1_wrap.png")

    # Test 2: Clean Graphic with Exact Final Pass
    print("\n--- Test 2: Clean Graphic Product Ad ---")
    out2 = "outputs/advanced_2_clean.png"
    cmd2 = [
        python_exe, script,
        "--preset", "clean_graphic",
        "--arabic-text", "عطر الجاذبية\nالأناقة في زجاجة",
        "--scene-prompt", "luxurious perfume bottle on a marble pedestal, water splashes, studio lighting, hyper-realistic, 8k, advertisement",
        "--font-style", "default",
        "--text-color", "255,215,0", 
        "--darken", "0.3",
        "--output", out2
    ]
    subprocess.run(cmd2)
    copy_to_artifacts(out2, "advanced_2_clean.png")

    # Test 3: CPDS ControlNet Text Guidance
    print("\n--- Test 3: Heavy Integration (ControlNet Guided) ---")
    out3 = "outputs/advanced_3_cpds.png"
    cmd3 = [
        python_exe, script,
        "--preset", "balanced",
        "--text-guide", "both",
        "--cn-cpds-weight", "0.7",
        "--arabic-text", "القهوة\nسر الصباح",
        "--scene-prompt", "steaming cup of coffee on a rustic wooden table, coffee beans scattered, warm morning light, cozy atmosphere, photorealistic",
        "--font-style", "default",
        "--harmonize", "0.38",
        "--final-text-pass", "0.3",
        "--output", out3
    ]
    subprocess.run(cmd3)
    copy_to_artifacts(out3, "advanced_3_cpds.png")

if __name__ == "__main__":
    run_advanced_tests()
