// 后端API配置
const config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001',
  useMockData: process.env.REACT_APP_USE_MOCK_DATA === 'false',
  // 国际化配置
  i18n: {
    supportedLngs: ['en', 'zh'],
    fallbackLng: 'en',
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false
    }
  }
};

export default config;
