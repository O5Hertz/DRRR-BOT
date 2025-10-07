# DRRR Bot Android应用手动构建指南

由于自动化构建存在问题，您可以按照以下步骤在本地手动构建APK文件。

## 前提条件

1. 安装Java Development Kit (JDK) 8或更高版本
2. 安装Android SDK
3. 安装Gradle构建工具

## 构建步骤

### 1. 克隆仓库
```bash
git clone https://github.com/O5Hertz/DRRR-BOT.git
cd DRRR-BOT
```

### 2. 安装Android SDK组件
确保您已安装以下组件：
- Android SDK Platform 30
- Android Build-Tools 30.0.3

### 3. 配置环境变量
设置以下环境变量：
```bash
export ANDROID_HOME=/path/to/android/sdk
export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH
```

### 4. 构建APK
进入简化版Android项目目录并构建：
```bash
cd simple-android-app
gradle assembleDebug
```

构建完成的APK文件将位于：
```
simple-android-app/app/build/outputs/apk/debug/app-debug.apk
```

## 故障排除

如果遇到构建问题，请尝试以下解决方案：

1. 确保所有依赖项都已正确安装
2. 检查Android SDK路径是否正确配置
3. 确保有足够的磁盘空间和内存
4. 如果出现权限问题，请检查文件权限设置

## 联系支持

如果按照以上步骤仍然无法构建，请联系：ZX114516@outlook.com