#!/usr/bin/env python3

import asyncio
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Get user's Downloads and Documents directories
DOWNLOADS_DIR = Path.home() / "Downloads"
DOCUMENTS_DIR = Path.home() / "OneDrive" / "Documents"


class FileManagerServer:
    def __init__(self):
        self.server = Server("file-manager")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="unzip_file",
                    description="Unzip a file from the Downloads directory. You can specify where to extract it, or it will extract to Downloads by default.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the zip file in Downloads (e.g., 'archive.zip')",
                            },
                            "destination": {
                                "type": "string",
                                "description": "Optional: Where to extract files (defaults to Downloads). Use 'downloads' or 'documents' or a specific path.",
                            },
                        },
                        "required": ["filename"],
                    },
                ),
                Tool(
                    name="move_svg_files",
                    description="Find and move all SVG files from Downloads to Documents directory. Can move to a specific subfolder in Documents (e.g., 'DoorHanger', 'Icons', 'Graphics').",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Optional: Source directory to search for SVG files (defaults to Downloads). Can be a path relative to Downloads if unzipping created a subfolder.",
                            },
                            "subfolder": {
                                "type": "string",
                                "description": "Optional: Subfolder name in Documents where SVG files should be moved (e.g., 'DoorHanger', 'Projects/Icons'). Will be created if it doesn't exist.",
                            },
                        },
                    },
                ),
                Tool(
                    name="list_zip_files",
                    description="List all zip files in the Downloads directory, sorted by date (newest first)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "number",
                                "description": "Optional: Maximum number of files to show (default: 10)",
                            },
                        },
                    },
                ),
                Tool(
                    name="list_svg_files",
                    description="List all SVG files in Downloads or a specified directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Optional: Directory to search (defaults to Downloads)",
                            },
                        },
                    },
                ),
                Tool(
                    name="unzip_and_move_svgs",
                    description="Combined operation: Unzip a file and then move all SVG files from the extracted folder to a specified location in Documents. Perfect for 'unzip project.zip and move SVGs to DoorHanger' requests.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the zip file in Downloads (e.g., 'project.zip')",
                            },
                            "destination_folder": {
                                "type": "string",
                                "description": "Subfolder in Documents where SVG files should go (e.g., 'DoorHanger', 'Icons')",
                            },
                        },
                        "required": ["filename", "destination_folder"],
                    },
                ),
                Tool(
                    name="list_recent_downloads",
                    description="Show the most recently downloaded files in the Downloads directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "number",
                                "description": "Optional: Number of recent files to show (default: 10)",
                            },
                            "file_type": {
                                "type": "string",
                                "description": "Optional: Filter by file extension (e.g., 'zip', 'pdf', 'svg')",
                            },
                        },
                    },
                ),
                Tool(
                    name="unzip_latest",
                    description="Unzip the most recently downloaded zip file from Downloads",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "destination": {
                                "type": "string",
                                "description": "Optional: Where to extract files (defaults to Downloads). Use 'downloads' or 'documents' or a specific path.",
                            },
                        },
                    },
                ),
                Tool(
                    name="unzip_latest_and_move_svgs",
                    description="Unzip the most recently downloaded zip file and move all SVG files to a specified folder in Documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "destination_folder": {
                                "type": "string",
                                "description": "Subfolder in Documents where SVG files should go (e.g., 'DoorHanger', 'Icons')",
                            },
                        },
                        "required": ["destination_folder"],
                    },
                ),
                Tool(
                    name="create_directory",
                    description="Create a new directory/folder. Can create in Documents, Downloads, or specify a full path.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the folder to create (e.g., 'MyProject', 'Photos/Vacation2024')",
                            },
                            "location": {
                                "type": "string",
                                "description": "Optional: Where to create the folder. Use 'documents' (default), 'downloads', or a full path.",
                            },
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="move_latest_svg",
                    description="Move only the most recently downloaded/modified SVG file from Downloads to a folder in Documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "destination_folder": {
                                "type": "string",
                                "description": "Subfolder in Documents where the SVG file should go (e.g., 'DoorHanger', 'Icons')",
                            },
                            "source": {
                                "type": "string",
                                "description": "Optional: Source directory to search (defaults to Downloads)",
                            },
                        },
                        "required": ["destination_folder"],
                    },
                ),
                Tool(
                    name="copy_file",
                    description="Copy a specific file by name from Downloads to Documents or another location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to copy (e.g., 'report.pdf', 'image.png')",
                            },
                            "destination_folder": {
                                "type": "string",
                                "description": "Optional: Subfolder in Documents where the file should go. If not specified, copies to Documents root.",
                            },
                            "source": {
                                "type": "string",
                                "description": "Optional: Source directory (defaults to Downloads). Can be 'downloads', 'documents', or a full path.",
                            },
                        },
                        "required": ["filename"],
                    },
                ),
                Tool(
                    name="move_file",
                    description="Move a specific file by name from Downloads to Documents or another location (removes from original location)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to move (e.g., 'report.pdf', 'image.png')",
                            },
                            "destination_folder": {
                                "type": "string",
                                "description": "Optional: Subfolder in Documents where the file should go. If not specified, moves to Documents root.",
                            },
                            "source": {
                                "type": "string",
                                "description": "Optional: Source directory (defaults to Downloads). Can be 'downloads', 'documents', or a full path.",
                            },
                        },
                        "required": ["filename"],
                    },
                ),
                Tool(
                    name="list_files",
                    description="List files in a directory, sorted by most recent first. Can filter by file type.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Optional: Directory to list (defaults to Downloads). Can be 'downloads', 'documents', a subfolder like 'documents/Projects', or a full path.",
                            },
                            "file_type": {
                                "type": "string",
                                "description": "Optional: Filter by file extension (e.g., 'pdf', 'svg', 'png')",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Optional: Maximum number of files to show (default: 20)",
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "unzip_file":
                    return await self.handle_unzip(arguments)
                elif name == "move_svg_files":
                    return await self.handle_move_svg(arguments)
                elif name == "list_zip_files":
                    return await self.handle_list_zip(arguments)
                elif name == "list_svg_files":
                    return await self.handle_list_svg(arguments)
                elif name == "unzip_and_move_svgs":
                    return await self.handle_unzip_and_move_svgs(arguments)
                elif name == "list_recent_downloads":
                    return await self.handle_list_recent_downloads(arguments)
                elif name == "unzip_latest":
                    return await self.handle_unzip_latest(arguments)
                elif name == "unzip_latest_and_move_svgs":
                    return await self.handle_unzip_latest_and_move_svgs(arguments)
                elif name == "create_directory":
                    return await self.handle_create_directory(arguments)
                elif name == "move_latest_svg":
                    return await self.handle_move_latest_svg(arguments)
                elif name == "copy_file":
                    return await self.handle_copy_file(arguments)
                elif name == "move_file":
                    return await self.handle_move_file(arguments)
                elif name == "list_files":
                    return await self.handle_list_files(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_unzip(self, args: dict) -> list[TextContent]:
        filename = args.get("filename")
        if not filename:
            raise ValueError("filename is required")

        zip_path = DOWNLOADS_DIR / filename

        if not zip_path.exists():
            raise ValueError(f"Zip file not found: {filename}")

        # Determine destination
        dest_dir = DOWNLOADS_DIR
        if "destination" in args:
            dest = args["destination"].lower()
            if dest == "downloads":
                dest_dir = DOWNLOADS_DIR
            elif dest == "documents":
                dest_dir = DOCUMENTS_DIR
            else:
                dest_dir = Path(args["destination"]).resolve()

        # Extract zip
        extract_path = dest_dir / zip_path.stem
        extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
            file_list = zip_ref.namelist()

        return [
            TextContent(
                type="text",
                text=f"Successfully unzipped {filename} to {extract_path}\n\nExtracted {len(file_list)} files:\n" + "\n".join(file_list),
            )
        ]

    async def handle_move_svg(self, args: dict) -> list[TextContent]:
        source_dir = Path(args.get("source", DOWNLOADS_DIR)).resolve()

        if not source_dir.exists():
            raise ValueError(f"Source directory not found: {source_dir}")

        # Determine destination
        dest_dir = DOCUMENTS_DIR
        if "subfolder" in args:
            dest_dir = DOCUMENTS_DIR / args["subfolder"]
            dest_dir.mkdir(parents=True, exist_ok=True)

        # Find all SVG files recursively
        svg_files = await self.find_files(source_dir, ".svg")

        if not svg_files:
            return [
                TextContent(
                    type="text", text=f"No SVG files found in {source_dir}"
                )
            ]

        # Move each SVG file
        moved_files = []
        for svg_path in svg_files:
            filename = svg_path.name
            dest_path = dest_dir / filename

            # Handle duplicate filenames
            final_dest_path = dest_path
            counter = 1
            while final_dest_path.exists():
                stem = svg_path.stem
                suffix = svg_path.suffix
                final_dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            svg_path.rename(final_dest_path)
            moved_files.append(final_dest_path.name)

        return [
            TextContent(
                type="text",
                text=f"Successfully moved {len(moved_files)} SVG file(s) from {source_dir} to {dest_dir}\n\nMoved files:\n" + "\n".join(moved_files),
            )
        ]

    async def handle_list_zip(self, args: dict) -> list[TextContent]:
        limit = args.get("limit", 10)
        
        if not DOWNLOADS_DIR.exists():
            raise ValueError(f"Downloads directory not found: {DOWNLOADS_DIR}")

        zip_files = [f for f in DOWNLOADS_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".zip"]

        if not zip_files:
            return [
                TextContent(
                    type="text", text=f"No zip files found in {DOWNLOADS_DIR}"
                )
            ]

        # Get file details with timestamps
        file_details = []
        for file in zip_files:
            stats = file.stat()
            file_details.append({
                "name": file.name,
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime),
            })

        # Sort by modified date (newest first)
        file_details.sort(key=lambda x: x["modified"], reverse=True)

        # Limit results
        limited_files = file_details[:limit]

        file_list = []
        for file in limited_files:
            size_mb = file["size"] / (1024 * 1024)
            date_str = file["modified"].strftime("%m/%d/%Y, %I:%M %p")
            file_list.append(f"{file['name']} ({size_mb:.2f} MB) - {date_str}")

        return [
            TextContent(
                type="text",
                text=f"Found {len(zip_files)} zip file(s) in Downloads (showing {len(limited_files)} most recent):\n\n" + "\n".join(file_list),
            )
        ]

    async def handle_list_svg(self, args: dict) -> list[TextContent]:
        search_dir = Path(args.get("directory", DOWNLOADS_DIR)).resolve()

        if not search_dir.exists():
            raise ValueError(f"Directory not found: {search_dir}")

        svg_files = await self.find_files(search_dir, ".svg")

        if not svg_files:
            return [
                TextContent(
                    type="text", text=f"No SVG files found in {search_dir}"
                )
            ]

        relative_paths = [str(f.relative_to(search_dir)) for f in svg_files]

        return [
            TextContent(
                type="text",
                text=f"Found {len(svg_files)} SVG file(s) in {search_dir}:\n\n" + "\n".join(relative_paths),
            )
        ]

    async def handle_unzip_and_move_svgs(self, args: dict) -> list[TextContent]:
        filename = args.get("filename")
        destination_folder = args.get("destination_folder")

        if not filename:
            raise ValueError("filename is required")
        if not destination_folder:
            raise ValueError("destination_folder is required")

        # Step 1: Unzip the file
        zip_path = DOWNLOADS_DIR / filename

        if not zip_path.exists():
            raise ValueError(f"Zip file not found: {filename}")

        extract_path = DOWNLOADS_DIR / zip_path.stem
        extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
            total_files = len(zip_ref.namelist())

        # Step 2: Find all SVG files in the extracted folder
        svg_files = await self.find_files(extract_path, ".svg")

        if not svg_files:
            return [
                TextContent(
                    type="text",
                    text=f"Successfully unzipped {filename} ({total_files} files) to {extract_path}\n\nBut no SVG files were found in the archive.",
                )
            ]

        # Step 3: Create destination folder in Documents
        dest_dir = DOCUMENTS_DIR / destination_folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Step 4: Move each SVG file
        moved_files = []
        for svg_path in svg_files:
            filename_svg = svg_path.name
            dest_path = dest_dir / filename_svg

            # Handle duplicate filenames
            final_dest_path = dest_path
            counter = 1
            while final_dest_path.exists():
                stem = svg_path.stem
                suffix = svg_path.suffix
                final_dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            svg_path.rename(final_dest_path)
            moved_files.append(final_dest_path.name)

        return [
            TextContent(
                type="text",
                text=f"Success! 🎉\n\n1. Unzipped {args['filename']} ({total_files} total files)\n2. Found {len(svg_files)} SVG file(s)\n3. Moved all SVGs to Documents\\{destination_folder}\n\nMoved files:\n" + "\n".join(moved_files),
            )
        ]

    async def handle_list_recent_downloads(self, args: dict) -> list[TextContent]:
        limit = args.get("limit", 10)
        file_type = args.get("file_type", "").lower()

        if not DOWNLOADS_DIR.exists():
            raise ValueError(f"Downloads directory not found: {DOWNLOADS_DIR}")

        # Get file details
        file_details = []
        for file in DOWNLOADS_DIR.iterdir():
            if file.is_file():
                try:
                    stats = file.stat()
                    extension = file.suffix.lower().lstrip(".")
                    file_details.append({
                        "name": file.name,
                        "size": stats.st_size,
                        "modified": datetime.fromtimestamp(stats.st_mtime),
                        "extension": extension,
                    })
                except Exception:
                    # Skip files we can't access
                    pass

        # Apply file type filter
        if file_type:
            file_details = [f for f in file_details if f["extension"] == file_type]

        if not file_details:
            type_msg = f" of type '{file_type}'" if file_type else ""
            return [
                TextContent(
                    type="text", text=f"No files{type_msg} found in Downloads"
                )
            ]

        # Sort by modified date (newest first)
        file_details.sort(key=lambda x: x["modified"], reverse=True)

        # Limit results
        limited_files = file_details[:limit]

        file_list = []
        for index, file in enumerate(limited_files):
            size = file["size"]
            if size > 1024 * 1024:
                display_size = f"{size / (1024 * 1024):.2f} MB"
            else:
                display_size = f"{size / 1024:.2f} KB"
            
            date_str = file["modified"].strftime("%m/%d/%Y, %I:%M %p")
            badge = " [LATEST]" if index == 0 else ""
            file_list.append(f"{file['name']}{badge}\n  Size: {display_size} | Downloaded: {date_str}")

        type_msg = f" (filtered to .{file_type} files)" if file_type else ""
        return [
            TextContent(
                type="text",
                text=f"Recent downloads{type_msg} (showing {len(limited_files)} of {len(file_details)}):\n\n" + "\n\n".join(file_list),
            )
        ]

    async def handle_unzip_latest(self, args: dict) -> list[TextContent]:
        if not DOWNLOADS_DIR.exists():
            raise ValueError(f"Downloads directory not found: {DOWNLOADS_DIR}")

        zip_files = [f for f in DOWNLOADS_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".zip"]

        if not zip_files:
            raise ValueError("No zip files found in Downloads")

        # Get the most recent zip file
        latest_zip = max(zip_files, key=lambda f: f.stat().st_mtime)

        # Use the existing unzip logic
        result = await self.handle_unzip({
            "filename": latest_zip.name,
            "destination": args.get("destination"),
        })

        # Modify the message to indicate it was the latest
        text = result[0].text.replace(
            f"Successfully unzipped {latest_zip.name}",
            f"Successfully unzipped the latest download: {latest_zip.name}",
        )

        return [TextContent(type="text", text=text)]

    async def handle_unzip_latest_and_move_svgs(self, args: dict) -> list[TextContent]:
        destination_folder = args.get("destination_folder")

        if not destination_folder:
            raise ValueError("destination_folder is required")

        if not DOWNLOADS_DIR.exists():
            raise ValueError(f"Downloads directory not found: {DOWNLOADS_DIR}")

        # Find the latest zip file
        zip_files = [f for f in DOWNLOADS_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".zip"]

        if not zip_files:
            raise ValueError("No zip files found in Downloads")

        latest_zip = max(zip_files, key=lambda f: f.stat().st_mtime)

        # Use the existing unzip and move logic
        return await self.handle_unzip_and_move_svgs({
            "filename": latest_zip.name,
            "destination_folder": destination_folder,
        })

    async def handle_create_directory(self, args: dict) -> list[TextContent]:
        name = args.get("name")
        if not name:
            raise ValueError("name is required")

        location = args.get("location", "documents").lower()

        # Determine base directory
        if location == "documents":
            base_dir = DOCUMENTS_DIR
        elif location == "downloads":
            base_dir = DOWNLOADS_DIR
        else:
            base_dir = Path(location).resolve()

        # Create the full path
        new_dir = base_dir / name

        if new_dir.exists():
            return [
                TextContent(
                    type="text",
                    text=f"Directory already exists: {new_dir}",
                )
            ]

        new_dir.mkdir(parents=True, exist_ok=True)

        return [
            TextContent(
                type="text",
                text=f"Successfully created directory: {new_dir}",
            )
        ]

    async def handle_move_latest_svg(self, args: dict) -> list[TextContent]:
        destination_folder = args.get("destination_folder")
        if not destination_folder:
            raise ValueError("destination_folder is required")

        source_dir = Path(args.get("source", DOWNLOADS_DIR)).resolve()

        if not source_dir.exists():
            raise ValueError(f"Source directory not found: {source_dir}")

        # Find all SVG files
        svg_files = await self.find_files(source_dir, ".svg")

        if not svg_files:
            return [
                TextContent(
                    type="text", text=f"No SVG files found in {source_dir}"
                )
            ]

        # Get the most recent SVG file by modification time
        latest_svg = max(svg_files, key=lambda f: f.stat().st_mtime)

        # Create destination folder in Documents
        dest_dir = DOCUMENTS_DIR / destination_folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Determine destination path
        dest_path = dest_dir / latest_svg.name

        # Handle duplicate filenames
        final_dest_path = dest_path
        counter = 1
        while final_dest_path.exists():
            stem = latest_svg.stem
            suffix = latest_svg.suffix
            final_dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Move the file
        latest_svg.rename(final_dest_path)

        return [
            TextContent(
                type="text",
                text=f"Successfully moved the latest SVG file to {final_dest_path}\n\nFile: {latest_svg.name}",
            )
        ]

    async def handle_copy_file(self, args: dict) -> list[TextContent]:
        filename = args.get("filename")
        if not filename:
            raise ValueError("filename is required")

        # Determine source directory
        source_arg = args.get("source", "downloads").lower()
        if source_arg == "downloads":
            source_dir = DOWNLOADS_DIR
        elif source_arg == "documents":
            source_dir = DOCUMENTS_DIR
        else:
            source_dir = Path(source_arg).resolve()

        source_file = source_dir / filename

        if not source_file.exists():
            # Try to find the file recursively if not found at top level
            found_files = list(source_dir.rglob(filename))
            if found_files:
                source_file = found_files[0]
            else:
                raise ValueError(f"File not found: {filename} in {source_dir}")

        # Determine destination
        dest_folder = args.get("destination_folder", "")
        if dest_folder:
            dest_dir = DOCUMENTS_DIR / dest_folder
        else:
            dest_dir = DOCUMENTS_DIR

        dest_dir.mkdir(parents=True, exist_ok=True)

        # Determine destination path
        dest_path = dest_dir / source_file.name

        # Handle duplicate filenames
        final_dest_path = dest_path
        counter = 1
        while final_dest_path.exists():
            stem = source_file.stem
            suffix = source_file.suffix
            final_dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Copy the file
        shutil.copy2(source_file, final_dest_path)

        return [
            TextContent(
                type="text",
                text=f"Successfully copied {source_file.name} to {final_dest_path}",
            )
        ]

    async def handle_move_file(self, args: dict) -> list[TextContent]:
        filename = args.get("filename")
        if not filename:
            raise ValueError("filename is required")

        # Determine source directory
        source_arg = args.get("source", "downloads").lower()
        if source_arg == "downloads":
            source_dir = DOWNLOADS_DIR
        elif source_arg == "documents":
            source_dir = DOCUMENTS_DIR
        else:
            source_dir = Path(source_arg).resolve()

        source_file = source_dir / filename

        if not source_file.exists():
            # Try to find the file recursively if not found at top level
            found_files = list(source_dir.rglob(filename))
            if found_files:
                source_file = found_files[0]
            else:
                raise ValueError(f"File not found: {filename} in {source_dir}")

        # Determine destination
        dest_folder = args.get("destination_folder", "")
        if dest_folder:
            dest_dir = DOCUMENTS_DIR / dest_folder
        else:
            dest_dir = DOCUMENTS_DIR

        dest_dir.mkdir(parents=True, exist_ok=True)

        # Determine destination path
        dest_path = dest_dir / source_file.name

        # Handle duplicate filenames
        final_dest_path = dest_path
        counter = 1
        while final_dest_path.exists():
            stem = source_file.stem
            suffix = source_file.suffix
            final_dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Move the file
        source_file.rename(final_dest_path)

        return [
            TextContent(
                type="text",
                text=f"Successfully moved {filename} to {final_dest_path}",
            )
        ]

    async def handle_list_files(self, args: dict) -> list[TextContent]:
        limit = args.get("limit", 20)
        file_type = args.get("file_type", "").lower().lstrip(".")

        # Determine directory
        dir_arg = args.get("directory", "downloads").lower()
        if dir_arg == "downloads":
            search_dir = DOWNLOADS_DIR
        elif dir_arg == "documents":
            search_dir = DOCUMENTS_DIR
        elif dir_arg.startswith("documents/") or dir_arg.startswith("documents\\"):
            subfolder = dir_arg.split("/", 1)[-1].split("\\", 1)[-1]
            search_dir = DOCUMENTS_DIR / subfolder
        elif dir_arg.startswith("downloads/") or dir_arg.startswith("downloads\\"):
            subfolder = dir_arg.split("/", 1)[-1].split("\\", 1)[-1]
            search_dir = DOWNLOADS_DIR / subfolder
        else:
            search_dir = Path(dir_arg).resolve()

        if not search_dir.exists():
            raise ValueError(f"Directory not found: {search_dir}")

        # Get file details
        file_details = []
        for file in search_dir.iterdir():
            if file.is_file():
                try:
                    stats = file.stat()
                    extension = file.suffix.lower().lstrip(".")
                    file_details.append({
                        "name": file.name,
                        "size": stats.st_size,
                        "modified": datetime.fromtimestamp(stats.st_mtime),
                        "extension": extension,
                    })
                except Exception:
                    pass

        # Apply file type filter
        if file_type:
            file_details = [f for f in file_details if f["extension"] == file_type]

        if not file_details:
            type_msg = f" of type '.{file_type}'" if file_type else ""
            return [
                TextContent(
                    type="text", text=f"No files{type_msg} found in {search_dir}"
                )
            ]

        # Sort by modified date (newest first)
        file_details.sort(key=lambda x: x["modified"], reverse=True)

        # Limit results
        limited_files = file_details[:limit]

        file_list = []
        for index, file in enumerate(limited_files):
            size = file["size"]
            if size > 1024 * 1024:
                display_size = f"{size / (1024 * 1024):.2f} MB"
            elif size > 1024:
                display_size = f"{size / 1024:.2f} KB"
            else:
                display_size = f"{size} bytes"

            date_str = file["modified"].strftime("%m/%d/%Y, %I:%M %p")
            badge = " [LATEST]" if index == 0 else ""
            file_list.append(f"{file['name']}{badge}\n  Size: {display_size} | Modified: {date_str}")

        type_msg = f" (filtered to .{file_type} files)" if file_type else ""
        return [
            TextContent(
                type="text",
                text=f"Files in {search_dir}{type_msg}\nShowing {len(limited_files)} of {len(file_details)} (sorted by most recent):\n\n" + "\n\n".join(file_list),
            )
        ]

    async def find_files(self, directory: Path, extension: str) -> List[Path]:
        results = []
        for item in directory.rglob(f"*{extension}"):
            if item.is_file():
                results.append(item)
        return results

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    server = FileManagerServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())