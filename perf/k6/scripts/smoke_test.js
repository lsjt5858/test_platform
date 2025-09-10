// import http from 'k6/http';
// import { check, sleep } from 'k6';

// export let options = {
//   vus: 2,
//   duration: '30s',
// };

// export default function () {
//   let res = http.get('https://www.baidu.com/'); // Mac 用 host.docker.internal
//   check(res, {
//     'is status 200': (r) => r.status === 200,
//   });
//   sleep(1);
// }

// 注意：如果你用的是 Docker 容器来运行 k6，而你想测试的是你本地正在开发的服务（比如你本地跑了一个 http://localhost:3000 的 API 服务），
// 那么你不能直接用 localhost 来访问你的服务，因为 localhost 在容器里指的是容器的内部网络。
// 测试 你本地正在开发的服务（比如你本地跑了一个 http://localhost:3000 的 API 服务），
// 而 k6 是跑在 Docker 容器里的 —— 容器内访问宿主机（你的 Mac）不能用 localhost，
// 必须用 host.docker.internal。


import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '60s',
};

export default function () {
  let res = http.get('http://host.docker.internal:3000/api/v1/status'); // 使用可靠的测试端点
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}