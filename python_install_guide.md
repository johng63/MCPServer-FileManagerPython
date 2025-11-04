# File Manager MCP Server (Python) - Installation Guide

This guide will help you set up the Python version of the MCP server on your wife's Windows computer.

## What It Does

Your wife will be able to ask Claude to:
- **Unzip files** from Downloads
- **Move all SVG files** from Downloads to Documents
- **List zip files** or SVG files
- **View recent downloads**
- **Work with latest files** without remembering filenames
- **Organize files** into subfolders

---

## Step 1: Install Python

1. Download Python from: https://www.python.org/downloads/
2. Choose **Python 3.11 or newer**
3. **IMPORTANT**: During installation, check the box "Add Python to PATH"
4. Click "Install Now"
5. Restart the computer after installation

### Verify Python Installation
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Type: `python --version`
4. You should see something like "Python 3.11.x" or "Python 3.12.x"

---

## Step 2: Create the Server Folder

1. Open File Explorer
2. Go to `C:\`
3. Create a new folder called `MCPServer`
4. You should now have: `C:\MCPServer\`

---

## Step 3: Add the Server Files

1. Copy the **server.py** file into `C:\MCPServer\`
2. Copy the **requirements.txt** file into `C:\MCPServer\`

Your folder should look like:
```
C:\MCPServer\
  ├── server.py
  └── requirements.txt
```

---

## Step 4: Install Python Dependencies

1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. In the command prompt, type:
   ```
   cd C:\MCPServer
   ```
4. Then type:
   ```
   pip install -r requirements.txt
   ```
5. Wait for it to finish (should take 10-30 seconds)
6. Close the command prompt

---

## Step 5: Configure Claude Desktop

1. Press `Windows Key + R`
2. Type `%APPDATA%\Claude\` and press Enter
3. Look for a file called `claude_desktop_config.json`
   - If it exists, open it with Notepad
   - If it doesn't exist, create a new file called `claude_desktop_config.json`
4. Add or update the configuration:

```json
{
  "mcpServers": {
    "file-manager": {
      "command": "python",
      "args": ["C:\\MCPServer\\server.py"]
    }
  }
}
```

**Note:** If you already have other MCP servers configured, add the `"file-manager"` section inside the existing `"mcpServers"` object.

5. Save the file
6. **Completely close Claude Desktop** (right-click the system tray icon and choose Exit)
7. Restart Claude Desktop

---

## Step 6: Test It!

Once Claude Desktop restarts, your wife can test it by asking Claude:

**"Can you list the zip files in my Downloads?"**

or

**"Please unzip myfile.zip from Downloads"**

or

**"What are my recent downloads?"**

---

## What Your Wife Can Ask

Here are example phrases she can use:

### Working with Latest Downloads
- **"What are my recent downloads?"**
- **"Show me the latest zip files"**
- **"Unzip my latest download and move the SVGs to DoorHanger"**
- **"Extract the newest zip file"**
- **"What did I download today?"**

### Combined Operations
- **"Unzip project.zip and move all SVG files to DoorHanger"**
- **"Extract icons.zip and put the SVG files in the Icons folder"**

### Unzipping Files
- "Unzip archive.zip"
- "Extract project.zip to Documents"

### Moving SVGs to Specific Folders
- "Move all SVG files to DoorHanger folder"
- "Put all my SVG files in the Graphics/Logos folder"

### Listing Files
- "What zip files do I have in Downloads?"
- "Show me all SVG files"

---

## Troubleshooting

### Claude doesn't respond to file commands
1. Make sure Claude Desktop was completely restarted after configuration
2. Check that the config file is in the right location: `%APPDATA%\Claude\`
3. Verify the path in the config is: `C:\\MCPServer\\server.py` (with double backslashes)

### "Python not found" error
- Make sure Python is installed and added to PATH
- Try using `python3` instead of `python` in the config:
  ```json
  "command": "python3",
  ```

### "Module not found" error
- Run `pip install -r requirements.txt` again in the `C:\MCPServer` folder
- Make sure you're in the correct directory when running the command

### Can't find config file location
- The full path is usually: `C:\Users\[Username]\AppData\Roaming\Claude\claude_desktop_config.json`

---

## Advantages of Python Version

✅ **Single file** - No node_modules folder  
✅ **Faster startup** - Python typically starts faster  
✅ **Easier to read/modify** - Python syntax is more straightforward  
✅ **Built-in zipfile** - No external zip library needed  

---

## Uninstalling

If you ever want to remove this:

1. Delete `C:\MCPServer\` folder
2. Remove the `"file-manager"` section from `claude_desktop_config.json`
3. Restart Claude Desktop

---

## Need Help?

The server logs errors to help with debugging. If something isn't working:
1. Close Claude Desktop completely
2. Open Command Prompt
3. Type: `cd C:\MCPServer`
4. Type: `python server.py`
5. Try a command - you'll see any error messages
6. Press Ctrl+C to stop
