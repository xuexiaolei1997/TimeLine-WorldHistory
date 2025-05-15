// 后端API配置
const config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  useMockData: process.env.REACT_APP_USE_MOCK_DATA === 'true',
  apiTimeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '5000'),
  // 国际化配置
  i18n: {
    supportedLngs: ['en', 'zh'],
    fallbackLng: process.env.REACT_APP_DEFAULT_LANG || 'en',
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false
    }
  }
};

export default config;
