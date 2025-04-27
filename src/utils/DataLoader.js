// 测试数据
const testEvents = [
  {
    id: "egypt-pyramids",
    title: "埃及金字塔建造",
    startDate: "-2600-01-01",
    endDate: "-2500-01-01",
    location: {
      coordinates: [29.9792, 31.1342], // 吉萨坐标
      zoomLevel: 3,
      highlightColor: "#FF0000"
    },
    contentRefs: {
      articles: ["egypt-construction"],
      images: ["pyramid1.jpg", "pyramid2.jpg"]
    }
  },
  {
    id: "great-wall",
    title: "长城修建",
    startDate: "-700-01-01", 
    endDate: "-200-01-01",
    location: {
      coordinates: [40.4319, 116.5704], // 北京附近
      zoomLevel: 3,
      highlightColor: "#FFA500"
    },
    contentRefs: {
      articles: ["great-wall-construction"],
      images: ["wall1.jpg"]
    }
  }
];

// 模拟API请求延迟
const simulateNetworkDelay = () => 
  new Promise(resolve => setTimeout(resolve, 500));

export const loadInitialData = async () => {
  await simulateNetworkDelay();
  
  return {
    events: testEvents.map(event => ({
      ...event,
      startDate: parseDate(event.startDate),
      endDate: parseDate(event.endDate)
    }))
  };
};

export const loadEventDetails = async (eventId) => {
  await simulateNetworkDelay();
  
  const event = testEvents.find(e => e.id === eventId);
  if (!event) return null;
  
  return {
    ...event,
    startDate: parseDate(event.startDate),
    endDate: parseDate(event.endDate),
    // 模拟详细内容
    articleContent: `这是关于${event.title}的详细文章内容...`,
    images: event.contentRefs.images.map(img => ({
      url: img,
      caption: `${event.title}相关图片`
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
