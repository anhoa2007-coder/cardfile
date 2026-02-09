# How to Build CardFile.exe

A simple guide to turn this Python app into a Windows program (.exe) that anyone can run.

## What You Need

- Python installed on your computer
- Internet connection (to download PyInstaller)

## Steps

### 1. Install PyInstaller

Open Command Prompt or PowerShell and type:

```
pip install pyinstaller
```

Wait for it to finish downloading.

### 2. Go to the CardFile Folder

Navigate to where your code is:

```
cd path\to\cardfile
```

### 3. Build the EXE

Run this command:

```
python -m PyInstaller --onefile --windowed --name "CardFile" main.py
```

**What the options mean:**
- `--onefile` = Everything packed into one single .exe file
- `--windowed` = No black console window when running
- `--name "CardFile"` = Name of your .exe file

### 4. Find Your EXE

When it's done, your program will be in:

```
dist\CardFile.exe
```

That's it! You can copy `CardFile.exe` anywhere and share it with others.

## Tips

- The .exe is about 11 MB (includes Python inside it)
- First run might be slow (Windows scans new programs)
- Works on any Windows PC, no Python needed to run it
