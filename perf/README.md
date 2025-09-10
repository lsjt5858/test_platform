# Performance Testing - 性能测试

## 概述

性能测试模块提供完整的性能测试解决方案，包括负载测试、压力测试、监控和分析。基于 K6 进行性能测试执行，使用 Prometheus + Grafana 进行监控和可视化。

## 技术栈

- **K6**: 现代化的负载测试工具，支持 JavaScript 编写测试脚本
- **Prometheus**: 时序数据库，用于收集和存储性能指标
- **Grafana**: 数据可视化平台，提供丰富的性能监控仪表板

## 目录结构

```
perf/
├── k6/                    # K6 测试脚本和结果
│   ├── scripts/          # 性能测试脚本
│   └── results/          # 测试结果存储
├── prometheus/           # Prometheus 配置
├── grafana/             # Grafana 配置
│   └── dashboards/      # 预定义仪表板
└── README.md
```

## 核心功能

### 1. 负载测试 (Load Testing)

模拟正常用户负载，验证系统在预期负载下的性能表现。

```javascript
// k6/scripts/load_test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // 2分钟内逐渐增加到100个用户
    { duration: '5m', target: 100 }, // 保持100个用户5分钟
    { duration: '2m', target: 0 },   // 2分钟内逐渐减少到0
  ],
};

export default function () {
  let response = http.get('http://api.example.com/users');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### 2. 压力测试 (Stress Testing)

测试系统在极限负载下的表现，找出系统的性能瓶颈。

```javascript
// k6/scripts/stress_test.js
export let options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },
    { duration: '5m', target: 500 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  // 压力测试逻辑
}
```

### 3. 突发测试 (Spike Testing)

测试系统应对流量突增的能力。

```javascript
// k6/scripts/spike_test.js
export let options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m', target: 1000 },  // 突然增加到1000用户
    { duration: '30s', target: 100 },
    { duration: '1m', target: 0 },
  ],
};
```

### 4. 容量测试 (Volume Testing)

测试系统在大量数据下的性能表现。

```javascript
// k6/scripts/volume_test.js
import { SharedArray } from 'k6/data';

const data = new SharedArray('large dataset', function () {
  return JSON.parse(open('./large_dataset.json'));
});

export default function () {
  // 使用大量数据进行测试
  let payload = data[Math.floor(Math.random() * data.length)];
  http.post('http://api.example.com/data', JSON.stringify(payload));
}
```

## 使用指南

### 1. 环境准备

```bash
# 安装 K6
brew install k6

# 启动监控服务（Prometheus + Grafana）
cd perf/
docker-compose up -d prometheus grafana
```

### 2. 运行性能测试

```bash
# 运行基础负载测试
k6 run k6/scripts/load_test.js

# 运行压力测试
k6 run k6/scripts/stress_test.js

# 运行测试并输出结果到文件
k6 run --out json=results/load_test_$(date +%Y%m%d_%H%M%S).json k6/scripts/load_test.js

# 运行测试并发送指标到 Prometheus
k6 run --out prometheus k6/scripts/load_test.js
```

### 3. 测试脚本编写

#### 基础 HTTP 测试

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 50,        // 虚拟用户数
  duration: '30s', // 测试持续时间
};

export default function () {
  // GET 请求
  let response = http.get('http://api.example.com/users');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response size > 0': (r) => r.body.length > 0,
  });

  // POST 请求
  let postData = {
    name: 'Test User',
    email: 'test@example.com',
  };
  
  let postResponse = http.post(
    'http://api.example.com/users',
    JSON.stringify(postData),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(postResponse, {
    'post status is 201': (r) => r.status === 201,
  });

  sleep(1); // 用户思考时间
}
```

