// 后端API配置
const config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001',
  useMockData: process.env.REACT_APP_USE_MOCK_DATA === 'false'
};

export default config;
