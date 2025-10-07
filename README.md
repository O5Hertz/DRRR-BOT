# DRRR Chat Room Bot for Android

## Overview

The DRRR Chat Room Bot is an advanced Android application designed for the DRRR (Dollars Chat Room) platform. This bot provides automated chat responses, music playback capabilities, room management features, and event handling to enhance the chat room experience.

## Features

### Core Functionality
- **Automated Chat Responses**: Intelligent bot responses to user messages
- **Music Playback System**: Integrated music player with playlist management
- **Room Management**: Comprehensive tools for room administration
- **Event Handling**: Real-time event processing and response

### Administrative Features
- **User Management**: Kick, ban, and unban users
- **Access Control**: Admin-only command execution
- **Whitelist/Blacklist**: Fine-grained user access control
- **Room Settings**: Configurable room parameters

### Music System
- **Playlist Management**: Add, remove, and organize songs
- **Multiple Music Sources**: Support for various music platforms
- **Text-to-Speech**: Convert text messages to audio
- **Playback Controls**: Play, pause, next, and clear functions

## Architecture

### Core Components
1. **DRRRBotCore**: Main bot controller managing overall operation
2. **CommandHandler**: Processes user commands and executes appropriate actions
3. **RoomManager**: Handles room administration and user management
4. **MusicPlayer**: Manages music playback and playlist functionality
5. **EventHandler**: Processes chat events and triggers responses
6. **DRRRClient**: Handles communication with the DRRR chat server

### Project Structure
```
DRRRBotAndroidApp/
├── app/                           # Main application module
│   ├── src/                       # Source code
│   │   ├── main/                  # Main source set
│   │   │   ├── java/com/drrr/bot/ # Java source files
│   │   │   │   ├── DRRRBotCore.java     # Main bot controller
│   │   │   │   ├── CommandHandler.java  # Command processing
│   │   │   │   ├── RoomManager.java     # Room administration
│   │   │   │   ├── MusicPlayer.java     # Music playback system
│   │   │   │   ├── EventHandler.java    # Event processing
│   │   │   │   ├── DRRRClient.java      # Server communication
│   │   │   │   ├── BotService.java      # Background service
│   │   │   │   ├── MainActivity.java    # Main activity
│   │   │   │   └── DRRRBotApplication.java # Application class
│   │   │   ├── res/               # Resource files
│   │   │   └── AndroidManifest.xml # Application manifest
├── build.xml                      # Ant build configuration
├── project.properties             # Project properties
└── README.md                      # This document
```

## Installation

### Prerequisites
- Android SDK
- JDK 8 or higher
- Apache Ant

### Building from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/O5Hertz/DRRR-BOT.git
   cd DRRR-BOT
   ```

2. Set up the Android SDK path in `local.properties`:
   ```properties
   sdk.dir=/path/to/android/sdk
   ```

3. Build the APK using Ant:
   ```bash
   ant debug
   ```

4. The built APK will be located at `bin/DRRRBotAndroidApp-debug.apk`

### GitHub Actions
This repository uses GitHub Actions for automated building. Every push to the main branch triggers a build workflow that:
1. Sets up the required environment
2. Builds the APK using Ant
3. Uploads the built APK as an artifact

## Usage

### Starting the Bot
1. Install the APK on an Android device
2. Launch the application
3. The bot will automatically start and connect to the DRRR chat room

### Command Reference

#### Administrative Commands (Admin-only)
- `/ai [on|off]` - Enable/disable AI functionality
- `/hang [on|off]` - Enable/disable room hanging
- `/kick <username>` - Kick a user from the room
- `/ban <username>` - Ban a user from the room
- `/unban <username>` - Unban a user
- `/help` - Display help information

#### Music Commands
- `/play <song_name> <url>` - Add a song to the playlist
- `/netmusic <song_name>` - Search NetEase Music
- `/qqmusic <song_name>` - Search QQ Music
- `/tts <text>` - Convert text to speech
- `/next` - Play the next song
- `/playlist` - Display current playlist
- `/clear` - Clear the playlist

## Configuration

### Admin Management
The bot recognizes users with the tripcode "52Hertz" as administrators by default. Additional administrators can be added through the RoomManager API.

### Room Settings
- **Direct Messages**: Enable/disable DMs (default: enabled)
- **Music System**: Enable/disable music playback (default: enabled)
- **User Limits**: Set maximum room capacity (default: unlimited)

## Development

### Code Structure
The bot follows a modular architecture with clearly separated concerns:
- **Core Module**: Main bot logic and state management
- **Command Module**: User command processing and execution
- **Room Module**: Room administration and user management
- **Music Module**: Music playback and playlist management
- **Network Module**: Server communication and event handling

### Building with Android Studio
1. Open the project in Android Studio
2. Sync the project with Gradle files
3. Build and run the application

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## Troubleshooting

### Common Issues
1. **Build Failures**: Ensure the Android SDK path is correctly set in `local.properties`
2. **Connection Issues**: Verify network connectivity and server availability
3. **Command Errors**: Check that the user has appropriate permissions

### Logs
Application logs can be viewed using Android Debug Bridge (ADB):
```bash
adb logcat -s DRRRBotCore CommandHandler RoomManager MusicPlayer
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- DRRR chat room community
- Android development community
- Open source libraries and tools