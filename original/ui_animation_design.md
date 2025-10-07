# DRRR Bot Android 高级UI动画和细节优化

## 1. 动画框架设计

### 1.1 动画系统架构
- 使用Android原生动画API实现所有动画效果
- 封装通用动画组件，提高复用性
- 实现动画协调器，管理复杂动画序列
- 支持动画性能监控和优化

### 1.2 动画类型分类
- 视图动画(View Animation): 位置、大小、透明度变化
- 属性动画(Property Animation): 更灵活的属性变化动画
- 转场动画(Transition Animation): 页面和状态切换动画
- 可绘制动画(Drawable Animation): 帧动画效果

## 2. 页面切换动画

### 2.1 导航转场动画
```kotlin
// 进入动画
fun enterTransition(): EnterTransition {
    return fadeIn(
        animationSpec = tween(
            durationMillis = 300,
            easing = FastOutSlowInEasing
        )
    ) + slideInHorizontally(
        initialOffsetX = { it },
        animationSpec = tween(
            durationMillis = 300,
            easing = FastOutSlowInEasing
        )
    )
}

// 退出动画
fun exitTransition(): ExitTransition {
    return fadeOut(
        animationSpec = tween(
            durationMillis = 300,
            easing = FastOutSlowInEasing
        )
    ) + slideOutHorizontally(
        targetOffsetX = { -it },
        animationSpec = tween(
            durationMillis = 300,
            easing = FastOutSlowInEasing
        )
    )
}
```

### 2.2 共享元素转场
```kotlin
// 在Compose中实现共享元素转场
@Composable
fun SharedElementTransition() {
    val transition = updateTransition(currentScreen, label = "Screen Transition")
    
    // 共享元素
    transition.AnimatedContent(
        transitionSpec = {
            when (targetState) {
                Screen.List -> {
                    slideInVertically { -it } togetherWith slideOutVertically { it }
                }
                Screen.Detail -> {
                    slideInVertically { it } togetherWith slideOutVertically { -it }
                }
            }
        }
    ) { screen ->
        when (screen) {
            Screen.List -> MessageListScreen()
            Screen.Detail -> MessageDetailScreen()
        }
    }
}
```

## 3. 交互反馈动画

### 3.1 按钮点击效果
```kotlin
@Composable
fun AnimatedButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    content: @Composable RowScope.() -> Unit
) {
    var isPressed by remember { mutableStateOf(false) }
    
    Button(
        onClick = onClick,
        modifier = modifier
            .scale(if (isPressed) 0.95f else 1f)
            .onPress { isPressed = it },
        content = content
    )
}

// 自定义按下状态处理
@Composable
fun Modifier.onPress(onPress: (Boolean) -> Unit): Modifier {
    return this.pointerInput(Unit) {
        detectTapGestures(
            onPress = {
                onPress(true)
                tryAwaitRelease()
                onPress(false)
            }
        )
    }
}
```

### 3.2 列表项动画
```kotlin
@Composable
fun AnimatedMessageList(messages: List<Message>) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        items(
            items = messages,
            key = { it.id }
        ) { message ->
            AnimatedMessageItem(message)
        }
    }
}

@Composable
fun AnimatedMessageItem(message: Message) {
    val animationState = remember { MutableTransitionState(false) }
        .apply { targetState = true }
    
    AnimatedVisibility(
        visibleState = animationState,
        enter = fadeIn() + slideInVertically(),
        exit = fadeOut() + slideOutVertically()
    ) {
        MessageCard(message)
    }
}
```

### 3.3 下拉刷新动画
```kotlin
@Composable
fun AnimatedPullToRefresh(
    refreshing: Boolean,
    onRefresh: () -> Unit,
    content: @Composable () -> Unit
) {
    val pullRefreshState = rememberPullRefreshState(refreshing, onRefresh)
    
    Box(
        modifier = Modifier.pullRefresh(pullRefreshState)
    ) {
        content()
        
        PullRefreshIndicator(
            refreshing = refreshing,
            state = pullRefreshState,
            modifier = Modifier.align(Alignment.TopCenter)
        )
    }
}
```

## 4. 设置页面动画

