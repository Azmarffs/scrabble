#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.data.database import DatabaseManager

def main():
    """Main entry point for the Scrabble game application."""
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Scrabble")
    app.setOrganizationName("ScrabbleGame")
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    
    # Create and show the main window
    main_window = MainWindow(db_manager)
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 