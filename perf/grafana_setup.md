# 🎨 Grafana 快速配置指南

## 1️⃣ 访问 Grafana
```
URL: http://localhost:3000
用户名: admin
密码: admin
```

## 2️⃣ 验证数据源（首次使用）
1. 左侧菜单 → ⚙️ **Configuration** → **Data sources**
2. 应该看到 **Prometheus** 数据源
3. 点击 **Test** 确认连接正常

## 3️⃣ 创建性能仪表板

### 步骤A: 新建仪表板
1. 点击 **+** → **Dashboard**
2. 点击 **Add new panel**

### 步骤B: 添加关键面板

#### 📊 面板1: HTTP 请求响应时间
```
标题: HTTP Response Time
查询: k6_http_req_duration
可视化类型: Time series
单位: milliseconds (ms)
```

#### 📊 面板2: 虚拟用户数
```
标题: Virtual Users
查询: k6_vus
可视化类型: Time series
```

#### 📊 面板3: HTTP 请求成功率
```
标题: Success Rate
查询: (k6_checks{check="status is 200"} / k6_http_reqs) * 100
可视化类型: Gauge
单位: percent (0-100)
```

#### 📊 面板4: 请求总数
```
标题: Total Requests
查询: k6_http_reqs
可视化类型: Stat
```

### 步骤C: 保存仪表板
1. 点击 💾 **Save**
2. 命名: "K6 Performance Dashboard"

## 4️⃣ 查看实时数据
- 设置自动刷新: 右上角选择 "5s" 或 "10s"
- 调整时间范围: 选择 "Last 5 minutes" 或 "Last 15 minutes"