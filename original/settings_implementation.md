# DRRR Bot Android App 设置页面功能实现

## 1. 设置数据模型

### 1.1 SettingsData 数据类
```kotlin
data class SettingsData(
    // 账户设置
    val cookie: String = "",
    val roomId: String = "",
    val adminName: String = "52Hertz",
    
    // AI设置
    val aiEnabled: Boolean = false,
    val aiModel: String = "V3",
    val aiManageEnabled: Boolean = true,
    
    // 音乐设置
    val autoPlayEnabled: Boolean = false,
    val autoPlayInterval: Int = 5, // 分钟
    val hangRoomEnabled: Boolean = true,
    val hangRoomInterval: Int = 20, // 分钟
    
    // 通知设置
    val messageNotifications: Boolean = true,
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    
    // 高级设置
    val heartbeatInterval: Int = 60, // 秒
    val requestTimeout: Int = 30, // 秒
    val messageLimit: Int = 5, // 条/分钟
    val repeatLimit: Int = 3 // 次
)
```

## 2. 数据存储实现

### 2.1 SharedPreferencesHelper
```kotlin
class SharedPreferencesHelper private constructor(context: Context) {
    private val prefs = context.getSharedPreferences("drrr_bot_settings", Context.MODE_PRIVATE)
    
    companion object {
        @Volatile
        private var INSTANCE: SharedPreferencesHelper? = null
        
        fun getInstance(context: Context): SharedPreferencesHelper {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: SharedPreferencesHelper(context).also { INSTANCE = it }
            }
        }
    }
    
    // 保存设置
    fun saveSettings(settings: SettingsData) {
        with(prefs.edit()) {
            putString("cookie", settings.cookie)
            putString("roomId", settings.roomId)
            putString("adminName", settings.adminName)
            putBoolean("aiEnabled", settings.aiEnabled)
            putString("aiModel", settings.aiModel)
            putBoolean("aiManageEnabled", settings.aiManageEnabled)
            putBoolean("autoPlayEnabled", settings.autoPlayEnabled)
            putInt("autoPlayInterval", settings.autoPlayInterval)
            putBoolean("hangRoomEnabled", settings.hangRoomEnabled)
            putInt("hangRoomInterval", settings.hangRoomInterval)
            putBoolean("messageNotifications", settings.messageNotifications)
            putBoolean("soundEnabled", settings.soundEnabled)
            putBoolean("vibrationEnabled", settings.vibrationEnabled)
            putInt("heartbeatInterval", settings.heartbeatInterval)
            putInt("requestTimeout", settings.requestTimeout)
            putInt("messageLimit", settings.messageLimit)
            putInt("repeatLimit", settings.repeatLimit)
            apply()
        }
    }
    
    // 加载设置
    fun loadSettings(): SettingsData {
        return SettingsData(
            cookie = prefs.getString("cookie", "") ?: "",
            roomId = prefs.getString("roomId", "") ?: "",
            adminName = prefs.getString("adminName", "52Hertz") ?: "52Hertz",
            aiEnabled = prefs.getBoolean("aiEnabled", false),
            aiModel = prefs.getString("aiModel", "V3") ?: "V3",
            aiManageEnabled = prefs.getBoolean("aiManageEnabled", true),
            autoPlayEnabled = prefs.getBoolean("autoPlayEnabled", false),
            autoPlayInterval = prefs.getInt("autoPlayInterval", 5),
            hangRoomEnabled = prefs.getBoolean("hangRoomEnabled", true),
            hangRoomInterval = prefs.getInt("hangRoomInterval", 20),
            messageNotifications = prefs.getBoolean("messageNotifications", true),
            soundEnabled = prefs.getBoolean("soundEnabled", true),
            vibrationEnabled = prefs.getBoolean("vibrationEnabled", true),
            heartbeatInterval = prefs.getInt("heartbeatInterval", 60),
            requestTimeout = prefs.getInt("requestTimeout", 30),
            messageLimit = prefs.getInt("messageLimit", 5),
            repeatLimit = prefs.getInt("repeatLimit", 3)
        )
    }
    
    // 重置为默认设置
    fun resetToDefaults() {
        with(prefs.edit()) {
            clear()
            apply()
        }
    }
}
```

