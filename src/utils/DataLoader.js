import config from '../config';

// Generate request ID
const generateRequestId = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// API request timeout control
const timeout = (promise, ms) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), ms)
    )
  ]);
};

class ApiError extends Error {
  constructor(error, requestId) {
    super(error.message);
    this.type = error.type;
    this.code = error.code;
    this.details = error.details;
    this.retryAfter = error.retry_after;
    this.requestId = requestId;
  }
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const handleApiResponse = async (response) => {
  const data = await response.json();
  const requestId = response.headers.get('X-Request-ID');
  
  if (!data.success) {
    throw new ApiError(data.error, requestId);
  }
  
  return { data: data.data, requestId };
};

const fetchWithRetry = async (url, options = {}, retries = 3) => {
  const baseDelay = 1000; // Start with 1 second delay
  
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) { // Rate limited
        const data = await response.json();
        const retryAfter = data.detail?.retry_after || Math.pow(2, i) * baseDelay;
        console.warn(`Rate limited, retrying after ${retryAfter}ms`);
        await sleep(retryAfter);
        continue;
      }
      
      return response;
    } catch (error) {
      if (i === retries - 1) throw error; // Last retry failed
      
      const delay = Math.pow(2, i) * baseDelay;
      console.warn(`Request failed, retrying in ${delay}ms`, error);
      await sleep(delay);
    }
  }
};

// Actual API call
const fetchApiData = async (endpoint, options = {}) => {
  try {
    const { method = 'GET', body, headers = {} } = options;
    const requestId = generateRequestId();
    
    const req_config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Request-ID': requestId,
        ...headers
      },
      credentials: 'include'
    };
    
    if (body) {
      req_config.body = JSON.stringify(body);
    }

    const response = await timeout(
      fetchWithRetry(`${config.apiBaseUrl}/${endpoint}`, req_config),
      config.apiTimeout
    );

    const { data, requestId: serverRequestId } = await handleApiResponse(response);
    return { 
      data,
      requestId: serverRequestId || requestId,
      performanceData: {
        responseTime: response.headers.get('X-Response-Time')
      }
    };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Convert other errors to ApiError format
    throw new ApiError({
      type: 'CLIENT_ERROR',
      message: error.message,
      details: { originalError: error.toString() }
    });
  }
};

// Mock data loading
const fetchData = async (file) => {
  try {
    const response = await fetch(`/mock-data/${file}`);
    if (!response.ok) {
      throw new Error(`Failed to load mock data: ${file}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error loading mock data ${file}:`, error);
    throw error;
  }
};

const parseDate = (dateStr) => {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  return isNaN(date.getTime()) ? null : date;
};

const transformEvent = (event) => ({
  id: event.id,
  title: event.title.zh || event.title.en,
  startDate: parseDate(event.date.start),
  endDate: parseDate(event.date.end),
  location: {
    coordinates: event.location.coordinates,
    zoomLevel: event.location.zoomLevel,
    highlightColor: event.location.highlightColor || "#FF0000"
  },
  contentRefs: {
    articles: event.contentRefs?.articles || [],
    images: event.media?.images || []
  }
});

export const loadInitialData = async (zoomLevel = 0, page = 1, pageSize = 20) => {
  try {
    let events, periods, regions;
    
    if (config.useMockData) {
      [events, periods, regions] = await Promise.all([
        fetchData('events.json'),
        fetchData('periods.json'),
        fetchData('regions.json')
      ]);
    } else {
      [events, periods, regions] = await Promise.all([
        fetchApiData('events', {
          method: 'GET',
          body: {
            skip: (page - 1) * pageSize,
            limit: pageSize,
            zoomLevel
          }
        }).then(res => res.data),
        fetchApiData('periods').then(res => res.data),
        fetchApiData('regions').then(res => res.data)
      ]);
    }

    // Filter events based on zoom level
    const filteredEvents = events.filter(event => 
      zoomLevel === 0 || event.location.zoomLevel <= zoomLevel
    );

    return {
      events: filteredEvents.map(transformEvent),
      periods,
      regions
    };
  } catch (error) {
    console.error('Failed to load initial data:', error);
    throw error;
  }
};

export const loadEventDetails = async (eventId) => {
  if (!eventId) return null;
  
  try {
    const event = config.useMockData
      ? (await fetchData('events.json')).find(e => e.id === eventId)
      : await fetchApiData(`events/${eventId}`).then(res => res.data);
      
    return event ? transformEvent(event) : null;
  } catch (error) {
    console.error(`Failed to load event details for ${eventId}:`, error);
    throw error;
  }
};

const DataLoader = {
  loadInitialData,
  loadEventDetails
};

export default DataLoader;
