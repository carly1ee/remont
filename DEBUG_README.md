# Flask Debug Setup Guide

This guide explains how to debug the Flask application running in Docker.

## 🚀 Quick Start

### Option 1: Using the provided scripts

**Windows:**
```bash
debug-setup.cmd
```

**Linux/Mac:**
```bash
chmod +x debug-setup.sh
./debug-setup.sh
```

### Option 2: Manual setup

1. Start the debug environment:
```bash
docker-compose -f docker-compose.debug.yml up --build -d
```

2. Wait for containers to be ready:
```bash
docker-compose -f docker-compose.debug.yml ps
```

3. Test the application:
```bash
curl http://localhost:5000
# Should return: "Backend работает должным образом."
```

4. In VS Code:
   - Press `Ctrl+Shift+D` to open Run and Debug
   - Select "Debug Flask in Docker" configuration
   - Press `F5` to start debugging

## 🔧 Debug Configuration

### Files Created:

- `backend/Dockerfile.debug` - Debug-specific Dockerfile with debugging tools
- `docker-compose.debug.yml` - Debug docker-compose configuration
- `.vscode/launch.json` - VS Code debug configurations
- `.vscode/settings.json` - VS Code workspace settings

### Debug Features:

- **Remote Debugging**: Uses `debugpy` for remote debugging
- **Live Code Changes**: Volume mounting allows live code changes
- **Breakpoints**: Set breakpoints in VS Code and they'll work in Docker
- **Hot Reload**: Flask debug mode enables automatic reloading
- **Interactive Debugging**: Full debugging capabilities in VS Code

## 📋 Debug Configurations

### 1. Debug Flask in Docker
- **Type**: Remote attach
- **Port**: 5678
- **Use Case**: Debugging the Flask app running in Docker container

### 2. Debug Flask Local
- **Type**: Launch
- **Use Case**: Debugging Flask app running locally (without Docker)

## 🛠️ Available Commands

```bash
# Start debug environment
docker-compose -f docker-compose.debug.yml up --build -d

# View logs
docker-compose -f docker-compose.debug.yml logs -f app

# Stop debug environment
docker-compose -f docker-compose.debug.yml down

# Rebuild containers
docker-compose -f docker-compose.debug.yml up --build

# Check container status
docker-compose -f docker-compose.debug.yml ps
```

## 🔍 Debugging Tips

1. **Setting Breakpoints**: Click in the left margin of your Python files in VS Code
2. **Variable Inspection**: Use the Debug Console to inspect variables
3. **Step Through Code**: Use F10 (step over), F11 (step into), F12 (step out)
4. **Watch Variables**: Add variables to the Watch panel
5. **Call Stack**: Use the Call Stack panel to navigate through function calls

## 🌐 Access Points

- **Flask Application**: http://localhost:5000
- **Debug Port**: localhost:5678
- **Database**: localhost:5434 (PostgreSQL)

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.debug.yml logs app

# Rebuild without cache
docker-compose -f docker-compose.debug.yml build --no-cache
```

### Can't connect to debugger
1. Ensure the debug container is running
2. Check that port 5678 is not blocked by firewall
3. Verify VS Code Python extension is installed

### Code changes not reflecting
1. Ensure volume mounting is working
2. Check if Flask debug mode is enabled
3. Restart the container if needed

## 📝 Environment Variables

The debug environment includes these additional variables:
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`

These enable Flask's debug features like:
- Automatic reloading on code changes
- Detailed error pages
- Debug toolbar (if installed)

## 🔒 Security Note

⚠️ **Important**: The debug configuration is for development only. Never use this in production as it exposes debugging capabilities and may have security implications. 