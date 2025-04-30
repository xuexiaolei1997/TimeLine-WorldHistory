import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const Earth3D = ({ currentDate, events, timezone, rotationSpeed }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(new THREE.Scene());
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const earthRef = useRef(null);
  const markersRef = useRef([]);
  const [zoomLevel, setZoomLevel] = useState(0);
  const raycasterRef = useRef(new THREE.Raycaster());
  const mouseRef = useRef(new THREE.Vector2());
  const [hoveredEvent, setHoveredEvent] = useState(null);
  const tooltipRef = useRef(null);
  const linesRef = useRef([]);
  const lastMousePosition = useRef({ clientX: 0, clientY: 0 });
  const directionalLightRef = useRef(null);

  useEffect(() => {
    // 初始化Three.js场景 (只运行一次)
    const scene = sceneRef.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    
    // 创建工具提示元素
    tooltipRef.current = document.createElement('div');
    tooltipRef.current.style.position = 'absolute';
    tooltipRef.current.style.backgroundColor = 'rgba(0,0,0,0.85)';
    tooltipRef.current.style.color = '#FFD700';
    tooltipRef.current.style.padding = '15px';
    tooltipRef.current.style.borderRadius = '8px';
    tooltipRef.current.style.border = '1px solid #FFD700';
    tooltipRef.current.style.boxShadow = '0 0 15px rgba(255, 215, 0, 0.5)';
    tooltipRef.current.style.fontFamily = 'Poppins, sans-serif';
    tooltipRef.current.style.maxWidth = '300px';
    tooltipRef.current.style.transition = 'all 0.3s ease';
    tooltipRef.current.style.pointerEvents = 'none';
    tooltipRef.current.style.display = 'none';
    document.body.appendChild(tooltipRef.current);
    renderer.setSize(window.innerWidth * 0.7, window.innerHeight);
    rendererRef.current = renderer;

    const camera = new THREE.PerspectiveCamera(
      75, 
      window.innerWidth * 0.7 / window.innerHeight, 
      0.1, 
      1000
    );
    camera.position.z = 5;
    cameraRef.current = camera;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    // Set zoom limits to prevent camera getting too close
    controls.minDistance = 2.5; // Minimum zoom distance (can't get closer than 2.5 units)
    controls.maxDistance = 10; // Maximum zoom distance
    controlsRef.current = controls;
    
    // Add zoom change listener
    controls.addEventListener('change', () => {
      // Calculate zoom level based on camera distance
      const newZoom = Math.max(0, Math.floor(5 - camera.position.z));
      if (newZoom !== zoomLevel) {
        setZoomLevel(newZoom);
      }
    });

    // 创建地球
    const geometry = new THREE.SphereGeometry(2, 64, 64);
    const material = new THREE.MeshPhongMaterial({
      map: new THREE.TextureLoader().load('/textures/earth.jpg'),
      specular: 0x111111,
      shininess: 5
    });
    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);
    earthRef.current = earth;

    // 添加光源
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLightRef.current = directionalLight;
    updateSunPosition(currentDate, timezone);
    earth.add(directionalLight);

    mountRef.current.appendChild(renderer.domElement);

    // 鼠标移动事件
    const onMouseMove = (event) => {
      mouseRef.current.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouseRef.current.y = -(event.clientY / window.innerHeight) * 2 + 1;
      lastMousePosition.current = { 
        clientX: event.clientX, 
        clientY: event.clientY 
      };
    };
    window.addEventListener('mousemove', onMouseMove);

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      document.body.removeChild(tooltipRef.current);
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  useEffect(() => {
    // 优化动画循环和标记更新
    let animationFrameId;
    let lastMarkerUpdate = 0;
    let lastLightUpdate = 0;
    let lastRaycastUpdate = 0;
    const markerUpdateThreshold = 10000; // 标记更新间隔100ms
    const lightUpdateThreshold = 50000; // 光源更新间隔500ms
    const raycastThreshold = 100; // 射线检测间隔100ms
    
    // 缓存可见事件
    const visibleEvents = zoomLevel > 0 ? 
      events.filter(event => 
        event.location.zoomLevel <= zoomLevel &&
        new Date(event.startDate) <= currentDate && 
        new Date(event.endDate) >= currentDate
      ) : 
      [];

    // 优化标记更新
    const updateMarkers = () => {
      if (!earthRef.current) return;
      
      // 批量清除旧标记
      markersRef.current.forEach(marker => earthRef.current.remove(marker));
      markersRef.current = [];

      // 批量添加新标记
      const newMarkers = visibleEvents.map(event => {
        const marker = createEventMarker(event);
        earthRef.current.add(marker);
        return marker;
      });
      
      markersRef.current = newMarkers;
    };

    const animate = (timestamp) => {
      animationFrameId = requestAnimationFrame(animate);
      
      // 地球自转
      if (earthRef.current) {
        earthRef.current.rotation.y += rotationSpeed * 0.001;
      }

      // 限制标记更新频率
      if (timestamp - lastMarkerUpdate > markerUpdateThreshold) {
        lastMarkerUpdate = timestamp;
        updateMarkers();
      }

      // 限制光源更新频率
      if (timestamp - lastLightUpdate > lightUpdateThreshold) {
        lastLightUpdate = timestamp;
        updateSunPosition(currentDate, timezone);
      }
      
      // 限制射线检测频率
      if (timestamp - lastRaycastUpdate > raycastThreshold && cameraRef.current) {
        lastRaycastUpdate = timestamp;
        
        raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
        const intersects = raycasterRef.current.intersectObjects(markersRef.current);
        
        if (intersects.length > 0) {
          const marker = intersects[0].object;
          const eventData = marker.userData.event;
          
          // 只有当悬停事件变化时才更新
          if (!hoveredEvent || hoveredEvent.id !== eventData.id) {
            setHoveredEvent(eventData);
            
            // 使用requestAnimationFrame优化DOM更新
            requestAnimationFrame(() => {
              if (tooltipRef.current) {
                tooltipRef.current.style.display = 'block';
                tooltipRef.current.style.left = `${lastMousePosition.current.clientX + 10}px`;
                tooltipRef.current.style.top = `${lastMousePosition.current.clientY + 10}px`;
                tooltipRef.current.innerHTML = `
                  <h3>${eventData.title}</h3>
                  <p>${eventData.description}</p>
                  <p>${new Date(eventData.startDate).toLocaleDateString()} - 
                     ${new Date(eventData.endDate).toLocaleDateString()}</p>
                `;
              }
            });
            
            // 创建延伸线
            createConnectionLine(marker.position);
          }
        } else {
          // Clear hover state when not intersecting any markers
          if (hoveredEvent) {
            setHoveredEvent(null);
            if (tooltipRef.current) {
              tooltipRef.current.style.display = 'none';
            }
            clearConnectionLines();
          }
        }
      }
      
      // 渲染场景
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    
    // 初始更新
    updateMarkers();
    animate(performance.now());

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [currentDate, events, timezone, rotationSpeed]);

  const updateSunPosition = (date, tzOffset) => {
    if (!directionalLightRef.current) return;
    
    // 计算太阳位置 (简化模型)
    const hours = date.getUTCHours() + tzOffset;
    const sunAngle = (hours / 12) * Math.PI; // 0-24小时映射到0-2π
    
    // 设置光源位置 (模拟太阳运动)
    directionalLightRef.current.position.set(
      Math.cos(sunAngle) * 5,
      3,
      Math.sin(sunAngle) * 5
    );
  };

  const createConnectionLine = (markerPosition) => {
    clearConnectionLines();
    
    // 计算地球表面点 (从标记位置到地球中心的向量)
    const direction = markerPosition.clone().normalize();
    const surfacePoint = direction.multiplyScalar(2); // 地球半径为2
    
    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
      surfacePoint,
      markerPosition
    ]);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffff00 });
    const line = new THREE.Line(lineGeometry, lineMaterial);
    
    sceneRef.current.add(line);
    linesRef.current.push(line);
  };

  const clearConnectionLines = () => {
    linesRef.current.forEach(line => {
      sceneRef.current.remove(line);
    });
    linesRef.current = [];
  };

  const createEventMarker = (event) => {
    // Create smaller, more subtle ring marker
    const markerGeometry = new THREE.RingGeometry(0.02, 0.03, 16);
    const markerMaterial = new THREE.MeshBasicMaterial({ 
      color: 0x00AAFF,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6
    });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.userData.event = event;
    // Rotate to face camera initially
    marker.lookAt(new THREE.Vector3(0, 0, 0));
    
    // 将经纬度转换为3D坐标
    const lat = event.location.coordinates[0];
    const lng = event.location.coordinates[1];
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    const radius = 2.05; // 略大于地球半径
    
    marker.position.set(
      -radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );

    return marker;
  };

  return (
    <div ref={mountRef} style={{ width: '100%', height: '100%' }} />
  );
};

export default Earth3D;
