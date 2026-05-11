@echo off
SetLocal EnableDelayedExpansion

set OUTDIR=C:\Users\moham\AppData\Roaming\AionUi\aionui\opencode-temp-1778498849711\output_images_fooocus

echo ===== Fooocus Batch Generation Start: %date% %time% =====

set PROMPT1="futuristic AI brain with glowing neural networks, Arabic text floating, cyberpunk tech, dark blue purple neon glow, highly detailed, 8k"
set PROMPT2="AI teacher hologram interacting with student, futuristic classroom, augmented reality, glowing interface, warm lighting, highly detailed, 8k"
set PROMPT3="humanoid AI robot with glowing eyes, advanced mechanical details, dark futuristic background, blue cyan neon accents, highly detailed, 8k"
set PROMPT4="powerful AI brain radiating light, multiple data streams, digital consciousness concept, purple blue gradient, highly detailed, 8k"
set PROMPT5="AI medical diagnosis interface, holographic doctor, medical data visualization, green blue health colors, futuristic hospital, highly detailed, 8k"
set PROMPT6="digital transformation abstract art, flowing data streams, neon particles, dark background with cyan magenta lights, highly detailed, 8k"
set PROMPT7="neural network visualization in 3D space, glowing nodes and connections, purple blue gradient, dark background, highly detailed, 8k"
set PROMPT8="AI writing assistant concept, floating pen and glowing screen, creative sparks, dark blue background with warm lighting, highly detailed, 8k"
set PROMPT9="machine learning data flow, algorithms visualization, colorful data particles, dark tech background, cyan orange lights, highly detailed, 8k"
set PROMPT10="AI ethics concept, balance scale with digital brain, glowing decision points, futuristic abstract, purple blue theme, highly detailed, 8k"

echo [1/10] Generating reel_01.png ...
fooocus-cli.bat --prompt !PROMPT1! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 1
if errorlevel 1 (echo [FAIL] reel_01) else (echo [OK] reel_01)

echo [2/10] Generating reel_02.png ...
fooocus-cli.bat --prompt !PROMPT2! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 2
if errorlevel 1 (echo [FAIL] reel_02) else (echo [OK] reel_02)

echo [3/10] Generating reel_03.png ...
fooocus-cli.bat --prompt !PROMPT3! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 3
if errorlevel 1 (echo [FAIL] reel_03) else (echo [OK] reel_03)

echo [4/10] Generating reel_04.png ...
fooocus-cli.bat --prompt !PROMPT4! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 4
if errorlevel 1 (echo [FAIL] reel_04) else (echo [OK] reel_04)

echo [5/10] Generating reel_05.png ...
fooocus-cli.bat --prompt !PROMPT5! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 5
if errorlevel 1 (echo [FAIL] reel_05) else (echo [OK] reel_05)

echo [6/10] Generating reel_06.png ...
fooocus-cli.bat --prompt !PROMPT6! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 6
if errorlevel 1 (echo [FAIL] reel_06) else (echo [OK] reel_06)

echo [7/10] Generating reel_07.png ...
fooocus-cli.bat --prompt !PROMPT7! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 7
if errorlevel 1 (echo [FAIL] reel_07) else (echo [OK] reel_07)

echo [8/10] Generating reel_08.png ...
fooocus-cli.bat --prompt !PROMPT8! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 8
if errorlevel 1 (echo [FAIL] reel_08) else (echo [OK] reel_08)

echo [9/10] Generating reel_09.png ...
fooocus-cli.bat --prompt !PROMPT9! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 9
if errorlevel 1 (echo [FAIL] reel_09) else (echo [OK] reel_09)

echo [10/10] Generating reel_10.png ...
fooocus-cli.bat --prompt !PROMPT10! --aspect-ratio "896x1152" --performance "Speed" --output "%OUTDIR%" --image-number 10
if errorlevel 1 (echo [FAIL] reel_10) else (echo [OK] reel_10)

echo ===== Fooocus Batch Generation End: %date% %time% =====

dir "%OUTDIR%\*.png" /b

echo.
echo All done! Check output folder.
pause