# WSL Setup Guide

## Overview
This folder contains shell scripts (`.sh` files) that were originally designed for WSL (Windows Subsystem for Linux) environments. Since the system now runs natively on Windows, these files have been archived.

## Files Moved Here
- `*.sh` - All shell script files for Linux/WSL setup

## If You Need to Run on WSL

### Prerequisites
1. Install WSL2 on Windows
2. Install Ubuntu or preferred Linux distribution
3. Install Python 3.9+ in WSL environment

### Setup Steps
1. Copy the shell scripts from this folder to your WSL environment
2. Make scripts executable: `chmod +x *.sh`
3. Run the appropriate setup script for your needs:
   - `setup.sh` - Basic setup
   - `setup-production.sh` - Production environment setup
   - `setup-dev.sh` - Development environment setup

### Key Differences from Windows Setup
- Uses `apt` package manager instead of Windows installers
- Different path structures (`/home/user/` vs `C:\Users\user\`)
- Shell scripts instead of batch files
- Different browser installation process

### Current Recommendation
The system is optimized for native Windows operation. WSL setup is only recommended if you specifically need Linux environment features.

## Windows vs WSL Performance
- **Windows Native**: Better performance, direct Chrome integration, simpler setup
- **WSL**: Linux compatibility, but additional complexity and potential performance overhead

For most users, the Windows native setup is recommended.