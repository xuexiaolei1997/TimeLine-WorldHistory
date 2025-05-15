import axios from 'axios';

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = new Set();
    this.healthCheckInterval = null;
  }

  // 初始化监控
  init() {
    // 监控API请求
    this.setupAxiosInterceptors();
    
    // 监控页面性能
    this.monitorPageMetrics();
    
    // 启动健康检查
    this.startHealthCheck();
  }

  // 设置Axios拦截器监控API性能
  setupAxiosInterceptors() {
    axios.interceptors.request.use(config => {
      config.metadata = { startTime: Date.now() };
      return config;
    });

    axios.interceptors.response.use(
      response => {
        this.recordApiCall(response.config, null);
        return response;
      },
      error => {
        this.recordApiCall(error.config, error);
        return Promise.reject(error);
      }
    );
  }

  // 记录API调用性能
  recordApiCall(config, error) {
    const duration = Date.now() - config.metadata.startTime;
    const endpoint = `${config.method} ${config.url}`;
    
    const metric = this.metrics.get(endpoint) || {
      calls: 0,
      totalDuration: 0,
      errors: 0,
      durations: []
    };

    metric.calls++;
    metric.totalDuration += duration;
    metric.durations.push(duration);
    if (error) metric.errors++;

    // 只保留最近100个请求的数据
    if (metric.durations.length > 100) {
      metric.durations.shift();
    }

    this.metrics.set(endpoint, metric);
    this.notifyObservers();
  }

  // 监控页面性能指标
  monitorPageMetrics() {
    if ('performance' in window) {
      // 监控页面加载性能
      window.addEventListener('load', () => {
        const pageLoadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        this.recordMetric('page_load', pageLoadTime);
      });

      // 监控资源加载性能
      const observer = new PerformanceObserver(list => {
        list.getEntries().forEach(entry => {
          if (entry.entryType === 'resource') {
            this.recordMetric(`resource_${entry.name}`, entry.duration);
          }
        });
      });

      observer.observe({ entryTypes: ['resource'] });
    }
  }

  // 记录一般性能指标
  recordMetric(name, value) {
    const metric = this.metrics.get(name) || {
      calls: 0,
      totalDuration: 0,
      errors: 0,
      durations: []
    };

    metric.calls++;
    metric.totalDuration += value;
    metric.durations.push(value);

    if (metric.durations.length > 100) {
      metric.durations.shift();
    }

    this.metrics.set(name, metric);
    this.notifyObservers();
  }

  // 定期健康检查
  startHealthCheck() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(async () => {
      try {
        const startTime = Date.now();
        const response = await axios.get('/api/health');
        const duration = Date.now() - startTime;

        this.recordMetric('health_check', duration);

        if (response.data.status === 'healthy') {
          this.recordMetric('health_check_success', 1);
        } else {
          this.recordMetric('health_check_failure', 1);
        }
      } catch (error) {
        this.recordMetric('health_check_failure', 1);
      }
    }, 30000); // 每30秒检查一次
  }

  // 添加观察者
  addObserver(callback) {
    this.observers.add(callback);
  }

  // 移除观察者
  removeObserver(callback) {
    this.observers.delete(callback);
  }

  // 通知所有观察者
  notifyObservers() {
    const metricsData = {};
    for (const [key, value] of this.metrics) {
      metricsData[key] = {
        averageDuration: value.totalDuration / value.calls,
        p95Duration: this.calculateP95(value.durations),
        errorRate: value.errors / value.calls,
        totalCalls: value.calls,
        recentDurations: value.durations.slice(-5)
      };
    }

    this.observers.forEach(callback => callback(metricsData));
  }

  // 计算95分位数
  calculateP95(durations) {
    if (!durations.length) return 0;
    const sorted = [...durations].sort((a, b) => a - b);
    const index = Math.floor(sorted.length * 0.95);
    return sorted[index];
  }

  // 获取当前性能指标摘要
  getSummary() {
    const summary = {};
    for (const [key, value] of this.metrics) {
      summary[key] = {
        averageDuration: value.totalDuration / value.calls,
        p95Duration: this.calculateP95(value.durations),
        errorRate: value.errors / value.calls,
        totalCalls: value.calls
      };
    }
    return summary;
  }

  // 清理资源
  cleanup() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    this.metrics.clear();
    this.observers.clear();
  }
}

// 创建单例实例
const performanceMonitor = new PerformanceMonitor();

export default performanceMonitor;