/**
 * ASTRA-Sec: 3D Satellite Mission Control & Geospatial Network Visualization.
 * Powered by Globe.gl (Open Source, MIT License - 100% Offline).
 * 
 * Implements real-time 3D Earth, 4-node space constellation topology,
 * dynamic communication links, animated packet hops, interactive node inspection,
 * and live integration with FastAPI backend & WebSocket stream.
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
      alt: 0.35,
      type: 'satellite',
      color: '#ffd700',
      role: 'Store-and-Forward Router (SQLite WAL Persistent Spool)'
    },
    sat2: {
      id: 'dtn://sat2/relay',
      name: 'Satellite Relay 2 (LEO-2)',
      location: 'Inclined LEO Relay Constellation (~550 km)',
      lat: -8.0,
      lng: 92.0,
      alt: 0.35,
      type: 'satellite',
      color: '#ffd700',
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
        stroke: 2.2,
        dashLength: 0.45,
        dashGap: 0.15,
        animateTime: 1800
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
        dashLength: isOutage ? 0.08 : 0.5,
        dashGap: isOutage ? 0.35 : 0.15,
        animateTime: isOutage ? 0 : 2200
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
        stroke: 2.2,
        dashLength: 0.45,
        dashGap: 0.15,
        animateTime: 1800
      }
    ];
  }

  // Node Points Data
  function getPointsData() {
    return Object.values(NODE_CONFIG).map(n => {
      const isSat = n.type === 'satellite';
      const isOutage = n.id.includes('sat') && activeIslState === 'DOWN';
      return {
        ...n,
        radius: isSat ? 0.95 : 0.65,
        color: isOutage ? (n.id.includes('sat1') ? '#ffab00' : '#ff1744') : n.color
      };
    });
  }

  // Node Billboard Labels Data
  function getLabelsData() {
    return [
      {
        lat: NODE_CONFIG.gsa.lat,
        lng: NODE_CONFIG.gsa.lng,
        alt: 0.02,
        text: '📡 GSA (Svalbard)'
      },
      {
        lat: NODE_CONFIG.sat1.lat,
        lng: NODE_CONFIG.sat1.lng,
        alt: NODE_CONFIG.sat1.alt + 0.07,
        text: `🛰️ SAT-1 | LEO-1 ${queueTelemetry['dtn://sat1/relay'] ? '(' + queueTelemetry['dtn://sat1/relay'].pending + ' queued)' : ''}`
      },
      {
        lat: NODE_CONFIG.sat2.lat,
        lng: NODE_CONFIG.sat2.lng,
        alt: NODE_CONFIG.sat2.alt + 0.07,
        text: `🛰️ SAT-2 | LEO-2 ${queueTelemetry['dtn://sat2/relay'] ? '(' + queueTelemetry['dtn://sat2/relay'].pending + ' queued)' : ''}`
      },
      {
        lat: NODE_CONFIG.gsb.lat,
        lng: NODE_CONFIG.gsb.lng,
        alt: 0.02,
        text: '🏢 GSB (Canberra)'
      }
    ];
  }

  // Pulsing Rings Data
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
        color: isOutage ? '#ffab00' : '#ffd700',
        maxRadius: 6.0,
        speed: isOutage ? 2.5 : 1.8,
        period: 1200
      },
      {
        lat: NODE_CONFIG.sat2.lat,
        lng: NODE_CONFIG.sat2.lng,
        alt: NODE_CONFIG.sat2.alt,
        color: isOutage ? '#ff1744' : '#ffd700',
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
      // 3D Nodes as Points
      .pointsData(getPointsData())
      .pointLat('lat')
      .pointLng('lng')
      .pointAltitude('alt')
      .pointColor('color')
      .pointRadius('radius')
      // 3D Billboard Labels
      .labelsData(getLabelsData())
      .labelLat('lat')
      .labelLng('lng')
      .labelAltitude('alt')
      .labelText('text')
      .labelSize(1.1)
      .labelColor(() => '#ffffff')
      .labelDotRadius(0.3)
      // 3D Curved Communication Arcs
      .arcsData(getLinksData())
      .arcStartLat('startLat')
      .arcStartLng('startLng')
      .arcStartAltitude('startAlt')
      .arcEndLat('endLat')
      .arcEndLng('endLng')
      .arcEndAltitude('endAlt')
      .arcColor('color')
      .arcAltitude('altitude')
      .arcStroke('stroke')
      .arcDashLength('dashLength')
      .arcDashGap('dashGap')
      .arcDashAnimateTime('animateTime')
      // Pulsing Halos / Rings
      .ringsData(getRingsData())
      .ringLat('lat')
      .ringLng('lng')
      .ringAltitude('alt')
      .ringColor('color')
      .ringMaxRadius('maxRadius')
      .ringPropagationSpeed('speed')
      .ringRepeatPeriod('period')
      // Interactive Click Listeners
      .onPointClick((d) => selectNode(d))
      .onGlobeClick(() => deselectNode());

    // OrbitControls Configuration
    const controls = worldGlobe.controls();
    if (controls) {
      controls.autoRotate = false;
      controls.autoRotateSpeed = 0.6;
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 140;
      controls.maxDistance = 500;
    }

    // Initial Camera View framing space constellation
    worldGlobe.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.3 }, 1500);

    // Responsive window resizing
    window.addEventListener('resize', () => {
      if (worldGlobe && container) {
        worldGlobe.width(container.clientWidth);
        worldGlobe.height(container.clientHeight);
      }
    });
  }

  // --- Dynamic Scene Refresher ---
  function refreshScene() {
    if (!worldGlobe) return;
    worldGlobe.arcsData(getLinksData());
    worldGlobe.pointsData(getPointsData());
    worldGlobe.ringsData(getRingsData());
    worldGlobe.labelsData(getLabelsData());

    // Update HUD link badge
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
        worldGlobe.pointOfView({ lat: NODE_CONFIG.gsa.lat, lng: NODE_CONFIG.gsa.lng, altitude: 0.8 }, 1000);
        selectNode(NODE_CONFIG.gsa);
        break;
      case 'gsb':
        worldGlobe.pointOfView({ lat: NODE_CONFIG.gsb.lat, lng: NODE_CONFIG.gsb.lng, altitude: 0.8 }, 1000);
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

  // --- Node Inspection HUD ---
  function selectNode(d) {
    if (typeof d === 'string') {
      d = NODE_CONFIG[d] || { id: d, name: d, type: 'UNKNOWN', lat: 0, lng: 0, alt: 0, role: 'Node' };
    }
    if (!d) return;
    selectedNode = d;
    const panel = document.getElementById('node-inspector-hud');
    if (!panel) return;

    const q = (d.id && queueTelemetry[d.id]) || { pending: 0, kb: 0 };
    const t = (d.id && nodesTelemetry[d.id]) || {};

    const nameEl = document.getElementById('insp-node-name');
    if (nameEl) nameEl.textContent = d.name || d.id || 'Node Inspector';
    const eidEl = document.getElementById('insp-node-eid');
    if (eidEl) eidEl.textContent = d.id || 'N/A';
    const typeEl = document.getElementById('insp-node-type');
    if (typeEl) typeEl.textContent = (d.type || 'NODE').toUpperCase();
    const coordsEl = document.getElementById('insp-node-coords');
    if (coordsEl) coordsEl.textContent = `${(d.lat || 0).toFixed(2)}° N/S, ${(d.lng || 0).toFixed(2)}° E/W (Alt: ${(d.alt || 0).toFixed(2)})`;
    const roleEl = document.getElementById('insp-node-role');
    if (roleEl) roleEl.textContent = d.role || 'Network Node';

    const statusEl = document.getElementById('insp-node-status');
    if (statusEl) {
      if (d.id && d.id.includes('sat') && activeIslState === 'DOWN') {
        statusEl.textContent = 'INTERRUPTED (SPOOLING)';
        statusEl.style.color = 'var(--accent-red)';
      } else {
        statusEl.textContent = 'ONLINE / NORMAL';
        statusEl.style.color = 'var(--accent-green)';
      }
    }

    const queueEl = document.getElementById('insp-node-queue');
    if (queueEl) queueEl.textContent = `${q.pending} bundles (${q.kb} KB)`;

    const kemFp = t.active_kem_pk_fingerprint || (d.id && d.id.includes('sat') ? 'RELAY_TRANSIT_ONLY' : 'b4a89e1f72c081...');
    const dsaFp = t.active_dsa_pk_fingerprint || (d.id && d.id.includes('sat') ? 'UNAUTHORIZED_FOR_L2_DECAP' : '9c34cc27d4ee...');
    const kemEl = document.getElementById('insp-node-kem');
    if (kemEl) kemEl.textContent = kemFp;
    const dsaEl = document.getElementById('insp-node-dsa');
    if (dsaEl) dsaEl.textContent = dsaFp;

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
      if (packetIdEl) packetIdEl.textContent = envelopeId ? envelopeId.slice(0, 8) + '...' : 'DISPATCH-REQ';
    }

    const sleep = (ms) => new Promise(res => setTimeout(res, ms));

    // STEP 1: Uplink GSA -> SAT1
    if (packetHop) packetHop.textContent = 'HOP 1/3: Uplink GSA -> SAT-1 (Polar Orbit)';
    if (packetStatus) packetStatus.textContent = 'Transmitting 5,119 B Post-Quantum Wire Bundle...';

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

      const nRes = await fetch('/api/nodes');
      const nData = await nRes.json();
      if (nData.ground_stations) {
        nData.ground_stations.forEach(gs => { nodesTelemetry[gs.eid] = gs; });
      }
      if (nData.satellite_relays) {
        nData.satellite_relays.forEach(sr => { nodesTelemetry[sr.eid] = sr; });
      }

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

  // WebSocket Live Message Listener
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

  // Export to window
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
