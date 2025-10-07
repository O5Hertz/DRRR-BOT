# DRRR Chat Room Bot

This repository contains two versions of the DRRR Chat Room Bot:

1. **Android Version** - An Android application implementation
2. **Original Version** - The original Python implementation

## Android Version

### Overview

The DRRR Chat Room Bot is an Android application designed for the DRRR (Dollars Chat Room) platform. This bot provides automated chat responses, room management features, and event handling.

**Notice**: This Android version is currently in testing phase as of 2025.10.7. Functionality may be limited and stability is not guaranteed.

### Features

#### Core Functionality
- **Automated Chat Responses**: Bot responses to user messages
- **Room Management**: Tools for room administration
- **Event Handling**: Event processing and response

#### Administrative Features
- **User Management**: Kick, ban, and unban users
- **Access Control**: Admin-only command execution
- **Whitelist/Blacklist**: User access control
- **Room Settings**: Configurable room parameters

#### AI Functionality
The AI functionality uses a third-party API service from an external website, not an official API. This feature:
- Relies on external API services for generating responses
- May have usage limitations or costs associated with the third-party service
- Is subject to the terms of service of the third-party API provider
- May experience downtime or performance issues based on the third-party service

Users should be aware that this functionality depends on external services and may not always be available or consistent.

#### DRRR Chat Room Interaction
The bot interacts with the DRRR chat room through web scraping techniques, not an official API. This approach:
- May be affected by changes to the DRRR website structure
- May not comply with the terms of service of the DRRR chat room
- May experience connectivity issues or blocking by the DRRR server
- Requires maintaining session cookies and mimicking browser behavior

Users should be aware of these limitations and potential issues when using this bot.

#### Music System (DEPRECATED)
The music playback system is currently non-functional and has been deprecated. The following features are not working:
- Playlist Management
- Multiple Music Sources
- Text-to-Speech
- Playback Controls

This functionality was part of the original design but is no longer maintained or operational. Users should not expect these commands to work.

### Architecture

#### Core Components
1. **DRRRBotCore**: Main bot controller managing overall operation
2. **CommandHandler**: Processes user commands and executes appropriate actions
3. **RoomManager**: Handles room administration and user management
4. **EventHandler**: Processes chat events and triggers responses
5. **DRRRClient**: Handles communication with the DRRR chat server

