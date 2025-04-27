import React, { useState, useEffect, useCallback } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { format, parseISO } from 'date-fns';

const TimelineController = ({ currentDate, onDateChange }) => {
  const [minDate, setMinDate] = useState(new Date(-3500, 0, 1)); // 公元前3500年
  const [maxDate, setMaxDate] = useState(new Date());
  const [sliderValue, setSliderValue] = useState(0);

  // 计算日期范围的总天数
  const totalDays = useCallback(() => {
    return Math.floor((maxDate - minDate) / (1000 * 60 * 60 * 24));
  }, [minDate, maxDate]);

  // 将日期转换为滑块值
  const dateToSliderValue = useCallback((date) => {
    const daysFromMin = Math.floor((date - minDate) / (1000 * 60 * 60 * 24));
    return (daysFromMin / totalDays()) * 100;
  }, [minDate, totalDays]);

  // 将滑块值转换为日期
  const sliderValueToDate = useCallback((value) => {
    const daysFromMin = (value / 100) * totalDays();
    const newDate = new Date(minDate);
    newDate.setDate(newDate.getDate() + daysFromMin);
    return newDate;
  }, [minDate, totalDays]);

  // 初始化滑块值
  useEffect(() => {
    setSliderValue(dateToSliderValue(currentDate));
  }, [currentDate, dateToSliderValue]);

  // 处理滑块变化
  const handleSliderChange = (value) => {
    setSliderValue(value);
    onDateChange(sliderValueToDate(value));
  };

  // 格式化日期显示
  const formatDateDisplay = (date) => {
    if (date.getFullYear() < 0) {
      return `公元前${Math.abs(date.getFullYear())}年`;
    }
    return format(date, 'yyyy年MM月dd日');
  };

  return (
    <div className="timeline-container">
      <div className="date-display">
        {formatDateDisplay(currentDate)}
      </div>
      <Slider
        min={0}
        max={100}
        value={sliderValue}
        onChange={handleSliderChange}
        step={0.01}
        railStyle={{ backgroundColor: '#ddd', height: 4 }}
        trackStyle={{ backgroundColor: '#1890ff', height: 4 }}
        handleStyle={{
          borderColor: '#1890ff',
          height: 16,
          width: 16,
          marginTop: -6,
          backgroundColor: '#fff',
        }}
      />
      <div className="time-range">
        <span>{formatDateDisplay(minDate)}</span>
        <span>{formatDateDisplay(maxDate)}</span>
      </div>
    </div>
  );
};

export default TimelineController;