### 4.1 设置组展开/收起动画
```kotlin
@Composable
fun AnimatedSettingsGroup(
    title: String,
    content: @Composable () -> Unit
) {
    var expanded by remember { mutableStateOf(true) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        elevation = 2.dp,
        shape = RoundedCornerShape(12.dp)
    ) {
        Column {
            // 组标题（带动画的展开/收起图标）
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
                
                // 旋转动画的展开/收起图标
                Icon(
                    imageVector = Icons.Default.ExpandMore,
                    contentDescription = if (expanded) "收起" else "展开",
                    modifier = Modifier.rotate(
                        if (expanded) 180f else 0f
                    )
                )
            }
            
            // 内容区域的展开/收起动画
            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn(
                    animationSpec = tween(200)
                ) + expandVertically(
                    animationSpec = tween(200)
                ),
                exit = fadeOut(
                    animationSpec = tween(200)
                ) + shrinkVertically(
                    animationSpec = tween(200)
                )
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

### 4.2 Switch切换动画
```kotlin
@Composable
fun AnimatedSwitch(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Switch(
        checked = checked,
        onCheckedChange = onCheckedChange,
        modifier = Modifier
            .animateContentSize(
                animationSpec = tween(150, easing = FastOutSlowInEasing)
            )
    )
}
```

### 4.3 Slider滑动动画
```kotlin
@Composable
fun AnimatedSlider(
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    steps: Int = 0
) {
    var isSliding by remember { mutableStateOf(false) }
    
    Slider(
        value = value,
        onValueChange = {
            isSliding = true
            onValueChange(it)
        },
        onValueChangeFinished = {
            isSliding = false
        },
        valueRange = valueRange,
        steps = steps,
        modifier = Modifier
            .fillMaxWidth()
            .animateContentSize(
                animationSpec = tween(100, easing = FastOutSlowInEasing)
            )
    )
}
```

## 5. 加载和进度动画

### 5.1 自定义加载指示器
```kotlin
@Composable
fun CustomLoadingIndicator() {
    val infiniteTransition = rememberInfiniteTransition()
    
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing)
        )
    )
    
    Icon(
        imageVector = Icons.Default.Refresh,
        contentDescription = "加载中",
        modifier = Modifier
            .size(48.dp)
            .rotate(rotation)
            .padding(8.dp),
        tint = MaterialTheme.colors.primary
    )
}
```

### 5.2 进度条动画
```kotlin
@Composable
fun AnimatedProgressBar(
    progress: Float,
    modifier: Modifier = Modifier
) {
    var currentProgress by remember { mutableStateOf(0f) }
    
    LaunchedEffect(progress) {
        animate(
            initialValue = currentProgress,
            targetValue = progress,
            animationSpec = tween(
                durationMillis = 500,
                easing = FastOutSlowInEasing
            )
        ) { value, _ ->
            currentProgress = value
        }
    }
    
    LinearProgressIndicator(
        progress = currentProgress,
        modifier = modifier
    )
}
```

## 6. 微交互动画

### 6.1 悬停效果
```kotlin
@Composable
fun HoverableCard(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    var isHovered by remember { mutableStateOf(false) }
    
    Card(
        modifier = modifier
            .onPointerEvent(PointerEventType.Enter) { isHovered = true }
            .onPointerEvent(PointerEventType.Exit) { isHovered = false }
            .scale(if (isHovered) 1.02f else 1f)
            .shadow(
                elevation = if (isHovered) 8.dp else 4.dp,
                shape = RoundedCornerShape(12.dp)
            )
            .clickable(onClick = onClick),
        elevation = if (isHovered) 8.dp else 4.dp,
        shape = RoundedCornerShape(12.dp)
    ) {
        content()
    }
}
```

### 6.2 输入框焦点动画
```kotlin
@Composable
fun AnimatedTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier
) {
    var isFocused by remember { mutableStateOf(false) }
    
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        modifier = modifier
            .onFocusChanged { isFocused = it.isFocused }
            .border(
                width = if (isFocused) 2.dp else 1.dp,
                color = if (isFocused) MaterialTheme.colors.primary else MaterialTheme.colors.onSurface.copy(alpha = 0.3f),
                shape = RoundedCornerShape(4.dp)
            )
    )
}
```

## 7. 主题切换动画

### 7.1 深色/浅色模式切换
```kotlin
@Composable
fun AnimatedThemeSwitch(
    isDarkTheme: Boolean,
    onThemeChange: (Boolean) -> Unit
) {
    val colors = if (isDarkTheme) {
        darkColors()
    } else {
        lightColors()
    }
    
    val transition = updateTransition(isDarkTheme, label = "Theme Transition")
    
    MaterialTheme(
        colors = transition.animateColor(
            transitionSpec = { tween(durationMillis = 300) },
            label = "BackgroundColor"
        ) { isDark ->
            if (isDark) DarkColors.background else LightColors.background
        }.value
    ) {
        // 应用内容
    }
}
```

## 8. 性能优化

### 8.1 动画性能监控
```kotlin
class AnimationPerformanceMonitor {
    private val frameMetrics = mutableListOf<Long>()
    private var frameCount = 0
    