#### Project Structure
```
DRRR-BOT/
├── app/                           # Main application module
│   ├── src/                       # Source code
│   │   ├── main/                  # Main source set
│   │   │   ├── java/com/drrr/bot/ # Java source files
│   │   │   │   ├── DRRRBotCore.java     # Main bot controller
│   │   │   │   ├── CommandHandler.java  # Command processing
│   │   │   │   ├── RoomManager.java     # Room administration
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

### Installation

#### Prerequisites
- Android SDK
- JDK 8 or higher
- Apache Ant

#### Building from Source
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

4. The built APK will be located at `bin/DRRR-BOT-debug.apk`

#### GitHub Actions
This repository uses GitHub Actions for automated building. Every push to the main branch triggers a build workflow that:
1. Sets up the required environment (JDK 17, Android SDK)
2. Builds the APK using Gradle (preferred) or Ant
3. Uploads the built APK as an artifact

There are two build workflows available:
1. `build.yml` - Uses Ant build system
2. `build-gradle.yml` - Uses Gradle build system (recommended)

The Gradle build process may take several minutes to complete. If the build fails, check the GitHub Actions logs for detailed error information.

### Usage

#### Starting the Bot
1. Install the APK on an Android device
2. Launch the application
3. The bot will automatically start and connect to the DRRR chat room

#### Command Reference

##### Administrative Commands (Admin-only)
- `/ai [on|off]` - Enable/disable AI functionality (uses third-party API)
- `/hang [on|off]` - Enable/disable room hanging
- `/kick <username>` - Kick a user from the room
- `/ban <username>` - Ban a user from the room
- `/unban <username>` - Unban a user
- `/help` - Display help information

##### Music Commands (DEPRECATED)
All music-related commands are currently non-functional:
- `/play <song_name> <url>` - Add a song to the playlist
- `/netmusic <song_name>` - Search NetEase Music
- `/qqmusic <song_name>` - Search QQ Music
- `/tts <text>` - Convert text to speech
- `/next` - Play the next song
- `/playlist` - Display current playlist
- `/clear` - Clear the playlist

### Configuration

#### Admin Management
The bot recognizes users with the tripcode "52Hertz" as administrators by default. Additional administrators can be added through the RoomManager API.

#### Room Settings
- **Direct Messages**: Enable/disable DMs (default: enabled)
- **User Limits**: Set maximum room capacity (default: unlimited)

### Development

#### Code Structure
The bot follows a modular architecture with clearly separated concerns:
- **Core Module**: Main bot logic and state management
- **Command Module**: User command processing and execution
- **Room Module**: Room administration and user management
- **Network Module**: Server communication and event handling

#### Building with Android Studio
1. Open the project in Android Studio
2. Sync the project with Gradle files
3. Build and run the application

#### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

### Troubleshooting

#### Common Issues
1. **Build Failures**: Ensure the Android SDK path is correctly set in `local.properties`
2. **Connection Issues**: Verify network connectivity and server availability
3. **Command Errors**: Check that the user has appropriate permissions
4. **AI Functionality Issues**: Verify third-party API service availability and configuration
5. **DRRR Connection Issues**: Verify DRRR website availability and cookie settings

#### General Support
Some features may have bugs or issues, or may not work as expected. If you encounter such problems:
1. First, check your environment and configuration files
2. If problems persist, please contact: ZX114516@outlook.com

#### Logs
Application logs can be viewed using Android Debug Bridge (ADB):
```bash
adb logcat -s DRRRBotCore CommandHandler RoomManager
```

#### License
This project is licensed under the MIT License - see the LICENSE file for details.

#### Acknowledgments
- DRRR chat room community
- Android development community
- Open source libraries and tools
- Third-party API providers

## Original Version

### Overview

DRRR聊天室机器人是一个AI机器人，具有用户欢迎、指令权限控制、AI对话和音乐点播功能。

### Features

- AI机器人，具有用户欢迎、指令权限控制、AI对话和音乐点播功能
- 管理员"52Hertz"可以执行管理命令
- 支持AI对话功能，通过指定API进行智能对话
- 音乐点播功能，支持添加、播放和管理音乐播放列表
- 所有命令以"/"开头
- 智能监控系统：监控机器人状态并进行决策
- 维持矩阵系统：分布式监控，确保机器人稳定运行
- QQ音乐搜索：支持搜索QQ音乐并输出链接
- 文本转语音：支持将文本转换为语音并输出链接

### Project Structure

```
drrr_bot_standalone_drrr机器人/
├── api/                     # API模块
├── modules/                 # 功能模块
├── success_versions/        # 成功版本备份
├── utils/                   # 工具模块
├── enhanced_ai_bot.py       # 增强版AI机器人主程序
├── bot_user_manual.md       # 用户手册
├── bot_ctl.sh               # 便捷启动脚本
├── bot-ctl                  # 便捷控制脚本
├── drrr_browser_proxy.js    # 浏览器代理脚本
├── unified_launcher.py      # 统一启动程序
├── matrix_node.py           # 维持矩阵节点
├── start_matrix.sh          # 启动矩阵系统
├── stop_matrix.sh           # 停止矩阵系统
├── enhanced_monitor.sh      # 增强监控脚本
├── requirements.txt         # 依赖包列表
└── README.md                # 本文件
```

### Dependencies

- requests>=2.25.1
- aiohttp>=3.7.4
- websockets>=9.1

### Unified Management

```bash
# 启动完整系统
bash bot_ctl.sh start

# 停止完整系统
bash bot_ctl.sh stop

# 重启完整系统
bash bot_ctl.sh restart

# 查看系统状态
bash bot_ctl.sh status
```

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