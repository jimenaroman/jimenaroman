# Setting up your pastel profile ♡

1. Make a new public repo named **exactly** your GitHub username
   (e.g. `sparkle-dev/sparkle-dev`). GitHub shows its README on your profile.
2. Upload everything from this folder, keeping the folders as they are
   (`assets/`, `tools/`, `.github/workflows/`).
3. In `README.md`, replace `YOUR-USERNAME` (3 spots), `YOUR NAME`, the bio line,
   and the three links. In the typing lines, spaces are `+` and `%E2%99%A1` is the ♡.
4. Turn on the snake: repo **Settings → Actions → General → Workflow permissions →
   Read and write permissions** → Save. Then **Actions → Pastel snake → Run workflow**.
   After a minute an `output` branch appears and the snake shows up.

## Your own header photo

The included header is made-up clouds. To use a photo of yours:

    pip install pillow numpy
    python3 tools/pastel_header.py my-photo.jpg              # pink → blue
    python3 tools/pastel_header.py my-photo.jpg --mode pink  # just pink
    python3 tools/pastel_header.py my-photo.jpg --mode blue  # just blue

Then commit the new `assets/header-dark.png` and `assets/header-light.png`.
Use `--top 0.2` (higher up) or `--top 0.6` (lower) to choose which strip of the
photo becomes the banner, and `--gamma 2` for sparser, sparklier dots.

## Colours used
pink `#F7A8C8` · lilac `#C9B6F2` · baby blue `#A8D8F7`
(deeper pink `#E88AB4` / blue `#7FB8E6` for light mode so it stays readable)
