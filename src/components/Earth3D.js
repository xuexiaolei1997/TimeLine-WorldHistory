import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer';
import { useTheme } from '@mui/material/styles';
import { Tooltip, Box, Typography, IconButton, Popover } from '@mui/material';
import { Info } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { gsap } from 'gsap';

const Earth3D = ({ 
  events, 
  selectedEvent, 
  onEventSelect, 
  currentDate,
  minImportance = 1
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const mountRef = useRef(null);
  const [scene, setScene] = useState(null);
  const [camera, setCamera] = useState(null);
  const [renderer, setRenderer] = useState(null);
  const [labelRenderer, setLabelRenderer] = useState(null);
  const [controls, setControls] = useState(null);
  const [earth, setEarth] = useState(null);
  const markersRef = useRef([]);

  // 初始化场景
  useEffect(() => {
    if (!mountRef.current) return;

    // 创建场景
    const newScene = new THREE.Scene();
    newScene.background = new THREE.Color(0x000000);

    // 创建相机
    const newCamera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    newCamera.position.z = 5;

    // 创建渲染器
    const newRenderer = new THREE.WebGLRenderer({ antialias: true });
    newRenderer.setSize(window.innerWidth, window.innerHeight);
    newRenderer.setPixelRatio(window.devicePixelRatio);

    // 创建标签渲染器
    const newLabelRenderer = new CSS2DRenderer();
    newLabelRenderer.setSize(window.innerWidth, window.innerHeight);
    newLabelRenderer.domElement.style.position = 'absolute';
    newLabelRenderer.domElement.style.top = '0';
    newLabelRenderer.domElement.style.pointerEvents = 'none';

    // 添加控制器
    const newControls = new OrbitControls(newCamera, newRenderer.domElement);
    newControls.enableDamping = true;
    newControls.dampingFactor = 0.05;
    newControls.minDistance = 3;
    newControls.maxDistance = 10;

    // 创建地球
    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    const earthTexture = textureLoader.load('/textures/earth.jpg');
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: earthTexture,
      bumpScale: 0.05,
    });
    const newEarth = new THREE.Mesh(earthGeometry, earthMaterial);

    // 添加环境光和平行光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 3, 5);
    
    newScene.add(newEarth);
    newScene.add(ambientLight);
    newScene.add(directionalLight);

    mountRef.current.appendChild(newRenderer.domElement);
    mountRef.current.appendChild(newLabelRenderer.domElement);

    setScene(newScene);
    setCamera(newCamera);
    setRenderer(newRenderer);
    setLabelRenderer(newLabelRenderer);
    setControls(newControls);
    setEarth(newEarth);

    // 清理函数
    return () => {
      newRenderer.dispose();
      newLabelRenderer.domElement.remove();
      mountRef.current?.removeChild(newRenderer.domElement);
      mountRef.current?.removeChild(newLabelRenderer.domElement);
    };
  }, []);

  // 处理窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      if (!camera || !renderer || !labelRenderer) return;

      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();

      renderer.setSize(window.innerWidth, window.innerHeight);
      labelRenderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [camera, renderer, labelRenderer]);

  // 渲染循环
  useEffect(() => {
    if (!scene || !camera || !renderer || !controls || !labelRenderer) return;

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    };

    animate();
  }, [scene, camera, renderer, controls, labelRenderer]);

  // Replace the color picker UI implementation with a simpler version using CSS color input
  const renderColorPicker = (color, onChange) => {
    return (
      <Box
        component="input"
        type="color"
        value={color}
        onChange={(e) => onChange(e.target.value)}
        sx={{
          width: '100%',
          height: '40px',
          padding: 0,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: theme.shape.borderRadius,
          cursor: 'pointer'
        }}
      />
    );
  };

  // 更新事件标记
  const updateMarkers = useCallback(() => {
    if (!scene) return;

    // 清除旧标记
    markersRef.current.forEach(marker => {
      scene.remove(marker);
      if (marker.children.length) {
        marker.children[0].element.remove();
      }
    });
    markersRef.current = [];

    // 添加新标记
    events.forEach(event => {
      if (event.importance < minImportance) return;

      const [lng, lat] = event.location.coordinates;
      const position = latLngToVector3(lng, lat);
      
      // 创建标记几何体
      const markerGeometry = new THREE.SphereGeometry(0.02, 16, 16);
      const markerMaterial = new THREE.MeshBasicMaterial({ 
        color: event.location.highlightColor || theme.palette.primary.main,
        transparent: true,
        opacity: 0.8
      });
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.copy(position);
      
      // 创建标签
      const labelElement = document.createElement('div');
      labelElement.className = 'marker-label';
      labelElement.style.backgroundColor = theme.palette.background.paper;
      labelElement.style.color = theme.palette.text.primary;
      labelElement.style.padding = '4px 8px';
      labelElement.style.borderRadius = '4px';
      labelElement.style.fontSize = '12px';
      labelElement.style.pointerEvents = 'auto';
      labelElement.style.cursor = 'pointer';
      labelElement.style.boxShadow = theme.shadows[1];
      labelElement.textContent = event.title[navigator.language.split('-')[0]] || event.title.en;
      
      const label = new CSS2DObject(labelElement);
      label.position.copy(position);
      
      // 添加点击事件
      labelElement.addEventListener('click', () => {
        onEventSelect(event);
        
        // 动画相机到标记位置
        const targetPosition = position.clone().multiplyScalar(2);
        gsap.to(camera.position, {
          duration: 1,
          x: targetPosition.x,
          y: targetPosition.y,
          z: targetPosition.z,
          ease: 'power2.inOut'
        });
      });
      
      scene.add(marker);
      scene.add(label);
      markersRef.current.push(marker, label);
    });
  }, [scene, events, minImportance, theme, onEventSelect, camera]);

  // 当事件或重要性改变时更新标记
  useEffect(() => {
    updateMarkers();
  }, [events, minImportance, updateMarkers]);

  // 当选中事件改变时更新相机位置
  useEffect(() => {
    if (!selectedEvent || !camera) return;

    const [lng, lat] = selectedEvent.location.coordinates;
    const targetPosition = latLngToVector3(lng, lat).multiplyScalar(2);
    
    gsap.to(camera.position, {
      duration: 1,
      x: targetPosition.x,
      y: targetPosition.y,
      z: targetPosition.z,
      ease: 'power2.inOut'
    });
  }, [selectedEvent, camera]);

  // 经纬度转换为三维坐标
  const latLngToVector3 = (lng, lat) => {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    const x = -(Math.sin(phi) * Math.cos(theta));
    const z = Math.sin(phi) * Math.sin(theta);
    const y = Math.cos(phi);
    return new THREE.Vector3(x, y, z);
  };

  return (
    <Box ref={mountRef} sx={{ width: '100%', height: '100vh', position: 'relative' }}>
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 1000,
          backgroundColor: 'background.paper',
          borderRadius: 1,
          p: 1,
        }}
      >
        <Tooltip title={t('earth.help')}>
          <IconButton size="small">
            <Info />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Earth3D;
