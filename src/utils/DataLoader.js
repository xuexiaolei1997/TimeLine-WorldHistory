// 从mock-data加载数据
const fetchData = async (file) => {
  try {
    const response = await fetch(`../../public/mock-data/${file}`);
    if (!response.ok) throw new Error(`Failed to load ${file}`);
    return await response.json();
  } catch (error) {
    console.error(`Error loading ${file}:`, error);
    throw error;
  }
};

// 模拟API请求延迟
const simulateNetworkDelay = () => 
  new Promise(resolve => setTimeout(resolve, 500));

// 转换事件数据结构
const transformEvent = (event) => ({
  id: event.id,
  title: event.title.zh || event.title.en,
  startDate: event.date.start,
  endDate: event.date.end,
  location: {
    coordinates: event.location.coordinates,
    zoomLevel: event.location.zoomLevel,
    highlightColor: "#FF0000" // 默认颜色
  },
  contentRefs: {
    articles: [],
    images: event.media?.images || []
  }
});

export const loadInitialData = async () => {
  await simulateNetworkDelay();
  
  const [events, periods] = await Promise.all([
    fetchData('events.json'),
    fetchData('periods.json')
  ]);

  return {
    events: events.map(event => ({
      ...transformEvent(event),
      startDate: parseDate(event.date.start),
      endDate: parseDate(event.date.end)
    })),
    periods
  };
};

export const loadEventDetails = async (eventId) => {
  await simulateNetworkDelay();
  
  const events = await fetchData('events.json');
  const event = events.find(e => e.id === eventId);
  if (!event) return null;
  
  const transformed = transformEvent(event);
  return {
    ...transformed,
    startDate: parseDate(event.date.start),
    endDate: parseDate(event.date.end),
    articleContent: `这是关于${transformed.title}的详细文章内容...`,
    images: transformed.contentRefs.images.map(img => ({
      url: img,
      caption: `${transformed.title}相关图片`
    }))
  };
};

// 辅助函数：解析日期字符串
function parseDate(dateStr) {
  if (dateStr.startsWith("-")) {
    // 公元前日期处理
    const year = parseInt(dateStr.substring(1, 5));
    const month = parseInt(dateStr.substring(6, 8)) - 1;
    const day = parseInt(dateStr.substring(9, 11));
    return new Date(-year, month, day);
  }
  return new Date(dateStr);
}

// 导出所有函数
export default {
  loadInitialData,
  loadEventDetails
};