## 3. ViewModel实现

### 3.1 SettingsViewModel
```kotlin
class SettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val settingsHelper = SharedPreferencesHelper.getInstance(application)
    
    private val _settings = MutableLiveData<SettingsData>()
    val settings: LiveData<SettingsData> = _settings
    
    private val _saveStatus = MutableLiveData<SaveStatus>()
    val saveStatus: LiveData<SaveStatus> = _saveStatus
    
    init {
        loadSettings()
    }
    
    fun loadSettings() {
        viewModelScope.launch(Dispatchers.IO) {
            val loadedSettings = settingsHelper.loadSettings()
            _settings.postValue(loadedSettings)
        }
    }
    
    fun updateSettings(newSettings: SettingsData) {
        _settings.value = newSettings
    }
    
    fun saveSettings() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                settingsHelper.saveSettings(_settings.value ?: SettingsData())
                _saveStatus.postValue(SaveStatus.Success)
            } catch (e: Exception) {
                _saveStatus.postValue(SaveStatus.Error(e.message ?: "保存失败"))
            }
        }
    }
    
    fun resetToDefaults() {
        viewModelScope.launch(Dispatchers.IO) {
            settingsHelper.resetToDefaults()
            loadSettings()
            _saveStatus.postValue(SaveStatus.Reset)
        }
    }
    
    sealed class SaveStatus {
        object Success : SaveStatus()
        object Reset : SaveStatus()
        data class Error(val message: String) : SaveStatus()
    }
}
```

## 4. UI组件实现 (Jetpack Compose)

### 4.1 设置页面主界面
```kotlin
@Composable
fun SettingsScreen(viewModel: SettingsViewModel = viewModel()) {
    val settings by viewModel.settings.observeAsState(SettingsData())
    val saveStatus by viewModel.saveStatus.observeAsState()
    
    // 处理保存状态
    when (saveStatus) {
        is SettingsViewModel.SaveStatus.Success -> {
            // 显示保存成功提示
            Toast.makeText(LocalContext.current, "设置已保存", Toast.LENGTH_SHORT).show()
        }
        is SettingsViewModel.SaveStatus.Error -> {
            // 显示保存错误提示
            val message = (saveStatus as SettingsViewModel.SaveStatus.Error).message
            Toast.makeText(LocalContext.current, "保存失败: $message", Toast.LENGTH_LONG).show()
        }
        is SettingsViewModel.SaveStatus.Reset -> {
            // 显示重置成功提示
            Toast.makeText(LocalContext.current, "已重置为默认设置", Toast.LENGTH_SHORT).show()
        }
        else -> {}
    }
    
    Scaffold(
        topBar = {
            SettingsTopBar(
                onSaveClick = { viewModel.saveSettings() }
            )
        },
        floatingActionButton = {
            SaveFloatingActionButton(
                onClick = { viewModel.saveSettings() }
            )
        }
    ) { padding ->
        SettingsContent(
            settings = settings,
            onSettingsChange = { viewModel.updateSettings(it) },
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
        )
    }
}
```

### 4.2 顶部AppBar
```kotlin
@Composable
fun SettingsTopBar(onSaveClick: () -> Unit) {
    TopAppBar(
        title = { Text("设置") },
        actions = {
            IconButton(onClick = onSaveClick) {
                Icon(
                    imageVector = Icons.Default.Save,
                    contentDescription = "保存"
                )
            }
        },
        backgroundColor = MaterialTheme.colors.primary,
        contentColor = MaterialTheme.colors.onPrimary
    )
}
```

### 4.3 保存浮动按钮
```kotlin
@Composable
fun SaveFloatingActionButton(onClick: () -> Unit) {
    FloatingActionButton(
        onClick = onClick,
        backgroundColor = MaterialTheme.colors.primary,
        contentColor = MaterialTheme.colors.onPrimary
    ) {
        Icon(
            imageVector = Icons.Default.Save,
            contentDescription = "保存设置"
        )
    }
}
```

