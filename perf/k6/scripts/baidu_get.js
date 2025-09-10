import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<1500'],
    http_req_failed: ['rate<0.05'],
    checks: ['rate>0.95'],
  },
};

export default function () {
  const params = {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Connection': 'keep-alive',
    },
    tags: { endpoint: 'baidu_search' },
    redirects: 5,
  };

  const url = 'https://www.baidu.com/s';
  const query = { wd: 'k6 性能测试' };

  // k6 http.get 不能直接用对象形式params传Query，使用URLSearchParams拼接
  const qs = Object.entries(query).map(([k,v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
  const fullUrl = `${url}?${qs}`;

  const res = http.get(fullUrl, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'body contains 百度': (r) => r.body && r.body.indexOf('百度') !== -1,
  });

  sleep(1);
}