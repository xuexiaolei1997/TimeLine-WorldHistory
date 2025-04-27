import React, { useState, useEffect } from 'react';
import Earth3D from './components/Earth3D';
import TimelineController from './components/Timeline/TimelineController';
import { loadInitialData } from './utils/DataLoader';

function App() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await loadInitialData();
      setEvents(data.events);
    };
    fetchData();
  }, []);

  return (
    <div className="app-container">
      <div className="vertical-timeline-container">
        <TimelineController 
          currentDate={currentDate}
          onDateChange={setCurrentDate}
        />
      </div>
      <div className="earth-container">
        <Earth3D 
          currentDate={currentDate}
          events={events}
        />
      </div>
    </div>
  );
}

export default App;
