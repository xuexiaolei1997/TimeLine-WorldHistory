
// 模拟数据加载
const fetchData = async (file) => {
  try {
    console.log('Using mock data for:', file);
    
    // 模拟events.json数据
    if (file === 'events.json') {
      return [
        {
          id: "pyramids",
          title: { en: "Construction of Pyramids", zh: "金字塔建造" },
          period: "ancient",
          date: { start: "-2600-01-01", end: "-2500-12-31" },
          location: { coordinates: [29.9792, 31.1342], zoomLevel: 4 },
          description: { en: "Construction of the Great Pyramids of Giza", zh: "吉萨大金字塔的建造时期" },
          media: { images: ["pyramid.jpg"] }
        },
        {
          id: "roman-empire",
          title: { en: "Roman Empire", zh: "罗马帝国" },
          period: "ancient",
          date: { start: "-27-01-16", end: "476-09-04" },
          location: { coordinates: [41.9028, 12.4964], zoomLevel: 3 },
          description: { en: "Rise and fall of the Roman Empire", zh: "罗马帝国的兴衰" }
        },
        {
          id: "great-wall",
          title: { en: "Great Wall Construction", zh: "长城修建" },
          period: "medieval",
          date: { start: "1368-01-01", end: "1644-12-31" },
          location: { coordinates: [40.4319, 116.5704], zoomLevel: 4 },
          description: { en: "Ming Dynasty reconstruction of the Great Wall", zh: "明朝时期长城的重建" }
        },
        {
          id: "industrial-revolution",
          title: { en: "Industrial Revolution", zh: "工业革命" },
          period: "modern",
          date: { start: "1760-01-01", end: "1840-12-31" },
          location: { coordinates: [51.5074, -0.1278], zoomLevel: 3 },
          description: { en: "Transition to new manufacturing processes", zh: "新型制造工艺的转型时期" }
        }
      ];
    }

    // 模拟periods.json数据
    if (file === 'periods.json') {
      return {
        ancient: { name: "Ancient", color: "#8B4513" },
        medieval: { name: "Medieval", color: "#556B2F" },
        modern: { name: "Modern", color: "#4682B4" }
      };
    }

    throw new Error(`No mock data available for ${file}`);
  } catch (error) {
    console.error(`Error loading mock data for ${file}:`, error);
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

export const loadInitialData = async (zoomLevel = 0) => {
  await simulateNetworkDelay();
  
  const [events, periods] = await Promise.all([
    fetchData('events.json'),
    fetchData('periods.json')
  ]);

  // Filter events based on zoom level
  const filteredEvents = events.filter(event => 
    zoomLevel === 0 || event.location.zoomLevel <= zoomLevel
  );

  return {
    events: filteredEvents.map(event => ({
      ...transformEvent(event),
      startDate: parseDate(event.date.start),
      endDate: parseDate(event.date.end)
    })),
    periods
  };
};

export const loadEventDetails = async (eventId, zoomLevel = 0) => {
  await simulateNetworkDelay();
  
  const events = await fetchData('events.json');
  const event = events.find(e => e.id === eventId);
  if (!event) return null;
  
  // Only load details if zoom level is sufficient
  if (zoomLevel > 0 && event.location.zoomLevel > zoomLevel) {
    return null;
  }
  
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
