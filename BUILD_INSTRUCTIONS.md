# DRRR Bot Android应用手动构建指南（更新版）

由于自动化构建存在问题，您可以按照以下步骤在本地手动构建APK文件。

## 方法一：使用Android Studio（推荐）

1. 下载并安装Android Studio
2. 打开Android Studio，选择"Open an existing Android Studio project"
3. 导航到DRRR-BOT/simple-android-app目录并打开
4. 等待项目同步完成
5. 点击"Build"菜单，选择"Build Bundle(s) / APK(s)"，然后选择"Build APK(s)"
6. 构建完成后，点击"locate"查看生成的APK文件

## 方法二：使用命令行工具

### 前提条件

1. 安装Java Development Kit (JDK) 8或更高版本
2. 安装Android SDK命令行工具
3. 设置环境变量：
   ```bash
   export ANDROID_HOME=/path/to/android/sdk
   export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH
   ```

### 构建步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/O5Hertz/DRRR-BOT.git
   cd DRRR-BOT
   ```

2. 安装Android SDK组件：
   ```bash
   sdkmanager "platforms;android-30" "build-tools;30.0.3"
   ```

3. 创建基本项目结构（如果尚未存在）：
   ```bash
   mkdir -p simple-android-app/app/src/main/{java/com/drrr/bot/simple,res/values,res/drawable}
   ```

4. 编译Java源代码：
   ```bash
   cd simple-android-app
   mkdir -p app/build/intermediates/javac/debug/classes
   javac -source 8 -target 8 -bootclasspath $ANDROID_HOME/platforms/android-30/android.jar -classpath app/build/intermediates/javac/debug/classes -d app/build/intermediates/javac/debug/classes app/src/main/java/com/drrr/bot/simple/*.java
   ```

5. 创建资源包：
   ```bash
   mkdir -p app/build/intermediates/res/merged/debug
   cp -r app/src/main/res/* app/build/intermediates/res/merged/debug/
   aapt package -f -m -J app/src/main/java -M app/src/main/AndroidManifest.xml -S app/src/main/res -I $ANDROID_HOME/platforms/android-30/android.jar
   ```

6. 创建未签名的APK：
   ```bash
   mkdir -p app/build/outputs/apk/debug
   aapt package -f -M app/src/main/AndroidManifest.xml -S app/src/main/res -I $ANDROID_HOME/platforms/android-30/android.jar -F app/build/outputs/apk/debug/app-debug-unaligned.apk app/build/intermediates/javac/debug/classes
   ```

7. 添加编译后的类文件到APK：
   ```bash
   cd app/build/intermediates/javac/debug/classes
   jar uf ../../../../outputs/apk/debug/app-debug-unaligned.apk .
   ```

8. 创建密钥库（如果尚未存在）：
   ```bash
   keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000
   ```

9. 签名APK：
   ```bash
   jarsigner -verbose -keystore debug.keystore -storepass android -keypass android -digestalg SHA1 -sigalg MD5withRSA app/build/outputs/apk/debug/app-debug-unaligned.apk androiddebugkey
   ```

10. 优化APK：
    ```bash
    zipalign -v 4 app/build/outputs/apk/debug/app-debug-unaligned.apk app/build/outputs/apk/debug/app-debug.apk
    ```

## 故障排除

如果遇到构建问题，请尝试以下解决方案：

1. 确保所有依赖项都已正确安装
2. 检查Android SDK路径是否正确配置
3. 确保有足够的磁盘空间和内存
4. 如果出现权限问题，请检查文件权限设置
5. 确保使用的JDK版本与Android SDK兼容

## 联系支持

如果按照以上步骤仍然无法构建，请联系：ZX114516@outlook.com