### 4.4 设置内容布局
```kotlin
@Composable
fun SettingsContent(
    settings: SettingsData,
    onSettingsChange: (SettingsData) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp)
    ) {
        // 账户设置组
        item {
            SettingsGroup(
                title = "账户设置",
                content = {
                    CookieSetting(
                        value = settings.cookie,
                        onValueChange = { onSettingsChange(settings.copy(cookie = it)) }
                    )
                    RoomIdSetting(
                        value = settings.roomId,
                        onValueChange = { onSettingsChange(settings.copy(roomId = it)) }
                    )
                    AdminNameSetting(
                        value = settings.adminName,
                        onValueChange = { onSettingsChange(settings.copy(adminName = it)) }
                    )
                }
            )
        }
        
        // AI设置组
        item {
            SettingsGroup(
                title = "AI设置",
                content = {
                    AiEnabledSetting(
                        value = settings.aiEnabled,
                        onValueChange = { onSettingsChange(settings.copy(aiEnabled = it)) }
                    )
                    AiModelSetting(
                        value = settings.aiModel,
                        onValueChange = { onSettingsChange(settings.copy(aiModel = it)) }
                    )
                    AiManageEnabledSetting(
                        value = settings.aiManageEnabled,
                        onValueChange = { onSettingsChange(settings.copy(aiManageEnabled = it)) }
                    )
                }
            )
        }
        
        // 音乐设置组
        item {
            SettingsGroup(
                title = "音乐设置",
                content = {
                    AutoPlayEnabledSetting(
                        value = settings.autoPlayEnabled,
                        onValueChange = { onSettingsChange(settings.copy(autoPlayEnabled = it)) }
                    )
                    AutoPlayIntervalSetting(
                        value = settings.autoPlayInterval,
                        onValueChange = { onSettingsChange(settings.copy(autoPlayInterval = it)) }
                    )
                    HangRoomEnabledSetting(
                        value = settings.hangRoomEnabled,
                        onValueChange = { onSettingsChange(settings.copy(hangRoomEnabled = it)) }
                    )
                    HangRoomIntervalSetting(
                        value = settings.hangRoomInterval,
                        onValueChange = { onSettingsChange(settings.copy(hangRoomInterval = it)) }
                    )
                }
            )
        }
        
        // 通知设置组
        item {
            SettingsGroup(
                title = "通知设置",
                content = {
                    MessageNotificationsSetting(
                        value = settings.messageNotifications,
                        onValueChange = { onSettingsChange(settings.copy(messageNotifications = it)) }
                    )
                    SoundEnabledSetting(
                        value = settings.soundEnabled,
                        onValueChange = { onSettingsChange(settings.copy(soundEnabled = it)) }
                    )
                    VibrationEnabledSetting(
                        value = settings.vibrationEnabled,
                        onValueChange = { onSettingsChange(settings.copy(vibrationEnabled = it)) }
                    )
                }
            )
        }
        
        // 高级设置组
        item {
            SettingsGroup(
                title = "高级设置",
                content = {
                    HeartbeatIntervalSetting(
                        value = settings.heartbeatInterval,
                        onValueChange = { onSettingsChange(settings.copy(heartbeatInterval = it)) }
                    )
                    RequestTimeoutSetting(
                        value = settings.requestTimeout,
                        onValueChange = { onSettingsChange(settings.copy(requestTimeout = it)) }
                    )
                    MessageLimitSetting(
                        value = settings.messageLimit,
                        onValueChange = { onSettingsChange(settings.copy(messageLimit = it)) }
                    )
                    RepeatLimitSetting(
                        value = settings.repeatLimit,
                        onValueChange = { onSettingsChange(settings.copy(repeatLimit = it)) }
                    )
                }
            )
        }
        
        // 重置按钮
        item {
            ResetToDefaultsButton(
                onResetClick = { /* 需要通过ViewModel处理 */ }
            )
        }
    }
}
```

