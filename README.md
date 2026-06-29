<div align="center">
  <img src="ghostwave.png" alt="GhostWave Logo" width="200"/>
  <h1>Gw</h1>
</div>

A lightweight utility to quickly block MotiveWave's license heartbeat, allowing you to use your license on another machine without having to close the app on your current one.

or share ur license with a friend and use it at the same time as them lol

## How it works
MotiveWave pings its licensing server every 60 seconds. This tool simply adds a local block in your Windows `hosts` file to drop that connection. The server assumes your PC went offline and releases the license to your home PC. MotiveWave keeps running perfectly fine offline in the background on your laptop

## Usage
1. Go to the `release` folder and download `GhostWave.exe`.
2. Right-click the `.exe` and select **Run as Administrator** (it requires admin privileges to edit the Windows network hosts file).
3. Click **Drop Connection** when you wanna use your license on another machine or with a friend.
4. Click **Restore Connection** when you're done, doesn't really matter.

## Build from Source
If you prefer to compile the python script yourself:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --uac-admin --name "GhostWave" --icon "ghostwave.ico" src/mw_killswitch.py
```

## Preview
![App in Use](Screenshot.png)

## Historical Data Downloader
Separately included is a script that pulls historical bar and tick data straight from MotiveWave's S3 servers. No login required.

```bash
# List available data for a symbol
python src/data_downloader.py ENQU6.CME --list

# Download all data
python src/data_downloader.py ENQU6.CME

# Download only bar data
python src/data_downloader.py ENQU6.CME --type bar

# Download only tick data
python src/data_downloader.py ENQU6.CME --type tick
```

yeah this gives you edge too
