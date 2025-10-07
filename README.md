# DRRR Chat Room Bot

This repository contains two versions of the DRRR Chat Room Bot:

1. **Android Version** - An Android application implementation
2. **Original Version** - The original Python implementation

## Android Version

The Android version is located in the `android/` directory. Please refer to [android/README.md](android/README.md) for details on building and using the Android application.

## Original Version

The original Python version is located in the `original/` directory. Please refer to [original/README.md](original/README.md) for details on setting up and running the Python bot.

## Repository Structure

```
DRRR-BOT/
├── android/           # Android application version
│   ├── app/           # Android application source code
│   ├── build.xml      # Ant build configuration
│   ├── project.properties # Project properties
│   ├── local.properties   # Local properties (SDK path)
│   └── README.md      # Android version documentation
├── original/          # Original Python implementation
│   ├── api/           # API modules
│   ├── modules/       # Bot modules
│   ├── utils/         # Utility modules
│   ├── success_versions/ # Successful versions backup
│   ├── enhanced_ai_bot.py # Main bot script
│   ├── requirements.txt   # Python dependencies
│   ├── login_config.json  # Login configuration (empty template)
│   ├── matrix_config.json # Matrix configuration (empty template)
│   └── README.md      # Original version documentation
```

## Configuration

Both versions come with empty configuration templates. You need to fill in your own configuration values before using the bots.

For the original Python version, you need to update:
- `original/login_config.json` - With your DRRR session cookie and room information
- `original/matrix_config.json` - With your bot directory and node configuration

For the Android version, you need to update:
- `android/local.properties` - With your Android SDK path

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you encounter any issues with either version, please check your environment and configuration files first. If problems persist, please contact: ZX114516@outlook.com