#### 业务场景测试

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  // 业务场景：用户注册 -> 登录 -> 创建订单
  
  // 1. 用户注册
  let userData = {
    username: `user_${__VU}_${__ITER}`,
    email: `user_${__VU}_${__ITER}@test.com`,
    password: 'password123'
  };
  
  let registerResp = http.post('http://api.example.com/register', JSON.stringify(userData));
  check(registerResp, { 'register successful': (r) => r.status === 201 });
  
  sleep(1);
  
  // 2. 用户登录
  let loginData = {
    username: userData.username,
    password: userData.password
  };
  
  let loginResp = http.post('http://api.example.com/login', JSON.stringify(loginData));
  check(loginResp, { 'login successful': (r) => r.status === 200 });
  
  let token = loginResp.json().token;
  let headers = { 'Authorization': `Bearer ${token}` };
  
  sleep(2);
  
  // 3. 创建订单
  let orderData = {
    product_id: 'P001',
    quantity: 2
  };
  
  let orderResp = http.post(
    'http://api.example.com/orders',
    JSON.stringify(orderData),
    { headers: headers }
  );
  check(orderResp, { 'order created': (r) => r.status === 201 });
  
  sleep(1);
}
```

### 4. 监控和分析

#### Prometheus 配置

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'k6'
    static_configs:
      - targets: ['localhost:6565']
```

#### Grafana 仪表板

```json
{
  "dashboard": {
    "title": "K6 Performance Testing",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(k6_http_reqs[1m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "k6_http_req_duration{quantile=\"0.95\"}",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## 性能指标

### 关键性能指标 (KPIs)

1. **吞吐量 (Throughput)**: 每秒处理的请求数 (RPS)
2. **响应时间 (Response Time)**: 
   - 平均响应时间
   - 95th 百分位响应时间
   - 99th 百分位响应时间
3. **错误率 (Error Rate)**: HTTP 错误状态码的百分比
4. **并发用户数 (Concurrent Users)**: 同时在线的虚拟用户数

### 性能基准

```javascript
// 性能基准定义
export let options = {
  thresholds: {
    'http_req_duration': ['p(95)<500'],        // 95% 的请求响应时间小于500ms
    'http_req_duration{name:login}': ['p(95)<200'], // 登录接口响应时间
    'http_reqs': ['rate>100'],                 // 每秒处理超过100个请求
    'http_req_failed': ['rate<0.01'],          // 错误率小于1%
    'checks': ['rate>0.95'],                   // 检查通过率大于95%
  },
};
```

## 最佳实践

### 1. 测试环境准备

- 使用独立的性能测试环境
- 确保测试环境与生产环境配置相似
- 在测试前清理数据和缓存

### 2. 测试数据准备

```javascript
// 使用外部数据文件
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

const csvData = new SharedArray('test data', function () {
  return papaparse.parse(open('./test_data.csv'), { header: true }).data;
});

export default function () {
  let data = csvData[Math.floor(Math.random() * csvData.length)];
  // 使用测试数据
}
```

### 3. 渐进式负载

```javascript
export let options = {
  stages: [
    { duration: '5m', target: 100 },   // 预热阶段
    { duration: '10m', target: 100 },  // 稳定负载
    { duration: '5m', target: 200 },   // 增加负载
    { duration: '10m', target: 200 },  // 稳定负载
    { duration: '5m', target: 0 },     // 冷却阶段
  ],
};
```

### 4. 结果分析

- 关注响应时间分布而不仅仅是平均值
- 分析错误模式和错误率趋势
- 识别性能瓶颈和容量限制
- 建立性能基准和回归测试

### 5. 持续性能测试

```bash
# 自动化性能测试脚本
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results/${TIMESTAMP}"

mkdir -p ${RESULTS_DIR}

# 运行负载测试
k6 run --out json=${RESULTS_DIR}/load_test.json k6/scripts/load_test.js

# 运行压力测试
k6 run --out json=${RESULTS_DIR}/stress_test.json k6/scripts/stress_test.js

# 生成报告
echo "Performance test completed. Results saved to ${RESULTS_DIR}"
```

## 故障排除

### 常见问题

1. **连接超时**: 检查网络连接和防火墙设置
2. **内存不足**: 减少虚拟用户数或增加测试机器内存
3. **指标缺失**: 确认 Prometheus 配置正确

### 调试技巧

```javascript
import { check } from 'k6';
import http from 'k6/http';

export default function () {
  let response = http.get('http://api.example.com/users');
  
  // 调试输出
  console.log(`Response status: ${response.status}`);
  console.log(`Response time: ${response.timings.duration}ms`);
  
  if (response.status !== 200) {
    console.error(`Error: ${response.body}`);
  }
}
```
