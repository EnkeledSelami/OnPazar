# OnPazar — Compare Smarter. Pay Less.

OnPazar compares live product listings across retailers in Albania and Kosovo. The local application includes retailer search, offer comparison, price history, wishlist, price alerts, CSV import/export, and English/Albanian UI.

## Run the desktop app

Double-click OnPazar.exe in this folder. It runs locally; app data and its signing key are stored in %LOCALAPPDATA%\OnPazar. No account is required.

## Build the desktop app from source

Use Windows PowerShell with Python 3.9 installed:

    Set-Location .\OnPazarWeb
    .\build-onpazar.ps1

The build places a fresh OnPazar.exe in this repository root. Generated build folders and executable files are excluded from Git.

## Run the web app from source

    Set-Location .\OnPazarWeb
    py -3.9 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000. SQLite stores local price observations.

## Retailers

The app searches Shpresa, 3V Fejzo, Neptun, Globe, Aza, Megatek, Gjirafa50, Ozone, German Computers, and GoTech. Retailer catalogues and availability vary.

## Repository contents

- OnPazarWeb/: full Flask app, retailer adapters, templates, static assets, local desktop launcher, and packaging script.
- Root Python files: earlier three-retailer desktop implementation retained for reference. OnPazar.exe uses the newer OnPazarWeb app.
- PriceHistory.csv: sample/importable historical price data.

Render configuration is retained with the web source. Its PRICEPAL_* environment variable names remain for compatibility with the earlier hosted configuration.