### 4.5 设置组容器
```kotlin
@Composable
fun SettingsGroup(
    title: String,
    content: @Composable () -> Unit
) {
    var expanded by remember { mutableStateOf(true) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        elevation = 2.dp,
        shape = RoundedCornerShape(8.dp)
    ) {
        Column {
            // 组标题（可点击展开/收起）
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { expanded = !expanded }
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.h6,
                    modifier = Modifier.weight(1f)
                )
                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (expanded) "收起" else "展开"
                )
            }
            
            // 组内容（根据展开状态显示/隐藏）
            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Divider()
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    content()
                }
            }
        }
    }
}
```

### 4.6 各种设置项组件示例

#### Cookie设置项
```kotlin
@Composable
fun CookieSetting(
    value: String,
    onValueChange: (String) -> Unit
) {
    var passwordVisible by remember { mutableStateOf(false) }
    
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Cookie") },
        placeholder = { Text("请输入Cookie字符串") },
        leadingIcon = {
            Icon(
                imageVector = Icons.Default.Lock,
                contentDescription = "Cookie"
            )
        },
        trailingIcon = {
            IconButton(onClick = { passwordVisible = !passwordVisible }) {
                Icon(
                    imageVector = if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                    contentDescription = if (passwordVisible) "隐藏" else "显示"
                )
            }
        },
        visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
        modifier = Modifier.fillMaxWidth()
    )
}
```

#### Switch设置项
```kotlin
@Composable
fun SwitchSetting(
    title: String,
    description: String,
    value: Boolean,
    onValueChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(
            modifier = Modifier.weight(1f)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.body1
            )
            Text(
                text = description,
                style = MaterialTheme.typography.caption,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.6f)
            )
        }
        Switch(
            checked = value,
            onCheckedChange = onValueChange
        )
    }
}
```

#### Slider设置项
```kotlin
@Composable
fun SliderSetting(
    title: String,
    value: Int,
    onValueChange: (Int) -> Unit,
    valueRange: IntRange,
    unit: String
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.body1
            )
            Text(
                text = "$value $unit",
                style = MaterialTheme.typography.body2,
                color = MaterialTheme.colors.primary
            )
        }
        Slider(
            value = value.toFloat(),
            onValueChange = { onValueChange(it.toInt()) },
            valueRange = valueRange.first.toFloat()..valueRange.last.toFloat(),
            steps = valueRange.last - valueRange.first - 1,
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

## 5. 动画实现

### 5.1 页面切换动画
```kotlin
// 在Navigation中使用
fun navBuilder() {
    composable(
        "settings",
        enterTransition = {
            slideInHorizontally(
                initialOffsetX = { it },
                animationSpec = tween(300, easing = FastOutSlowInEasing)
            )
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it },
                animationSpec = tween(300, easing = FastOutSlowInEasing)
            )
        }
    ) {
        SettingsScreen()
    }
}
```

### 5.2 Switch切换动画
```kotlin
@Composable
fun AnimatedSwitch(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Switch(
        checked = checked,
        onCheckedChange = onCheckedChange,
        modifier = Modifier.animateContentSize(
            animationSpec = tween(150, easing = FastOutSlowInEasing)
        )
    )
}
```

## 6. 数据验证

### 6.1 输入验证函数
```kotlin
class SettingsValidator {
    fun validateCookie(cookie: String): Boolean {
        return cookie.contains("drrr-session-1=") && cookie.contains("_ga=")
    }
    
    fun validateRoomId(roomId: String): Boolean {
        return roomId.isNotEmpty() && roomId.length >= 6
    }
    
    fun validateAdminName(name: String): Boolean {
        return name.isNotEmpty() && name.length <= 20
    }
    
    fun validateInterval(value: Int, min: Int, max: Int): Boolean {
        return value in min..max
    }
}
```

## 7. 错误处理和用户反馈

### 7.1 错误提示组件
```kotlin
@Composable
fun ErrorText(
    text: String,
    modifier: Modifier = Modifier
) {
    Text(
        text = text,
        color = MaterialTheme.colors.error,
        style = MaterialTheme.typography.caption,
        modifier = modifier
    )
}
```

## 8. 主题和样式

### 8.1 自定义主题
```kotlin
@Composable
fun DRRRBotTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) {
        DarkColorScheme
    } else {
        LightColorScheme
    }
    
    MaterialTheme(
        colors = colors,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}
```