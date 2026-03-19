#!/usr/bin/env python3
"""
Setup script for HEXSTORM game.
Automatically installs all required dependencies if not already present.
"""

import subprocess
import sys
import importlib.util


def check_and_install_package(package_name, import_name=None):
    """Check if a package is installed and install it if not."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.util.find_spec(import_name)
        print(f"✓ {package_name} is already installed")
        return True
    except ImportError:
        print(f"✗ {package_name} not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✓ {package_name} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package_name}: {e}")
            return False


def install_requirements():
    """Install all packages from requirements.txt."""
    try:
        with open("requirements.txt", "r") as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        print("Installing dependencies from requirements.txt...")
        success = True
        
        for package in packages:
            if not check_and_install_package(package):
                success = False
        
        return success
    except FileNotFoundError:
        print("requirements.txt not found. Installing pygame only...")
        return check_and_install_package("pygame")


def main():
    """Main setup function."""
    print("HEXSTORM Setup - Installing Dependencies")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    
    # Install dependencies
    if install_requirements():
        print("\n✓ All dependencies installed successfully!")
        print("You can now run the game with: python main.py")
    else:
        print("\n✗ Some dependencies failed to install")
        print("Please install them manually: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
