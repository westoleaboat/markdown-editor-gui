# Markdown Editor GUI
This project is a PyQt-based GUI application for editing and viewing Markdown files. It provides a simple text editor with features like Markdown rendering, search and replace, and settings customization. This application serves as both a practical tool and an example of using PyQt5 to create desktop applications.


![Screenshot_select-area_20240914141100](https://github.com/user-attachments/assets/1149629f-56a3-4133-a6e5-ed6a20460939)

## Features

- **Markdown Editing**: Switch between raw text editing and rendered Markdown view.
- **Search and Replace**: Replace text with an intuitive side dock.
- **Character Count**: Real-time character count displayed in the status bar.
- **File Operations**: Open and save files with support for various formats.
- **Settings Dialog**: Configure application settings (e.g., toggle warnings).
- **Custom Dialogs**: Message boxes for alerts and an About dialog for app information.
- **Undo/Redo**: Built-in text editing capabilities.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/westoleaboat/markdown-editor-gui.git
   cd markdown-editor-gui
   ```

2. Install the required dependencies:
   ```
   pip install PyQt5
   ```

3. Run the application:
   ```
   python markdown_editor.py
   ```

## How to Use

1. Launch the application.
2. Use the **File Menu** or **Toolbar** to open or save files.
3. Toggle Markdown rendering via the "Toggle Markdown" button in the toolbar.
4. Use the dock widget to search and replace text.
5. Customize settings via the "Settings" option in the Edit menu.

## Settings

Settings are saved using `QSettings`, ensuring persistence across sessions. Current setting options:

- Toggle "Show Warnings" (display beta warnings on startup).

## Future Enhancements

- [ ] Add more Markdown formatting options.
- [ ] Implement themes for the editor.
- [ ] Enhance file format support (e.g., JSON, XML).
- [x] word count
- [x] word search and replace
- [x] save settings
- [x] markdown view