    fun startMonitoring() {
        frameCount = 0
        frameMetrics.clear()
    }
    
    fun recordFrameDuration(duration: Long) {
        frameMetrics.add(duration)
        frameCount++
        
        // 每100帧计算一次平均帧时间
        if (frameCount % 100 == 0) {
            val averageFrameTime = frameMetrics.average()
            if (averageFrameTime > 16.67) { // 超过60fps
                // 记录性能警告
                Log.w("Animation", "Average frame time: ${averageFrameTime}ms, target: 16.67ms")
            }
        }
    }
}
```

### 8.2 动画优化策略
- 减少过度绘制
- 使用硬件加速
- 避免在动画中进行复杂计算
- 合理使用动画缓存
- 在低性能设备上降低动画复杂度

## 9. 细节优化

### 9.1 字体和排版动画
```kotlin
@Composable
fun AnimatedText(
    text: String,
    style: TextStyle,
    modifier: Modifier = Modifier
) {
    var currentText by remember { mutableStateOf("") }
    
    LaunchedEffect(text) {
        // 文字逐字显示动画
        for (i in text.indices) {
            currentText = text.substring(0, i + 1)
            delay(50) // 字符间延迟
        }
    }
    
    Text(
        text = currentText,
        style = style,
        modifier = modifier
    )
}
```

### 9.2 图标动画
```kotlin
@Composable
fun AnimatedIcon(
    imageVector: ImageVector,
    contentDescription: String?,
    modifier: Modifier = Modifier
) {
    var scale by remember { mutableStateOf(1f) }
    
    Icon(
        imageVector = imageVector,
        contentDescription = contentDescription,
        modifier = modifier
            .scale(scale)
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = {
                        // 点击时的缩放动画
                        scale = 0.8f
                        // 动画结束后恢复
                        // 这里需要使用协程来实现动画效果
                    }
                )
            }
    )
}
```

## 10. 用户体验增强

### 10.1 手势反馈
```kotlin
@Composable
fun GestureFeedbackArea(
    onSwipeLeft: () -> Unit,
    onSwipeRight: () -> Unit,
    content: @Composable () -> Unit
) {
    var offsetX by remember { mutableStateOf(0f) }
    
    Box(
        modifier = Modifier
            .offset { IntOffset(offsetX.toInt(), 0) }
            .pointerInput(Unit) {
                detectHorizontalDragGestures(
                    onDragStart = { },
                    onDragEnd = {
                        // 根据拖拽距离判断是否触发手势
                        when {
                            offsetX > 200 -> onSwipeRight()
                            offsetX < -200 -> onSwipeLeft()
                        }
                        // 回弹动画
                        offsetX = 0f
                    },
                    onDragCancel = {
                        offsetX = 0f
                    },
                    onHorizontalDrag = { _, dragAmount ->
                        offsetX += dragAmount
                    }
                )
            }
    ) {
        content()
    }
}
```

### 10.2 视觉反馈
```kotlin
@Composable
fun VisualFeedbackOverlay(
    isVisible: Boolean,
    message: String
) {
    AnimatedVisibility(
        visible = isVisible,
        enter = slideInVertically { -it } + fadeIn(),
        exit = slideOutVertically { -it } + fadeOut()
    ) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            color = MaterialTheme.colors.primary,
            shape = RoundedCornerShape(8.dp)
        ) {
            Text(
                text = message,
                color = MaterialTheme.colors.onPrimary,
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```