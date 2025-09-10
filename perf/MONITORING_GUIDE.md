# 🔍 性能监控查看指南

## 📊 各组件访问地址

| 组件 | 地址 | 用途 | 登录信息 |
|------|------|------|----------|
| **Prometheus** | http://localhost:9090 | 数据存储和查询 | 无需登录 |
| **Grafana** | http://localhost:3000 | 数据可视化仪表板 | admin/admin |
| **Pushgateway** | http://localhost:9091 | K6数据推送中转 | 无需登录 |

---

## 🎯 Prometheus 数据查看

### 1. 访问 Graph 页面
```
URL: http://localhost:9090/graph
```

### 2. 常用 K6 查询语句

#### 📈 基础指标
```promql
# 当前虚拟用户数
k6_vus

# 最大虚拟用户数
k6_vus_max

# HTTP 请求总数
k6_http_reqs

# HTTP 响应时间（毫秒）
k6_http_req_duration
```

#### 🔍 高级分析查询
```promql
# HTTP 错误率（过去5分钟）
rate(k6_http_req_failed[5m]) * 100

# 平均响应时间
avg(k6_http_req_duration)

# 95分位数响应时间
quantile(0.95, k6_http_req_duration)

# 按状态码分组的请求数
sum by (status) (k6_http_reqs)

# 按URL分组的平均响应时间
avg by (url) (k6_http_req_duration)
```

### 3. 查看所有可用指标
```
URL: http://localhost:9090/targets
检查 Pushgateway 目标状态是否为 UP
```

---

## 📈 Grafana 仪表板配置

### 1. 首次访问设置

#### 访问 Grafana
```
URL: http://localhost:3000
用户名: admin
密码: admin
```

#### 验证数据源
1. 点击左侧 ⚙️ **Configuration** → **Data sources**
2. 应该看到 **Prometheus** 数据源
3. 点击 **Test** 按钮验证连接

### 2. 创建 K6 性能仪表板

#### 添加新仪表板
1. 点击 **+** → **Dashboard** → **Add new panel**

#### 推荐面板配置

##### 📊 Panel 1: HTTP 请求数
```
Title: HTTP Requests
Query: k6_http_reqs
Visualization: Stat
```

##### 📊 Panel 2: 响应时间趋势
```
Title: Response Time Trend
Query: k6_http_req_duration
Visualization: Time series
Unit: milliseconds (ms)
```

##### 📊 Panel 3: 虚拟用户数
```
Title: Virtual Users
Query: k6_vus
Visualization: Time series
```

##### 📊 Panel 4: 错误率
```
Title: Error Rate
Query: rate(k6_http_req_failed[5m]) * 100
Visualization: Gauge
Unit: percent (0-100)
Max: 100
```

##### 📊 Panel 5: 响应时间分布
```
Title: Response Time Distribution
Query: histogram_quantile(0.95, k6_http_req_duration)
Visualization: Stat
```

### 3. 保存仪表板
1. 点击右上角 💾 **Save dashboard**
2. 命名为 "K6 Performance Dashboard"

---

## 🚀 Pushgateway 数据查看

### 访问 Pushgateway
```
URL: http://localhost:9091
```

### 查看推送的指标
1. **主页面**: 显示所有推送的指标组
2. **Metrics 端点**: http://localhost:9091/metrics
   - 查看原始 Prometheus 格式数据
   - 验证 K6 数据是否成功推送

### 推送状态验证
```bash
# 查看推送的 K6 指标
curl http://localhost:9091/metrics | grep k6_
```

---

## 📊 性能数据解读指南

### 🎯 关键性能指标（KPI）

#### 1. **响应时间指标**
| 指标 | 含义 | 好/坏阈值 |
|------|------|-----------|
| `k6_http_req_duration` | HTTP请求响应时间 | <500ms 好, >2s 差 |
| `k6_http_req_waiting` | 服务器处理时间 | <300ms 好, >1s 差 |
| `k6_http_req_blocked` | 建立连接时间 | <100ms 好, >500ms 差 |

#### 2. **吞吐量指标**
| 指标 | 含义 | 参考值 |
|------|------|--------|
| `k6_http_reqs` | 请求总数 | 越高越好 |
| `rate(k6_http_reqs[1m])` | 每秒请求数(RPS) | 取决于预期 |

#### 3. **错误率指标**
| 指标 | 含义 | 阈值 |
|------|------|------|
| `k6_http_req_failed` | 失败请求率 | <1% 好, >5% 差 |
| `k6_checks` | 断言通过率 | 100% 理想 |

#### 4. **负载指标**
| 指标 | 含义 | 说明 |
|------|------|------|
| `k6_vus` | 当前虚拟用户数 | 测试负载大小 |
| `k6_iterations` | 完成的迭代数 | 测试执行量 |

### 🔍 性能分析要点

#### ✅ 良好性能特征
- 响应时间稳定且低
- 错误率接近0%
- 吞吐量满足需求
- 资源利用率合理

#### ⚠️ 性能问题信号
- 响应时间波动大
- 错误率突然上升
- 吞吐量达到瓶颈
- 超时请求增多

#### 📈 性能优化建议
1. **响应时间高**: 优化数据库查询、缓存策略
2. **错误率高**: 检查服务健康状态、容量规划
3. **吞吐量低**: 扩展资源、负载均衡优化

---

## 🔄 持续监控工作流

### 1. 执行测试
```bash
./run_perf.sh
```

### 2. 数据流验证
1. **Pushgateway**: 确认数据推送成功
2. **Prometheus**: 验证指标可查询
3. **Grafana**: 查看可视化结果

### 3. 性能分析
1. 查看关键指标趋势
2. 识别性能瓶颈
3. 对比历史基线数据

### 4. 结果判断
- ✅ 性能达标: 继续监控
- ⚠️ 性能下降: 分析根因
- ❌ 性能不达标: 优化和重测

---

## 🛠️ 故障排查

### 常见问题

#### 1. Grafana 无法查询到数据
```bash
# 检查 Prometheus 连接
curl http://localhost:9090/api/v1/query?query=k6_vus

# 检查数据源配置
# Grafana → Configuration → Data sources → Prometheus
```

#### 2. Pushgateway 中没有数据
```bash
# 检查 K6 桥接脚本
docker-compose run --rm k6-bridge

# 查看推送状态
curl http://localhost:9091/metrics | grep k6_
```

#### 3. Prometheus 抓取失败
```bash
# 检查 Targets 状态
curl http://localhost:9090/targets
```

### 重新运行测试
```bash
# 清理并重新开始
docker-compose down
./run_perf.sh
```