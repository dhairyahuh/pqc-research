/**
 * ASTRA-Sec: 3D Satellite Mission Control & Geospatial Network Visualization.
 * Powered by Three.js & Globe.gl (Open Source, MIT License).
 * 
 * Implements real-time 3D Earth, 4-node space constellation topology,
 * dynamic communication links, animated packet hops, interactive node inspection,
 * and seamless integration with FastAPI backend & WebSocket events.
 */

(function () {
  'use strict';

  // --- Constellation Node Coordinates (Deterministic WGS84 Geodetic) ---
  const NODE_CONFIG = {
    gsa: {
      id: 'dtn://gsa/app',
      name: 'Ground Station Alpha',
      location: 'Svalbard Satellite Station, Norway',
      lat: 78.2297,
      lng: 15.4078,
      alt: 0.01,
      type: 'ground_station',
      color: '#00e5ff',
      role: 'Cryptographic Originator (ML-KEM Encap / ML-DSA Signer)'
    },
    sat1: {
      id: 'dtn://sat1/relay',
      name: 'Satellite Relay 1 (LEO-1)',
      location: 'Polar Sun-Synchronous Orbit (~550 km)',
      lat: 52.0,
      lng: 38.0,
      alt: 0.36,
      type: 'satellite_relay',
      color: '#00e5ff',
      role: 'Store-and-Forward Router (SQLite WAL Persistent Spool)'
    },
    sat2: {
      id: 'dtn://sat2/relay',
      name: 'Satellite Relay 2 (LEO-2)',
      location: 'Inclined LEO Relay Constellation (~550 km)',
      lat: -8.0,
      lng: 92.0,
      alt: 0.36,
      type: 'satellite_relay',
      color: '#00e5ff',
      role: 'Store-and-Forward Router (SQLite WAL Persistent Spool)'
    },
    gsb: {
      id: 'dtn://gsb/app',
      name: 'Ground Station Bravo',
      location: 'Canberra Deep Space Communication Complex, Australia',
      lat: -35.4014,
      lng: 148.9817,
      alt: 0.01,
      type: 'ground_station',
      color: '#00e676',
      role: 'Destination Verifier (ML-KEM Decapsulation / Anti-Replay / ACK)'
    }
  };

  // State Management
  let worldGlobe = null;
  let activeIslState = 'UP'; // 'UP' or 'DOWN'
  let selectedNode = null;
  let isAutoRotating = false;
  let nodesTelemetry = {};
  let queueTelemetry = {};
  let inFlightAnimationActive = false;

  // Link Definitions
  function getLinksData() {
    const isOutage = activeIslState === 'DOWN';
    return [
      {
        id: 'uplink',
        name: 'Uplink (RFC 9171 BPv7)',
        startLat: NODE_CONFIG.gsa.lat,
        startLng: NODE_CONFIG.gsa.lng,
        startAlt: NODE_CONFIG.gsa.alt,
        endLat: NODE_CONFIG.sat1.lat,
        endLng: NODE_CONFIG.sat1.lng,
        endAlt: NODE_CONFIG.sat1.alt,
        color: ['#00e5ff', '#2979ff'],
        altitude: 0.22,
        stroke: 2.0,
        dashLength: 0.4,
        dashGap: 0.2,
        animateTime: 1800,
        state: 'UP'
      },
      {
        id: 'isl',
        name: 'Inter-Satellite Link (ISL)',
        startLat: NODE_CONFIG.sat1.lat,
        startLng: NODE_CONFIG.sat1.lng,
        startAlt: NODE_CONFIG.sat1.alt,
        endLat: NODE_CONFIG.sat2.lat,
        endLng: NODE_CONFIG.sat2.lng,
        endAlt: NODE_CONFIG.sat2.alt,
        color: isOutage ? ['#ff1744', '#b71c1c'] : ['#00e5ff', '#00e676'],
        altitude: 0.45,
        stroke: isOutage ? 3.5 : 2.5,
        dashLength: isOutage ? 0.1 : 0.5,
        dashGap: isOutage ? 0.3 : 0.15,
        animateTime: isOutage ? 0 : 2200,
        state: activeIslState
      },
      {
        id: 'downlink',
        name: 'Downlink (BPv7 E2E)',
        startLat: NODE_CONFIG.sat2.lat,
        startLng: NODE_CONFIG.sat2.lng,
        startAlt: NODE_CONFIG.sat2.alt,
        endLat: NODE_CONFIG.gsb.lat,
        endLng: NODE_CONFIG.gsb.lng,
        endAlt: NODE_CONFIG.gsb.alt,
        color: ['#2979ff', '#00e676'],
        altitude: 0.22,
        stroke: 2.0,
        dashLength: 0.4,
        dashGap: 0.2,
        animateTime: 1800,
        state: 'UP'
      }
    ];
  }

  // Node Objects Data
  function getNodesData() {
    return Object.values(NODE_CONFIG).map(n => {
      const q = queueTelemetry[n.id] || { pending: 0, kb: 0 };
      const t = nodesTelemetry[n.id] || {};
      return {
        ...n,
        pending_bundles: q.pending,
        storage_kb: q.kb,
        operational_state: (n.id.includes('sat') && activeIslState === 'DOWN') ? 'SPOOLING_ACTIVE' : 'ONLINE'
      };
    });
  }

  // Rings Data (Pulsing node halos)
  function getRingsData() {
    const isOutage = activeIslState === 'DOWN';
    return [
      {
        lat: NODE_CONFIG.gsa.lat,
        lng: NODE_CONFIG.gsa.lng,
        alt: 0.015,
        color: '#00e5ff',
        maxRadius: 4.5,
        speed: 1.5,
        period: 1400
      },
      {
        lat: NODE_CONFIG.sat1.lat,
        lng: NODE_CONFIG.sat1.lng,
        alt: NODE_CONFIG.sat1.alt,
        color: isOutage ? '#ffab00' : '#00e5ff',
        maxRadius: 6.0,
        speed: isOutage ? 2.5 : 1.8,
        period: 1200
      },
      {
        lat: NODE_CONFIG.sat2.lat,
        lng: NODE_CONFIG.sat2.lng,
        alt: NODE_CONFIG.sat2.alt,
        color: isOutage ? '#ff1744' : '#00e5ff',
        maxRadius: 6.0,
        speed: isOutage ? 2.5 : 1.8,
        period: 1200
      },
      {
        lat: NODE_CONFIG.gsb.lat,
        lng: NODE_CONFIG.gsb.lng,
        alt: 0.015,
        color: '#00e676',
        maxRadius: 4.5,
        speed: 1.5,
        period: 1400
      }
    ];
  }

  // Labels Data
  function getLabelsData() {
    return [
      {
        lat: NODE_CONFIG.gsa.lat,
        lng: NODE_CONFIG.gsa.lng,
        alt: 0.02,
        text: '📡 GSA (Svalbard)',
        size: 0.9,
        color: '#00e5ff'
      },
      {
        lat: NODE_CONFIG.sat1.lat,
        lng: NODE_CONFIG.sat1.lng,
        alt: NODE_CONFIG.sat1.alt + 0.07,
        text: `🛰️ SAT-1 | LEO-1 ${queueTelemetry['dtn://sat1/relay'] ? '(' + queueTelemetry['dtn://sat1/relay'].pending + ' queued)' : ''}`,
        size: 0.95,
        color: activeIslState === 'DOWN' ? '#ffab00' : '#00e5ff'
      },
      {
        lat: NODE_CONFIG.sat2.lat,
        lng: NODE_CONFIG.sat2.lng,
        alt: NODE_CONFIG.sat2.alt + 0.07,
        text: `🛰️ SAT-2 | LEO-2 ${queueTelemetry['dtn://sat2/relay'] ? '(' + queueTelemetry['dtn://sat2/relay'].pending + ' queued)' : ''}`,
        size: 0.95,
        color: activeIslState === 'DOWN' ? '#ff1744' : '#00e5ff'
      },
      {
        lat: NODE_CONFIG.gsb.lat,
        lng: NODE_CONFIG.gsb.lng,
        alt: 0.02,
        text: '🏢 GSB (Canberra)',
        size: 0.9,
        color: '#00e676'
      }
    ];
  }

  // --- Three.js Custom 3D Mesh Builders ---
  function buildSatellite3D(d) {
    const group = new THREE.Group();

    // Metallic gold central spacecraft bus
    const busGeo = new THREE.BoxGeometry(2.4, 2.4, 3.2);
    const busMat = new THREE.MeshStandardMaterial({
      color: 0xffd54f,
      metalness: 0.9,
      roughness: 0.2,
      emissive: 0x443300
    });
    const bus = new THREE.Mesh(busGeo, busMat);
    group.add(bus);

    // Blue solar array panels
    const panelGeo = new THREE.BoxGeometry(6.5, 1.8, 0.15);
    const panelMat = new THREE.MeshStandardMaterial({
      color: 0x0d47a1,
      metalness: 0.8,
      roughness: 0.15,
      emissive: 0x001944
    });

    const panelL = new THREE.Mesh(panelGeo, panelMat);
    panelL.position.set(-4.6, 0, 0);
    group.add(panelL);

    const panelR = new THREE.Mesh(panelGeo, panelMat);
    panelR.position.set(4.6, 0, 0);
    group.add(panelR);

    // Nadir antenna dish pointing to Earth
    const dishGeo = new THREE.ConeGeometry(1.2, 1.1, 16, 1, true);
    const dishMat = new THREE.MeshStandardMaterial({
      color: 0xeeeeee,
      metalness: 0.6,
      roughness: 0.3,
      side: THREE.DoubleSide
    });
    const dish = new THREE.Mesh(dishGeo, dishMat);
    dish.rotation.x = Math.PI;
    dish.position.set(0, -1.8, 0);
    group.add(dish);

    // Beacon light
    const isOutage = d.id === 'dtn://sat1/relay' && activeIslState === 'DOWN';
    const beaconGeo = new THREE.SphereGeometry(0.7, 12, 12);
    const beaconMat = new THREE.MeshBasicMaterial({
      color: isOutage ? 0xff1744 : 0x00e5ff
    });
    const beacon = new THREE.Mesh(beaconGeo, beaconMat);
    beacon.position.set(0, 2.0, 0);
    group.add(beacon);

    group.userData = d;
    return group;
  }

  function buildGroundStation3D(d) {
    const group = new THREE.Group();

    // Radome base
    const domeGeo = new THREE.SphereGeometry(2.0, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshStandardMaterial({
      color: 0xdde6ed,
      metalness: 0.2,
      roughness: 0.4
    });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    group.add(dome);

    // Steerable antenna dish
    const dishGeo = new THREE.CylinderGeometry(0.1, 1.8, 0.5, 16);
    const dishMat = new THREE.MeshStandardMaterial({
      color: d.color === '#00e676' ? 0x00e676 : 0x00e5ff,
      metalness: 0.7,
      roughness: 0.3
    });
    const dish = new THREE.Mesh(dishGeo, dishMat);
    dish.position.set(0, 1.9, 0);
    dish.rotation.z = Math.PI / 5;
    group.add(dish);

    // Ground platform ring
    const ringGeo = new THREE.RingGeometry(2.1, 2.6, 24);
    const ringMat = new THREE.MeshBasicMaterial({
      color: d.color === '#00e676' ? 0x00e676 : 0x00e5ff,
      side: THREE.DoubleSide
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    group.add(ring);

    group.userData = d;
    return group;
  }

  // --- Initialise 3D Globe Visualization ---
  function init3DGlobe() {
    const container = document.getElementById('globe-viewport');
    if (!container) return;

    worldGlobe = Globe()(container)
      .globeImageUrl('/static/textures/earth-night.jpg')
      .backgroundImageUrl('/static/textures/night-sky.png')
      .showAtmosphere(true)
      .atmosphereColor('#2979ff')
      .atmosphereAltitude(0.25)
      // Custom 3D Spacecraft & Antennas
      .customLayerData(getNodesData())
      .customThreeObject(d => {
        return d.type === 'satellite_relay' ? buildSatellite3D(d) : buildGroundStation3D(d);
      })
      .customThreeObjectUpdate((obj, d) => {
        Object.assign(obj.position, worldGlobe.getCoords(d.lat, d.lng, d.alt));
      })
      // 3D Communication Arcs
      .arcsData(getLinksData())
      .arcStartLat(d => d.startLat)
      .arcStartLng(d => d.startLng)
      .arcStartAltitude(d => d.startAlt)
      .arcEndLat(d => d.endLat)
      .arcEndLng(d => d.endLng)
      .arcEndAltitude(d => d.endAlt)
      .arcColor(d => d.color)
      .arcAltitude(d => d.altitude)
      .arcStroke(d => d.stroke)
      .arcDashLength(d => d.dashLength)
      .arcDashGap(d => d.dashGap)
      .arcDashAnimateTime(d => d.animateTime)
      // Pulsing Node Rings
      .ringsData(getRingsData())
      .ringLat(d => d.lat)
      .ringLng(d => d.lng)
      .ringAltitude(d => d.alt)
      .ringColor(d => d.color)
      .ringMaxRadius(d => d.maxRadius)
      .ringPropagationSpeed(d => d.speed)
      .ringRepeatPeriod(d => d.period)
      // Node Billboard Labels
      .labelsData(getLabelsData())
      .labelLat(d => d.lat)
      .labelLng(d => d.lng)
      .labelAltitude(d => d.alt)
      .labelText(d => d.text)
      .labelSize(d => d.size)
      .labelColor(d => d.color)
      .labelDotRadius(0.3)
      // Interaction Listeners
      .onCustomLayerClick((d) => selectNode(d))
      .onGlobeClick(() => deselectNode());

    // Configure OrbitControls
    const controls = worldGlobe.controls();
    if (controls) {
      controls.autoRotate = false;
      controls.autoRotateSpeed = 0.6;
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 140;
      controls.maxDistance = 500;
    }

    // Set initial camera focus framing the space network
    worldGlobe.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.2 }, 1500);

    // Handle container resize
    window.addEventListener('resize', () => {
      if (worldGlobe && container) {
        worldGlobe.width(container.clientWidth);
        worldGlobe.height(container.clientHeight);
      }
    });

    // Orbital Drift Loop
    let lastTime = Date.now();
    (function animateOrbit() {
      const now = Date.now();
      const dt = (now - lastTime) / 1000.0;
      lastTime = now;

      if (isAutoRotating && controls) {
        controls.update();
      }

      requestAnimationFrame(animateOrbit);
    })();
  }

  // --- Dynamic Scene Refresher ---
  function refreshScene() {
    if (!worldGlobe) return;
    worldGlobe.arcsData(getLinksData());
    worldGlobe.customLayerData(getNodesData());
    worldGlobe.ringsData(getRingsData());
    worldGlobe.labelsData(getLabelsData());

    // Update link status badge in HUD
    const hudLinkBadge = document.getElementById('hud-isl-status');
    if (hudLinkBadge) {
      if (activeIslState === 'DOWN') {
        hudLinkBadge.textContent = 'ISL: OUTAGE (SPOOLING)';
        hudLinkBadge.style.color = 'var(--accent-red)';
      } else {
        hudLinkBadge.textContent = 'ISL: ACTIVE (UP)';
        hudLinkBadge.style.color = 'var(--accent-cyan)';
      }
    }
  }

  // --- Camera View Presets ---
  function setCameraView(preset) {
    if (!worldGlobe) return;
    switch (preset) {
      case 'overview':
        worldGlobe.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.3 }, 1200);
        break;
      case 'sat1':
        worldGlobe.pointOfView({ lat: NODE_CONFIG.sat1.lat, lng: NODE_CONFIG.sat1.lng, altitude: 1.1 }, 1000);
        selectNode(NODE_CONFIG.sat1);
        break;
      case 'sat2':
        worldGlobe.pointOfView({ lat: NODE_CONFIG.sat2.lat, lng: NODE_CONFIG.sat2.lng, altitude: 1.1 }, 1000);
        selectNode(NODE_CONFIG.sat2);
        break;
      case 'gsa':
        worldGlobe.pointOfView({ lat: NODE_CONFIG.gsa.lat, lng: NODE_CONFIG.gsa.lng, altitude: 0.7 }, 1000);
        selectNode(NODE_CONFIG.gsa);
        break;
      case 'gsb':
        worldGlobe.pointOfView({ lat: NODE_CONFIG.gsb.lat, lng: NODE_CONFIG.gsb.lng, altitude: 0.7 }, 1000);
        selectNode(NODE_CONFIG.gsb);
        break;
    }
  }

  function toggleAutoRotate() {
    isAutoRotating = !isAutoRotating;
    const btn = document.getElementById('rotate-toggle-btn');
    if (worldGlobe && worldGlobe.controls()) {
      worldGlobe.controls().autoRotate = isAutoRotating;
    }
    if (btn) {
      btn.textContent = isAutoRotating ? 'Auto-Rotate: ON' : 'Auto-Rotate: OFF';
      btn.style.color = isAutoRotating ? 'var(--accent-cyan)' : 'var(--text-muted)';
    }
  }

  // --- Node Inspection Panel ---
  function selectNode(d) {
    selectedNode = d;
    const panel = document.getElementById('node-inspector-hud');
    if (!panel) return;

    const q = queueTelemetry[d.id] || { pending: 0, kb: 0 };
    const t = nodesTelemetry[d.id] || {};

    document.getElementById('insp-node-name').textContent = d.name;
    document.getElementById('insp-node-eid').textContent = d.id;
    document.getElementById('insp-node-type').textContent = d.type.toUpperCase();
    document.getElementById('insp-node-coords').textContent = `${d.lat.toFixed(2)}° N/S, ${d.lng.toFixed(2)}° E/W (Alt: ${d.alt.toFixed(2)})`;
    document.getElementById('insp-node-role').textContent = d.role;

    const statusEl = document.getElementById('insp-node-status');
    if (d.id.includes('sat') && activeIslState === 'DOWN') {
      statusEl.textContent = 'INTERRUPTED (SPOOLING)';
      statusEl.style.color = 'var(--accent-red)';
    } else {
      statusEl.textContent = 'ONLINE / NORMAL';
      statusEl.style.color = 'var(--accent-green)';
    }

    document.getElementById('insp-node-queue').textContent = `${q.pending} bundles (${q.kb} KB)`;

    // Cryptographic Details
    const kemFp = t.active_kem_pk_fingerprint || (d.id.includes('sat') ? 'RELAY_TRANSIT_ONLY' : 'b4a89e1f72c081...');
    const dsaFp = t.active_dsa_pk_fingerprint || (d.id.includes('sat') ? 'UNAUTHORIZED_FOR_L2_DECAP' : '9c34cc27d4ee...');
    document.getElementById('insp-node-kem').textContent = kemFp;
    document.getElementById('insp-node-dsa').textContent = dsaFp;

    panel.style.display = 'block';
  }

  function deselectNode() {
    selectedNode = null;
    const panel = document.getElementById('node-inspector-hud');
    if (panel) panel.style.display = 'none';
  }

  // --- 3D Packet Movement Animation Engine ---
  async function animatePacketDispatch(envelopeId, payloadText, hasFault) {
    if (!worldGlobe || inFlightAnimationActive) return;
    inFlightAnimationActive = true;

    const packetHud = document.getElementById('packet-hud');
    const packetHop = document.getElementById('packet-hop-text');
    const packetStatus = document.getElementById('packet-status-text');
    const packetIdEl = document.getElementById('packet-id-text');

    if (packetHud) {
      packetHud.style.display = 'block';
      packetIdEl.textContent = envelopeId ? envelopeId.slice(0, 8) + '...' : 'DISPATCH-REQ';
    }

    const sleep = (ms) => new Promise(res => setTimeout(res, ms));

    // STEP 1: Uplink GSA -> SAT1
    if (packetHop) packetHop.textContent = 'HOP 1/3: Uplink GSA -> SAT-1 (Polar Orbit)';
    if (packetStatus) packetStatus.textContent = 'Transmitting 5,119 B Post-Quantum Wire Bundle...';

    // Highlight Uplink arc
    worldGlobe.arcsData([
      {
        startLat: NODE_CONFIG.gsa.lat,
        startLng: NODE_CONFIG.gsa.lng,
        startAlt: NODE_CONFIG.gsa.alt,
        endLat: NODE_CONFIG.sat1.lat,
        endLng: NODE_CONFIG.sat1.lng,
        endAlt: NODE_CONFIG.sat1.alt,
        color: ['#ffea00', '#ffea00'],
        altitude: 0.22,
        stroke: 4.5,
        dashLength: 0.9,
        dashGap: 0.1,
        animateTime: 900
      },
      ...getLinksData()
    ]);
    await sleep(950);

    // STEP 2: Spool Ingestion at SAT1
    if (packetHop) packetHop.textContent = 'HOP 1/3 COMPLETED: Ingested at SAT-1 Relay';
    if (packetStatus) packetStatus.textContent = 'Transactional SQLite WAL write committed. Checking ISL link state...';
    refreshScene();
    await sleep(400);

    // Check ISL Link State
    if (activeIslState === 'DOWN') {
      // In-flight hold at SAT-1 due to outage!
      if (packetHop) packetHop.textContent = 'HOLD: ISL Link SAT-1 -> SAT-2 is OCCULTED / DOWN';
      if (packetStatus) {
        packetStatus.textContent = 'Bundle safely spooled in SQLite WAL queue. Awaiting link restoration.';
        packetStatus.style.color = 'var(--accent-red)';
      }
      inFlightAnimationActive = false;
      return;
    }

    // STEP 3: ISL Transit SAT1 -> SAT2
    if (packetHop) packetHop.textContent = 'HOP 2/3: Inter-Satellite Link SAT-1 -> SAT-2';
    if (packetStatus) packetStatus.textContent = 'Transiting space laser ISL. Zero intermediate decryption.';

    worldGlobe.arcsData([
      {
        startLat: NODE_CONFIG.sat1.lat,
        startLng: NODE_CONFIG.sat1.lng,
        startAlt: NODE_CONFIG.sat1.alt,
        endLat: NODE_CONFIG.sat2.lat,
        endLng: NODE_CONFIG.sat2.lng,
        endAlt: NODE_CONFIG.sat2.alt,
        color: ['#ffea00', '#00e676'],
        altitude: 0.45,
        stroke: 5.0,
        dashLength: 0.9,
        dashGap: 0.1,
        animateTime: 1200
      },
      ...getLinksData()
    ]);
    await sleep(1250);

    // STEP 4: Downlink Transit SAT2 -> GSB
    if (packetHop) packetHop.textContent = 'HOP 3/3: Direct Downlink SAT-2 -> GSB (Canberra)';
    if (packetStatus) packetStatus.textContent = 'Entering destination atmosphere. BPv7 Bundle delivery in progress...';

    worldGlobe.arcsData([
      {
        startLat: NODE_CONFIG.sat2.lat,
        startLng: NODE_CONFIG.sat2.lng,
        startAlt: NODE_CONFIG.sat2.alt,
        endLat: NODE_CONFIG.gsb.lat,
        endLng: NODE_CONFIG.gsb.lng,
        endAlt: NODE_CONFIG.gsb.alt,
        color: ['#00e676', '#ffea00'],
        altitude: 0.22,
        stroke: 4.5,
        dashLength: 0.9,
        dashGap: 0.1,
        animateTime: 950
      },
      ...getLinksData()
    ]);
    await sleep(1000);

    // STEP 5: Destination Arrival & Verification at GSB
    if (hasFault) {
      if (packetHop) packetHop.textContent = 'DESTINATION ARRIVAL: L4 Invariant Triggered!';
      if (packetStatus) {
        packetStatus.textContent = '[RECOVERED] NTT Butterfly SEU bit-flip detected! Local snapshot rollback K=1 succeeded!';
        packetStatus.style.color = 'var(--accent-amber)';
      }
    } else {
      if (packetHop) packetHop.textContent = 'DELIVERY CONFIRMED: GSB Verified';
      if (packetStatus) {
        packetStatus.textContent = 'FIPS 203 ML-KEM-768 shared secret decapsulated. ML-DSA-65 signature verified. SDC: 0.';
        packetStatus.style.color = 'var(--accent-green)';
      }
    }

    refreshScene();
    await sleep(2500);

    if (packetHud) {
      packetHud.style.display = 'none';
      if (packetStatus) packetStatus.style.color = 'var(--accent-cyan)';
    }
    inFlightAnimationActive = false;
  }

  // --- Backend Telemetry Ingestion ---
  async function fetchTelemetry() {
    try {
      // 1. Fetch Queue States
      const qRes = await fetch('/api/queue');
      const qData = await qRes.json();
      if (qData.queues) {
        qData.queues.forEach(q => {
          queueTelemetry[q.relay_eid] = {
            pending: q.pending_bundles,
            kb: q.storage_kb
          };
        });
      }

      // 2. Fetch Nodes Status
      const nRes = await fetch('/api/nodes');
      const nData = await nRes.json();
      if (nData.ground_stations) {
        nData.ground_stations.forEach(gs => { nodesTelemetry[gs.eid] = gs; });
      }
      if (nData.satellite_relays) {
        nData.satellite_relays.forEach(sr => { nodesTelemetry[sr.eid] = sr; });
      }

      // 3. Fetch Topology State
      const tRes = await fetch('/api/topology');
      const tData = await tRes.json();
      if (tData.links) {
        const islLink = tData.links.find(l => l.source.includes('sat1') && l.target.includes('sat2'));
        if (islLink && islLink.state) {
          activeIslState = islLink.state;
        }
      }

      refreshScene();
      if (selectedNode) selectNode(selectedNode);
    } catch (e) {
      console.warn('3D Telemetry update error:', e);
    }
  }

  // Hook into WebSocket live events
  function handleWsMessage(eventData) {
    try {
      const msg = typeof eventData === 'string' ? JSON.parse(eventData) : eventData;
      if (msg.type === 'MESSAGE_TRANSMITTED' && msg.record) {
        animatePacketDispatch(msg.record.envelope_id, '', msg.record.fault_recovered);
        fetchTelemetry();
      } else if (msg.type === 'FAULT_STATE_CHANGED') {
        if (msg.fault_type === 'link_outage') activeIslState = 'DOWN';
        if (msg.fault_type === 'link_restore') activeIslState = 'UP';
        fetchTelemetry();
      }
    } catch (e) {
      console.warn('WS handle error:', e);
    }
  }

  // Export functions to global scope
  window.AstraMissionControl3D = {
    init: init3DGlobe,
    setCameraView: setCameraView,
    toggleAutoRotate: toggleAutoRotate,
    selectNode: selectNode,
    deselectNode: deselectNode,
    refreshScene: refreshScene,
    fetchTelemetry: fetchTelemetry,
    handleWsMessage: handleWsMessage,
    animatePacketDispatch: animatePacketDispatch,
    setIslState: (state) => {
      activeIslState = state;
      refreshScene();
    }
  };

  // Auto-init upon DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      init3DGlobe();
      fetchTelemetry();
      setInterval(fetchTelemetry, 3000);
    }, 200);
  });
})();
