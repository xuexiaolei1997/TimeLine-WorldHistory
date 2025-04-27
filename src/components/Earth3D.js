import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const Earth3D = ({ currentDate, events }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(new THREE.Scene());
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const earthRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // 初始化Three.js场景
    const scene = sceneRef.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
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
    controlsRef.current = controls;

    // 添加光源
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

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

    mountRef.current.appendChild(renderer.domElement);

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  useEffect(() => {
    // 更新事件标记
    const scene = sceneRef.current;
    
    // 清除旧标记
    markersRef.current.forEach(marker => {
      scene.remove(marker);
    });
    markersRef.current = [];

    // 添加新标记
    events.forEach(event => {
      if (new Date(event.startDate) <= currentDate && 
          new Date(event.endDate) >= currentDate) {
        const marker = createEventMarker(event);
        scene.add(marker);
        markersRef.current.push(marker);
      }
    });
  }, [currentDate, events]);

  const createEventMarker = (event) => {
    const markerGeometry = new THREE.SphereGeometry(0.05, 16, 16);
    const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    
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

  return <div ref={mountRef} style={{ width: '70%', height: '100vh' }} />;
};

export default Earth3D;
