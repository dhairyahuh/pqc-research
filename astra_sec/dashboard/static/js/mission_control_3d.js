/**
 * ASTRA-Sec: Professional 3D Satellite Mission Control & Geospatial Network Visualization.
 * Inspired by NASA Open MCT and Aerospace Flight Operations consoles.
 * 
 * Powered by:
 * - Globe.gl (Geospatial Scene & Earth rendering)
 * - Three.js (High-Fidelity 3D Spacecraft & Ground Station Models)
 * - Satellite.js (Real-Time SGP4 Astrodynamics & Orbital Propagation)
 * 100% Offline Air-Gapped Capable.
 */

(function () {
  'use strict';

  // Polyfill Matrix4.determinantAffine for Three.js compatibility with Globe.gl
  if (window.THREE && window.THREE.Matrix4 && !window.THREE.Matrix4.prototype.determinantAffine) {
    window.THREE.Matrix4.prototype.determinantAffine = function () {
      return this.determinant ? this.determinant() : 1;
    };
  }

  // --- Static Ground Station Configurations ---
  const GROUND_STATIONS = {
    gsa: {
      id: 'dtn://gsa/app',
      name: 'Ground Station Alpha (GSA)',
      location: 'Svalbard Satellite Station, Norway (78.23° N, 15.41° E)',
      lat: 78.2297,
      lng: 15.4078,
      alt: 0.015,
      type: 'ground_station',
      classification: 'GROUND_STATION_TERMINAL',
      color: '#00e5ff',
      facility: 'SvalSat Polar Tracking Station',
      elevation: '450 m ASL',
      antenna: '11 m S/X-Band Tracking Radome & Az/El Pedestal',
      role: 'Cryptographic Originator (FIPS 203 ML-KEM-768 Encap / FIPS 204 ML-DSA-65 Signer)'
    },
    gsb: {
      id: 'dtn://gsb/app',
      name: 'Ground Station Bravo (GSB)',
      location: 'Canberra Deep Space Complex, Australia (-35.40° S, 148.98° E)',
      lat: -35.4014,
      lng: 148.9817,
      alt: 0.015,
      type: 'ground_station',
      classification: 'GROUND_STATION_TERMINAL',
      color: '#00e676',
      facility: 'CDSCC Deep Space Communication Complex',
      elevation: '650 m ASL',
      antenna: '34 m Beam Waveguide Parabolic Tracking Dish',
      role: 'Destination Verifier (Monitored ML-KEM-768 Decaps / ML-DSA-65 Verify / ACK Signer)'
    }
  };

  // --- Dynamic Satellite Ephemeris Catalog ---
  let satelliteCatalog = {
    sat1: {
      id: 'dtn://sat1/relay',
      key: 'sat1',
      name: 'ASTRA-LEO-1 (SAT-1 Relay)',
      classification: 'SIMULATED_TESTBED_NODE',
      operational_status: 'ACTIVE_FLIGHT_RELAY',
      orbit_type: 'Polar Sun-Synchronous LEO',
      lat: 52.0,
      lng: 38.0,
      alt: 0.35,
      nominal_alt_km: 550,
      altitude_km: 550,
      velocity_kms: 7.59,
      period_min: 95.6,
      inclination_deg: 97.4,
      sub_sat: '52.00° N, 38.00° E',
      color: '#ffd700',
      bus_type: 'Dual 3-Panel Photovoltaic Array + High-Gain Steerable Reflector Dish',
      role: 'Store-and-Forward Router (SQLite WAL Persistent Spool / RFC 9171 BPv7)',
      satrec: null
    },
    sat2: {
      id: 'dtn://sat2/relay',
      key: 'sat2',
      name: 'ASTRA-LEO-2 (SAT-2 Relay)',
      classification: 'SIMULATED_TESTBED_NODE',
      operational_status: 'ACTIVE_FLIGHT_RELAY',
      orbit_type: 'Inclined LEO Relay Constellation',
      lat: -8.0,
      lng: 92.0,
      alt: 0.35,
      nominal_alt_km: 550,
      altitude_km: 550,
      velocity_kms: 7.59,
      period_min: 95.6,
      inclination_deg: 45.0,
      sub_sat: '8.00° S, 92.00° E',
      color: '#ff9100',
      bus_type: 'Dual 2-Panel Photovoltaic Array + Cross-Dipole ISL Optical / RF Terminal',
      role: 'Store-and-Forward Router (SQLite WAL Persistent Spool / RFC 9171 BPv7)',
      satrec: null
    },
    iss: {
      id: 'norad://25544',
      key: 'iss',
      name: 'ISS (ZARYA) Reference',
      classification: 'REAL_REFERENCE_ORBIT',
      operational_status: 'SPACE_STATION_REFERENCE',
      orbit_type: 'Low Earth Orbit (LEO)',
      lat: 20.0,
      lng: 60.0,
      alt: 0.28,
      nominal_alt_km: 420,
      altitude_km: 420,
      velocity_kms: 7.66,
      period_min: 92.9,
      inclination_deg: 51.64,
      sub_sat: '20.00° N, 60.00° E',
      color: '#00e5ff',
      bus_type: 'Multi-Module Space Station Truss & Solar Array',
      role: 'Real-World Ground Truth Ephemeris Verification Target',
      satrec: null
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
  let returnAckActive = false;
  let propagationTimer = null;
  let activeIslRangeKm = 9585.0;

  // --- High-Fidelity 3D Spacecraft & Ground Station Model Factory ---

  function createSat1Model() {
    const group = new THREE.Group();
    group.scale.set(0.65, 0.65, 0.65);

    // 1. Spacecraft Main Bus (Metallic Gold Foil MLI Cuboid)
    const busGeo = new THREE.BoxGeometry(2.4, 1.6, 1.6);
    const busMat = new THREE.MeshStandardMaterial({
      color: 0xffd700,
      metalness: 0.88,
      roughness: 0.22,
      name: 'GoldFoilMLI'
    });
    const bus = new THREE.Mesh(busGeo, busMat);
    group.add(bus);

    // Avionics Instrument Service Panels (Dark Carbon Top/Bottom)
    const panelGeo = new THREE.BoxGeometry(2.44, 0.35, 1.64);
    const panelMat = new THREE.MeshStandardMaterial({
      color: 0x1a2332,
      metalness: 0.5,
      roughness: 0.5
    });
    const topPanel = new THREE.Mesh(panelGeo, panelMat);
    topPanel.position.y = 0.8;
    const btmPanel = new THREE.Mesh(panelGeo, panelMat);
    btmPanel.position.y = -0.8;
    group.add(topPanel);
    group.add(btmPanel);

    // 2. Dual 3-Panel Photovoltaic Solar Wings
    const wingMat = new THREE.MeshStandardMaterial({
      color: 0x0a3871,
      metalness: 0.4,
      roughness: 0.2
    });
    const wingFrameMat = new THREE.MeshStandardMaterial({
      color: 0xffd700,
      metalness: 0.9,
      roughness: 0.2
    });

    // Left Wing (3 segments)
    const leftWingGroup = new THREE.Group();
    for (let i = 0; i < 3; i++) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.06, 1.1), wingMat);
      panel.position.x = 2.0 + i * 1.5;
      const frame = new THREE.Mesh(new THREE.BoxGeometry(1.44, 0.04, 1.14), wingFrameMat);
      frame.position.copy(panel.position);
      leftWingGroup.add(frame);
      leftWingGroup.add(panel);
    }
    // Left Yoke
    const yokeL = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.8), wingFrameMat);
    yokeL.rotation.z = Math.PI / 2;
    yokeL.position.x = 1.4;
    leftWingGroup.add(yokeL);
    group.add(leftWingGroup);

    // Right Wing (3 segments)
    const rightWingGroup = new THREE.Group();
    for (let i = 0; i < 3; i++) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.06, 1.1), wingMat);
      panel.position.x = -(2.0 + i * 1.5);
      const frame = new THREE.Mesh(new THREE.BoxGeometry(1.44, 0.04, 1.14), wingFrameMat);
      frame.position.copy(panel.position);
      rightWingGroup.add(frame);
      rightWingGroup.add(panel);
    }
    // Right Yoke
    const yokeR = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.8), wingFrameMat);
    yokeR.rotation.z = Math.PI / 2;
    yokeR.position.x = -1.4;
    rightWingGroup.add(yokeR);
    group.add(rightWingGroup);

    // 3. High-Gain Parabolic Reflector Dish (Nadir-Pointing)
    const dishMat = new THREE.MeshStandardMaterial({
      color: 0xf0f4f8,
      metalness: 0.6,
      roughness: 0.3,
      side: THREE.DoubleSide
    });
    const dish = new THREE.Mesh(new THREE.ConeGeometry(1.3, 0.45, 24, 1, true), dishMat);
    dish.rotation.x = Math.PI; // point towards nadir
    dish.position.set(0, 1.4, 0.4);
    group.add(dish);

    // Feed Horn & Boom
    const hornMat = new THREE.MeshStandardMaterial({ color: 0x00e5ff, metalness: 0.8, roughness: 0.2 });
    const feedHorn = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.12, 0.6, 12), hornMat);
    feedHorn.position.set(0, 1.25, 0.4);
    group.add(feedHorn);

    // 4. Optical Crosslink Laser Terminal (Pointing on Z axis)
    const optMat = new THREE.MeshStandardMaterial({ color: 0x00e5ff, emissive: 0x00838f, roughness: 0.2 });
    const optTerminal = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.4, 16), optMat);
    optTerminal.rotation.x = Math.PI / 2;
    optTerminal.position.set(0.6, 0, 0.9);
    group.add(optTerminal);

    // 5. Zenith Omni Beacon Mast
    const mastMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.7 });
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.0), mastMat);
    mast.position.set(0, -1.2, 0);
    const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 12), new THREE.MeshBasicMaterial({ color: 0xffd700 }));
    beacon.position.set(0, -1.7, 0);
    group.add(mast);
    group.add(beacon);

    return group;
  }

  function createSat2Model() {
    const group = new THREE.Group();
    group.scale.set(0.65, 0.65, 0.65);

    // 1. Spacecraft Main Bus (Octagonal Cylindrical Bus with Silver Titanium & Gold Trim)
    const busGeo = new THREE.CylinderGeometry(1.15, 1.15, 2.2, 8);
    const busMat = new THREE.MeshStandardMaterial({
      color: 0xcfd8dc,
      metalness: 0.85,
      roughness: 0.25,
      name: 'TitaniumBus'
    });
    const bus = new THREE.Mesh(busGeo, busMat);
    group.add(bus);

    // Gold Thermal Blanket Trim Rings
    const ringMat = new THREE.MeshStandardMaterial({ color: 0xff9100, metalness: 0.9, roughness: 0.2 });
    const ring1 = new THREE.Mesh(new THREE.TorusGeometry(1.16, 0.06, 8, 8), ringMat);
    ring1.rotation.x = Math.PI / 2;
    ring1.position.y = 0.7;
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(1.16, 0.06, 8, 8), ringMat);
    ring2.rotation.x = Math.PI / 2;
    ring2.position.y = -0.7;
    group.add(ring1);
    group.add(ring2);

    // 2. Dual 2-Panel Solar Wings
    const wingMat = new THREE.MeshStandardMaterial({ color: 0x0a3871, metalness: 0.4, roughness: 0.2 });
    const wingFrameMat = new THREE.MeshStandardMaterial({ color: 0xff9100, metalness: 0.8, roughness: 0.3 });

    // Left Wing (2 wide panels)
    const leftWing = new THREE.Group();
    for (let i = 0; i < 2; i++) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.06, 1.2), wingMat);
      panel.position.x = 1.9 + i * 1.7;
      const frame = new THREE.Mesh(new THREE.BoxGeometry(1.64, 0.04, 1.24), wingFrameMat);
      frame.position.copy(panel.position);
      leftWing.add(frame);
      leftWing.add(panel);
    }
    const yokeL = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.8), wingFrameMat);
    yokeL.rotation.z = Math.PI / 2;
    yokeL.position.x = 1.4;
    leftWing.add(yokeL);
    group.add(leftWing);

    // Right Wing (2 wide panels)
    const rightWing = new THREE.Group();
    for (let i = 0; i < 2; i++) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.06, 1.2), wingMat);
      panel.position.x = -(1.9 + i * 1.7);
      const frame = new THREE.Mesh(new THREE.BoxGeometry(1.64, 0.04, 1.24), wingFrameMat);
      frame.position.copy(panel.position);
      rightWing.add(frame);
      rightWing.add(panel);
    }
    const yokeR = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.8), wingFrameMat);
    yokeR.rotation.z = Math.PI / 2;
    yokeR.position.x = -1.4;
    rightWing.add(yokeR);
    group.add(rightWing);

    // 3. Dual Horn Antennas + Cross-Dipole
    const hornMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.7, roughness: 0.2 });
    const horn1 = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.7, 16, 1, true), hornMat);
    horn1.position.set(0.4, 1.3, 0);
    const horn2 = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.7, 16, 1, true), hornMat);
    horn2.position.set(-0.4, 1.3, 0);
    group.add(horn1);
    group.add(horn2);

    // Cross-Dipole Booms
    const dipoleMat = new THREE.MeshStandardMaterial({ color: 0xff9100, metalness: 0.9 });
    const dipole1 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.6), dipoleMat);
    dipole1.rotation.z = Math.PI / 4;
    dipole1.position.set(0, 1.4, 0.4);
    const dipole2 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.6), dipoleMat);
    dipole2.rotation.z = -Math.PI / 4;
    dipole2.position.set(0, 1.4, 0.4);
    group.add(dipole1);
    group.add(dipole2);

    // 4. Dual Aft Thruster Bells (Burnt Titanium)
    const thrustMat = new THREE.MeshStandardMaterial({ color: 0x3e2723, metalness: 0.9, roughness: 0.4 });
    const nozzle1 = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.5, 12, 1, true), thrustMat);
    nozzle1.rotation.x = Math.PI;
    nozzle1.position.set(0.35, -1.35, 0);
    const nozzle2 = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.5, 12, 1, true), thrustMat);
    nozzle2.rotation.x = Math.PI;
    nozzle2.position.set(-0.35, -1.35, 0);
    group.add(nozzle1);
    group.add(nozzle2);

    // Optical ISL Terminal matching SAT-1
    const optMat = new THREE.MeshStandardMaterial({ color: 0xff9100, emissive: 0xe65100, roughness: 0.2 });
    const optTerminal = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.4, 16), optMat);
    optTerminal.rotation.x = Math.PI / 2;
    optTerminal.position.set(0, 0, 1.25);
    group.add(optTerminal);

    return group;
  }

  function createISSModel() {
    const group = new THREE.Group();
    group.scale.set(0.5, 0.5, 0.5);

    // Long Integrated Truss Structure
    const trussMat = new THREE.MeshStandardMaterial({ color: 0x90a4ae, metalness: 0.6, roughness: 0.4 });
    const truss = new THREE.Mesh(new THREE.BoxGeometry(8.4, 0.25, 0.25), trussMat);
    group.add(truss);

    // Pressurized Habitat Modules (Zarya / Unity Cross)
    const modMat = new THREE.MeshStandardMaterial({ color: 0xe0e0e0, metalness: 0.7, roughness: 0.3 });
    const mod1 = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 2.4, 16), modMat);
    mod1.rotation.z = Math.PI / 2;
    const mod2 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.8, 16), modMat);
    mod2.rotation.x = Math.PI / 2;
    group.add(mod1);
    group.add(mod2);

    // 4 Massive Solar Array Wings (Bronze / Dark Photovoltaic)
    const solMat = new THREE.MeshStandardMaterial({ color: 0xbcaaa4, metalness: 0.5, roughness: 0.2 });
    [-3.4, -2.4, 2.4, 3.4].forEach(x => {
      const sol = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.04, 2.6), solMat);
      sol.position.set(x, 0, 0);
      group.add(sol);
    });

    const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 12), new THREE.MeshBasicMaterial({ color: 0x00e5ff }));
    beacon.position.set(0, 0.6, 0);
    group.add(beacon);

    return group;
  }

  function createGSAModel() {
    // Svalbard SvalSat Geodesic Radome & Tower
    const group = new THREE.Group();
    group.scale.set(0.5, 0.5, 0.5);

    // Reinforced Concrete Base Pedestal
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x37474f, roughness: 0.8 });
    const base = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 2.2, 0.9, 16), baseMat);
    base.position.y = 0.45;
    group.add(base);

    // Geodesic Radome (High-Polygon Faceted Translucent White Sphere)
    const domeMat = new THREE.MeshStandardMaterial({
      color: 0xe0f7fa,
      roughness: 0.4,
      metalness: 0.1,
      transparent: true,
      opacity: 0.92
    });
    const dome = new THREE.Mesh(new THREE.IcosahedronGeometry(1.6, 2), domeMat);
    dome.position.y = 1.5;
    group.add(dome);

    // Calibration Whip Antenna & Perimeter Beacon
    const whip = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.4), new THREE.MeshBasicMaterial({ color: 0x00e5ff }));
    whip.position.set(1.4, 1.2, 0);
    group.add(whip);

    const light = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), new THREE.MeshBasicMaterial({ color: 0x00e5ff }));
    light.position.set(0, 3.1, 0);
    group.add(light);

    return group;
  }

  function createGSBModel() {
    // Canberra 34m Beam Waveguide Parabolic Tracking Dish
    const group = new THREE.Group();
    group.scale.set(0.5, 0.5, 0.5);

    // Concrete Operations Building Base
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x263238, roughness: 0.85 });
    const base = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.8, 2.8), baseMat);
    base.position.y = 0.4;
    group.add(base);

    // Azimuth-Elevation Gimbal Fork
    const forkMat = new THREE.MeshStandardMaterial({ color: 0x78909c, metalness: 0.7, roughness: 0.3 });
    const forkBase = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1.0, 0.7, 16), forkMat);
    forkBase.position.y = 1.0;
    group.add(forkBase);

    // Parabolic Dish (Open Reflector Concave)
    const dishMat = new THREE.MeshStandardMaterial({
      color: 0xf5f5f5,
      metalness: 0.5,
      roughness: 0.3,
      side: THREE.DoubleSide
    });
    const dish = new THREE.Mesh(new THREE.SphereGeometry(2.0, 24, 16, 0, Math.PI * 2, 0, Math.PI / 3), dishMat);
    dish.rotation.x = Math.PI / 4; // Angled tracking elevation
    dish.position.set(0, 2.2, 0);
    group.add(dish);

    // Sub-reflector Tripod Feed
    const feedMat = new THREE.MeshStandardMaterial({ color: 0x00e676, metalness: 0.8 });
    const feed = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.6, 12), feedMat);
    feed.rotation.x = -Math.PI / 4;
    feed.position.set(0, 2.6, 0.5);
    group.add(feed);

    return group;
  }

  function create3DModelForNode(node) {
    if (!window.THREE) return new THREE.Group();
    if (node.key === 'sat1' || (node.id && node.id.includes('sat1'))) {
      return createSat1Model();
    } else if (node.key === 'sat2' || (node.id && node.id.includes('sat2'))) {
      return createSat2Model();
    } else if (node.key === 'iss') {
      return createISSModel();
    } else if (node.id === 'dtn://gsa/app' || node.key === 'gsa') {
      return createGSAModel();
    } else if (node.id === 'dtn://gsb/app' || node.key === 'gsb') {
      return createGSBModel();
    }
    // Fallback satellite mesh
    return createSat1Model();
  }

  // --- 3D Orbital Trajectory Polyline Generator (SGP4 Propagation) ---

  function getOrbitalTracks() {
    const tracks = [];
    if (!window.satellite) return tracks;

    const now = new Date();

    // SAT-1 Track (Polar Sun-Synchronous LEO ~95.6 min)
    if (satelliteCatalog.sat1 && satelliteCatalog.sat1.satrec) {
      const points = [];
      const periodMin = satelliteCatalog.sat1.period_min || 95.6;
      const stepSec = (periodMin * 60) / 72; // 72 segments
      for (let i = 0; i <= 72; i++) {
        const t = new Date(now.getTime() + i * stepSec * 1000);
        const y = t.getUTCFullYear(), m = t.getUTCMonth() + 1, d = t.getUTCDate();
        const hr = t.getUTCHours(), mn = t.getUTCMinutes(), sc = t.getUTCSeconds();
        const pv = satellite.propagate(satelliteCatalog.sat1.satrec, y, m, d, hr, mn, sc);
        if (pv && pv.position) {
          const gmst = satellite.gstime(y, m, d, hr, mn, sc);
          const geo = satellite.eciToGeodetic(pv.position, gmst);
          points.push([
            satellite.degreesLat(geo.latitude),
            satellite.degreesLong(geo.longitude),
            Math.max(0.15, geo.height / 6371.0)
          ]);
        }
      }
      if (points.length > 2) {
        tracks.push({
          id: 'orbit-sat1',
          name: 'SAT-1 Polar Sun-Sync LEO (97.4°)',
          color: '#ffd700',
          stroke: 1.8,
          dashLength: 0.9,
          dashGap: 0.1,
          points: points
        });
      }
    }

    // SAT-2 Track (Inclined LEO ~95.6 min)
    if (satelliteCatalog.sat2 && satelliteCatalog.sat2.satrec) {
      const points = [];
      const periodMin = satelliteCatalog.sat2.period_min || 95.6;
      const stepSec = (periodMin * 60) / 72;
      for (let i = 0; i <= 72; i++) {
        const t = new Date(now.getTime() + i * stepSec * 1000);
        const y = t.getUTCFullYear(), m = t.getUTCMonth() + 1, d = t.getUTCDate();
        const hr = t.getUTCHours(), mn = t.getUTCMinutes(), sc = t.getUTCSeconds();
        const pv = satellite.propagate(satelliteCatalog.sat2.satrec, y, m, d, hr, mn, sc);
        if (pv && pv.position) {
          const gmst = satellite.gstime(y, m, d, hr, mn, sc);
          const geo = satellite.eciToGeodetic(pv.position, gmst);
          points.push([
            satellite.degreesLat(geo.latitude),
            satellite.degreesLong(geo.longitude),
            Math.max(0.15, geo.height / 6371.0)
          ]);
        }
      }
      if (points.length > 2) {
        tracks.push({
          id: 'orbit-sat2',
          name: 'SAT-2 Inclined Relay Orbit (45.0°)',
          color: '#ff9100',
          stroke: 1.8,
          dashLength: 0.9,
          dashGap: 0.1,
          points: points
        });
      }
    }

    // ISS Reference Track (~92.9 min)
    if (satelliteCatalog.iss && satelliteCatalog.iss.satrec) {
      const points = [];
      const periodMin = satelliteCatalog.iss.period_min || 92.9;
      const stepSec = (periodMin * 60) / 72;
      for (let i = 0; i <= 72; i++) {
        const t = new Date(now.getTime() + i * stepSec * 1000);
        const y = t.getUTCFullYear(), m = t.getUTCMonth() + 1, d = t.getUTCDate();
        const hr = t.getUTCHours(), mn = t.getUTCMinutes(), sc = t.getUTCSeconds();
        const pv = satellite.propagate(satelliteCatalog.iss.satrec, y, m, d, hr, mn, sc);
        if (pv && pv.position) {
          const gmst = satellite.gstime(y, m, d, hr, mn, sc);
          const geo = satellite.eciToGeodetic(pv.position, gmst);
          points.push([
            satellite.degreesLat(geo.latitude),
            satellite.degreesLong(geo.longitude),
            Math.max(0.12, geo.height / 6371.0)
          ]);
        }
      }
      if (points.length > 2) {
        tracks.push({
          id: 'orbit-iss',
          name: 'ISS Reference LEO (51.64°)',
          color: '#00e5ff',
          stroke: 1.0,
          dashLength: 0.4,
          dashGap: 0.2,
          points: points
        });
      }
    }

    return tracks;
  }

  // --- Dynamic 3D Communication Link Arcs ---
  function getLinksData() {
    const isOutage = activeIslState === 'DOWN';
    const sat1 = satelliteCatalog.sat1;
    const sat2 = satelliteCatalog.sat2;
    const gsa = GROUND_STATIONS.gsa;
    const gsb = GROUND_STATIONS.gsb;

    const links = [
      {
        id: 'uplink',
        name: 'Uplink (GSA -> SAT-1)',
        protocol: 'RFC 9171 BPv7 / BPSec',
        startLat: gsa.lat,
        startLng: gsa.lng,
        startAlt: gsa.alt,
        endLat: sat1.lat,
        endLng: sat1.lng,
        endAlt: sat1.alt,
        color: ['#00e5ff', '#2979ff'],
        altitude: 0.25,
        stroke: 2.8,
        dashLength: 0.45,
        dashGap: 0.15,
        animateTime: 1600
      },
      {
        id: 'isl',
        name: 'Inter-Satellite Crosslink (ISL: SAT-1 -> SAT-2)',
        protocol: 'Direct Optical/RF ISL',
        startLat: sat1.lat,
        startLng: sat1.lng,
        startAlt: sat1.alt,
        endLat: sat2.lat,
        endLng: sat2.lng,
        endAlt: sat2.alt,
        color: isOutage ? ['#ff1744', '#b71c1c'] : ['#00e5ff', '#00e676'],
        altitude: 0.52,
        stroke: isOutage ? 3.5 : 2.8,
        dashLength: isOutage ? 0.06 : 0.5,
        dashGap: isOutage ? 0.35 : 0.15,
        animateTime: isOutage ? 0 : 2000
      },
      {
        id: 'downlink',
        name: 'Downlink (SAT-2 -> GSB)',
        protocol: 'RFC 9171 BPv7 E2E',
        startLat: sat2.lat,
        startLng: sat2.lng,
        startAlt: sat2.alt,
        endLat: gsb.lat,
        endLng: gsb.lng,
        endAlt: gsb.alt,
        color: ['#ff9100', '#00e676'],
        altitude: 0.25,
        stroke: 2.8,
        dashLength: 0.45,
        dashGap: 0.15,
        animateTime: 1600
      }
    ];

    if (returnAckActive) {
      links.push({
        id: 'ack-return',
        name: 'Return ACK Verification Path (GSB -> GSA)',
        protocol: 'Signed Cryptographic ACK',
        startLat: gsb.lat,
        startLng: gsb.lng,
        startAlt: gsb.alt,
        endLat: gsa.lat,
        endLng: gsa.lng,
        endAlt: gsa.alt,
        color: ['#00e676', '#ffd700', '#00e5ff'],
        altitude: 0.60,
        stroke: 3.2,
        dashLength: 0.6,
        dashGap: 0.1,
        animateTime: 1200
      });
    }

    return links;
  }

  // --- Node Objects Data for 3D Custom Rendering ---
  function getSpacecraftAndStationObjects() {
    const objects = [];

    // Ground Stations
    Object.values(GROUND_STATIONS).forEach(g => {
      objects.push({
        ...g,
        radius: 1.2
      });
    });

    // Satellites
    Object.values(satelliteCatalog).forEach(s => {
      objects.push({
        ...s,
        radius: 1.4
      });
    });

    return objects;
  }

  // --- 3D Billboard Labels ---
  function getLabelsData() {
    const isOutage = activeIslState === 'DOWN';
    const sat1Queue = queueTelemetry['dtn://sat1/relay'] ? queueTelemetry['dtn://sat1/relay'].pending : 0;
    const sat2Queue = queueTelemetry['dtn://sat2/relay'] ? queueTelemetry['dtn://sat2/relay'].pending : 0;

    return [
      {
        lat: GROUND_STATIONS.gsa.lat,
        lng: GROUND_STATIONS.gsa.lng,
        alt: 0.035,
        text: '📡 GSA (Svalbard SvalSat)',
        color: '#00e5ff'
      },
      {
        lat: satelliteCatalog.sat1.lat,
        lng: satelliteCatalog.sat1.lng,
        alt: satelliteCatalog.sat1.alt + 0.09,
        text: `🛰️ SAT-1 [LEO-1 Polar] ${sat1Queue > 0 ? '(' + sat1Queue + ' spooled)' : ''}`,
        color: isOutage ? '#ffab00' : '#ffd700'
      },
      {
        lat: satelliteCatalog.sat2.lat,
        lng: satelliteCatalog.sat2.lng,
        alt: satelliteCatalog.sat2.alt + 0.09,
        text: `🛰️ SAT-2 [LEO-2 Inclined] ${sat2Queue > 0 ? '(' + sat2Queue + ' spooled)' : ''}`,
        color: isOutage ? '#ff1744' : '#ff9100'
      },
      {
        lat: GROUND_STATIONS.gsb.lat,
        lng: GROUND_STATIONS.gsb.lng,
        alt: 0.035,
        text: '🏢 GSB (Canberra CDSCC)',
        color: '#00e676'
      },
      {
        lat: satelliteCatalog.iss.lat,
        lng: satelliteCatalog.iss.lng,
        alt: satelliteCatalog.iss.alt + 0.08,
        text: '🛸 ISS (Zarya Reference)',
        color: '#00e5ff'
      }
    ];
  }

  // --- Ground Station & Footprint Pulsing Rings ---
  function getRingsData() {
    const isOutage = activeIslState === 'DOWN';
    return [
      {
        lat: GROUND_STATIONS.gsa.lat,
        lng: GROUND_STATIONS.gsa.lng,
        alt: 0.015,
        color: '#00e5ff',
        maxRadius: 5.5,
        speed: 1.5,
        period: 1400
      },
      {
        lat: satelliteCatalog.sat1.lat,
        lng: satelliteCatalog.sat1.lng,
        alt: satelliteCatalog.sat1.alt,
        color: isOutage ? '#ffab00' : '#ffd700',
        maxRadius: 7.5,
        speed: isOutage ? 2.5 : 1.8,
        period: 1200
      },
      {
        lat: satelliteCatalog.sat2.lat,
        lng: satelliteCatalog.sat2.lng,
        alt: satelliteCatalog.sat2.alt,
        color: isOutage ? '#ff1744' : '#ff9100',
        maxRadius: 7.5,
        speed: isOutage ? 2.5 : 1.8,
        period: 1200
      },
      {
        lat: GROUND_STATIONS.gsb.lat,
        lng: GROUND_STATIONS.gsb.lng,
        alt: 0.015,
        color: '#00e676',
        maxRadius: 5.5,
        speed: 1.5,
        period: 1400
      }
    ];
  }

  // --- SGP4 Continuous Orbital Propagation Loop ---
  function runOrbitalPropagation() {
    if (!window.satellite) return;

    const now = new Date();
    const y = now.getUTCFullYear(), m = now.getUTCMonth() + 1, d = now.getUTCDate();
    const hr = now.getUTCHours(), mn = now.getUTCMinutes(), sc = now.getUTCSeconds();

    // Propagate all satellites
    Object.values(satelliteCatalog).forEach(sat => {
      if (!sat.satrec) return;

      const pv = satellite.propagate(sat.satrec, y, m, d, hr, mn, sc);
      if (pv && pv.position) {
        const gmst = satellite.gstime(y, m, d, hr, mn, sc);
        const geo = satellite.eciToGeodetic(pv.position, gmst);
        
        sat.lat = satellite.degreesLat(geo.latitude);
        sat.lng = satellite.degreesLong(geo.longitude);
        sat.altitude_km = geo.height;
        sat.alt = Math.max(0.12, geo.height / 6371.0);

        if (pv.velocity) {
          sat.velocity_kms = Math.sqrt(pv.velocity.x ** 2 + pv.velocity.y ** 2 + pv.velocity.z ** 2);
        }

        const latDir = sat.lat >= 0 ? 'N' : 'S';
        const lngDir = sat.lng >= 0 ? 'E' : 'W';
        sat.sub_sat = `${Math.abs(sat.lat).toFixed(2)}° ${latDir}, ${Math.abs(sat.lng).toFixed(2)}° ${lngDir}`;
      }
    });

    // Compute Physical ISL Range between SAT-1 and SAT-2
    const s1 = satelliteCatalog.sat1;
    const s2 = satelliteCatalog.sat2;
    if (s1 && s2) {
      const r1 = 6371.0 + s1.altitude_km;
      const r2 = 6371.0 + s2.altitude_km;
      const la1 = (s1.lat * Math.PI) / 180.0, lo1 = (s1.lng * Math.PI) / 180.0;
      const la2 = (s2.lat * Math.PI) / 180.0, lo2 = (s2.lng * Math.PI) / 180.0;
      const x1 = r1 * Math.cos(la1) * Math.cos(lo1), y1 = r1 * Math.cos(la1) * Math.sin(lo1), z1 = r1 * Math.sin(la1);
      const x2 = r2 * Math.cos(la2) * Math.cos(lo2), y2 = r2 * Math.cos(la2) * Math.sin(lo2), z2 = r2 * Math.sin(la2);
      activeIslRangeKm = Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2);

      const islRangeEl = document.getElementById('hud-isl-range');
      if (islRangeEl) {
        islRangeEl.textContent = `${activeIslRangeKm.toFixed(0)} km`;
      }
    }

    // Refresh dynamic scene elements
    if (worldGlobe) {
      worldGlobe.objectsData(getSpacecraftAndStationObjects());
      worldGlobe.arcsData(getLinksData());
      worldGlobe.ringsData(getRingsData());
      worldGlobe.labelsData(getLabelsData());
    }

    // Refresh Inspector if a node is currently selected
    if (selectedNode) {
      selectNode(selectedNode);
    }
  }

  // --- Initialise 3D Globe Visualization ---
  function init3DGlobe() {
    const container = document.getElementById('globe-viewport');
    if (!container) return;

    worldGlobe = Globe()(container)
      .width(container.clientWidth || 800)
      .height(container.clientHeight || 560)
      .globeImageUrl('/static/textures/earth-night.jpg')
      .backgroundImageUrl('/static/textures/night-sky.png')
      .showAtmosphere(true)
      .atmosphereColor('#2979ff')
      .atmosphereAltitude(0.28)
      // Professional 3D Spacecraft and Ground Station Models
      .objectsData(getSpacecraftAndStationObjects())
      .objectLat('lat')
      .objectLng('lng')
      .objectAltitude('alt')
      .objectThreeObject(d => create3DModelForNode(d))
      .objectFacesSurface(true)
      .onObjectClick(d => selectNode(d))
      // 3D Orbital Trajectory Curves
      .pathsData(getOrbitalTracks())
      .pathPoints('points')
      .pathPointLat(p => p[0])
      .pathPointLng(p => p[1])
      .pathPointAlt(p => p[2])
      .pathColor('color')
      .pathStroke('stroke')
      .pathDashLength('dashLength')
      .pathDashGap('dashGap')
      // 3D Billboard Labels
      .labelsData(getLabelsData())
      .labelLat('lat')
      .labelLng('lng')
      .labelAltitude('alt')
      .labelText('text')
      .labelSize(1.15)
      .labelColor(d => d.color || '#ffffff')
      .labelDotRadius(0.35)
      // 3D Communication Arcs
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
      // Pulsing Halos / Ground Rings
      .ringsData(getRingsData())
      .ringLat('lat')
      .ringLng('lng')
      .ringAltitude('alt')
      .ringColor('color')
      .ringMaxRadius('maxRadius')
      .ringPropagationSpeed('speed')
      .ringRepeatPeriod('period')
      .onGlobeClick(() => deselectNode());

    // OrbitControls Configuration
    const controls = worldGlobe.controls();
    if (controls) {
      controls.autoRotate = false;
      controls.autoRotateSpeed = 0.5;
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 140;
      controls.maxDistance = 580;
    }

    // Default Camera Framing (Centered on space constellation & Earth)
    worldGlobe.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.2 }, 1500);

    // Responsive window & panel resizing
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => {
        if (worldGlobe && container && container.clientWidth > 0 && container.clientHeight > 0) {
          worldGlobe.width(container.clientWidth);
          worldGlobe.height(container.clientHeight);
        }
      });
      ro.observe(container);
    }
    window.addEventListener('resize', () => {
      if (worldGlobe && container && container.clientWidth > 0 && container.clientHeight > 0) {
        worldGlobe.width(container.clientWidth);
        worldGlobe.height(container.clientHeight);
      }
    });

    // Ingest TLEs and start real-time propagation loop
    fetchOrbitalCatalog().then(() => {
      runOrbitalPropagation();
      if (!propagationTimer) {
        propagationTimer = setInterval(runOrbitalPropagation, 1000);
      }
    });

    fetchTelemetry();
  }

  // --- Dynamic Scene Refresher ---
  function refreshScene() {
    if (!worldGlobe) return;
    worldGlobe.arcsData(getLinksData());
    worldGlobe.objectsData(getSpacecraftAndStationObjects());
    worldGlobe.ringsData(getRingsData());
    worldGlobe.labelsData(getLabelsData());

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

  // --- Ingest Public TLE Orbital Catalog ---
  async function fetchOrbitalCatalog() {
    try {
      const res = await fetch('/api/orbital/satellites');
      if (!res.ok) return;
      const data = await res.json();

      const ephemStatusEl = document.getElementById('hud-ephemeris-status');
      const ephemSourceEl = document.getElementById('hud-ephemeris-source');
      if (ephemStatusEl) {
        ephemStatusEl.textContent = data.data_freshness_status === 'LIVE_PUBLIC_EPHEMERIS' ? 'LIVE CELESTRAK' : 'SGP4 REAL-TIME';
        ephemStatusEl.style.color = data.data_freshness_status === 'LIVE_PUBLIC_EPHEMERIS' ? 'var(--accent-cyan)' : 'var(--accent-green)';
      }
      if (ephemSourceEl) {
        ephemSourceEl.textContent = data.source ? data.source.replace(/_/g, ' ').slice(0, 18) : 'CelesTrak / TLE';
      }

      if (data.satellites && window.satellite) {
        data.satellites.forEach(s => {
          if (satelliteCatalog[s.id]) {
            satelliteCatalog[s.id].classification = s.classification;
            satelliteCatalog[s.id].nominal_alt_km = s.nominal_altitude_km;
            satelliteCatalog[s.id].period_min = s.period_minutes;
            satelliteCatalog[s.id].inclination_deg = s.inclination_deg;
            satelliteCatalog[s.id].bus_type = s.bus_type;
            satelliteCatalog[s.id].role = s.role;
            if (s.line1 && s.line2) {
              satelliteCatalog[s.id].satrec = satellite.twoline2satrec(s.line1, s.line2);
            }
          }
        });

        // Recompute orbital tracks
        if (worldGlobe) {
          worldGlobe.pathsData(getOrbitalTracks());
        }
      }
    } catch (e) {
      console.warn('Orbital catalog fetch error:', e);
    }
  }

  // --- Camera View Presets ---
  function setCameraView(preset) {
    if (!worldGlobe) return;
    switch (preset) {
      case 'overview':
        worldGlobe.pointOfView({ lat: 25.0, lng: 55.0, altitude: 2.2 }, 1200);
        break;
      case 'sat1':
        worldGlobe.pointOfView({ lat: satelliteCatalog.sat1.lat, lng: satelliteCatalog.sat1.lng, altitude: 0.95 }, 1000);
        selectNode(satelliteCatalog.sat1);
        break;
      case 'sat2':
        worldGlobe.pointOfView({ lat: satelliteCatalog.sat2.lat, lng: satelliteCatalog.sat2.lng, altitude: 0.95 }, 1000);
        selectNode(satelliteCatalog.sat2);
        break;
      case 'gsa':
        worldGlobe.pointOfView({ lat: GROUND_STATIONS.gsa.lat, lng: GROUND_STATIONS.gsa.lng, altitude: 0.75 }, 1000);
        selectNode(GROUND_STATIONS.gsa);
        break;
      case 'gsb':
        worldGlobe.pointOfView({ lat: GROUND_STATIONS.gsb.lat, lng: GROUND_STATIONS.gsb.lng, altitude: 0.75 }, 1000);
        selectNode(GROUND_STATIONS.gsb);
        break;
      case 'iss':
        worldGlobe.pointOfView({ lat: satelliteCatalog.iss.lat, lng: satelliteCatalog.iss.lng, altitude: 0.95 }, 1000);
        selectNode(satelliteCatalog.iss);
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

  // --- Node Inspection HUD & Left Panel Dispatch ---
  function selectNode(d) {
    if (typeof d === 'string') {
      d = GROUND_STATIONS[d] || satelliteCatalog[d] || { id: d, name: d, type: 'UNKNOWN', lat: 0, lng: 0, alt: 0, role: 'Node' };
    }
    if (!d) return;
    selectedNode = d;

    // Trigger external Left-Panel telemetry updater if available
    if (typeof window.onNodeSelected === 'function') {
      window.onNodeSelected(d);
    }

    const panel = document.getElementById('node-inspector-hud');
    if (panel) {
      const q = (d.id && queueTelemetry[d.id]) || { pending: 0, kb: 0 };
      const t = (d.id && nodesTelemetry[d.id]) || {};

      const nameEl = document.getElementById('insp-node-name');
      if (nameEl) nameEl.textContent = d.name || d.id || 'Node Inspector';

      const classEl = document.getElementById('insp-node-class');
      if (classEl) {
        classEl.textContent = d.classification || (d.type === 'satellite' ? 'SIMULATED_TESTBED_NODE' : 'GROUND_STATION_TERMINAL');
        classEl.style.color = d.classification === 'REAL_REFERENCE_ORBIT' ? 'var(--accent-cyan)' : 'var(--accent-gold)';
      }

      const eidEl = document.getElementById('insp-node-eid');
      if (eidEl) eidEl.textContent = d.id || 'N/A';

      const orbitEl = document.getElementById('insp-node-orbit');
      if (orbitEl) orbitEl.textContent = d.orbit_type || (d.type === 'ground_station' ? 'Earth Surface Facility' : 'Low Earth Orbit');

      const coordsEl = document.getElementById('insp-node-coords');
      if (coordsEl) coordsEl.textContent = `${(d.lat || 0).toFixed(2)}° N/S, ${(d.lng || 0).toFixed(2)}° E/W`;

      const altVelEl = document.getElementById('insp-node-alt-vel');
      if (altVelEl) {
        const altStr = d.altitude_km ? `${d.altitude_km.toFixed(1)} km` : (d.elevation || '0.0 km');
        const velStr = d.velocity_kms ? `${d.velocity_kms.toFixed(2)} km/s` : '0.00 km/s (Fixed)';
        altVelEl.textContent = `${altStr} | ${velStr}`;
      }

      const periodIncEl = document.getElementById('insp-node-period-inc');
      if (periodIncEl) {
        if (d.period_min && d.inclination_deg !== undefined) {
          periodIncEl.textContent = `${d.period_min.toFixed(1)} min | ${d.inclination_deg.toFixed(2)}°`;
        } else {
          periodIncEl.textContent = 'Stationary Earth Frame';
        }
      }

      const subsatEl = document.getElementById('insp-node-subsat');
      if (subsatEl) subsatEl.textContent = d.sub_sat || coordsEl.textContent;

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

      const busEl = document.getElementById('insp-node-bus');
      if (busEl) busEl.textContent = d.bus_type || d.antenna || 'Aerospace Terminal';

      const queueEl = document.getElementById('insp-node-queue');
      if (queueEl) queueEl.textContent = `${q.pending} bundles (${q.kb} KB)`;

      const roleEl = document.getElementById('insp-node-role');
      if (roleEl) roleEl.textContent = d.role || 'Network Node';

      panel.style.display = 'block';
    }
  }

  function deselectNode() {
    selectedNode = null;
    const panel = document.getElementById('node-inspector-hud');
    if (panel) panel.style.display = 'none';
  }

  // --- 3D Packet Movement Animation Engine ---
  async function animatePacketDispatch(envelopeId, payloadText, hasFault, scenario) {
    if (!worldGlobe || inFlightAnimationActive) return;
    inFlightAnimationActive = true;

    const packetHud = document.getElementById('packet-hud');
    const packetHop = document.getElementById('packet-hop-text');
    const packetStatus = document.getElementById('packet-status-text');
    const packetIdEl = document.getElementById('packet-id-text');

    if (packetHud) {
      packetHud.style.display = 'block';
      if (packetIdEl) packetIdEl.textContent = envelopeId ? envelopeId.slice(0, 8) + '...' : 'PQC-ENVELOPE';
    }

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Hop 1: GSA -> SAT-1 (Uplink)
    if (packetHop) packetHop.textContent = 'HOP 1/3: Uplink GSA -> SAT-1';
    if (packetStatus) {
      packetStatus.textContent = 'Transmitting 5,119 B Post-Quantum Wire Bundle (ML-KEM-768 Encap + ML-DSA-65 Sign)...';
      packetStatus.style.color = 'var(--accent-cyan)';
    }
    await sleep(900);

    // Hop 2: SAT-1 -> SAT-2 (ISL)
    if (activeIslState === 'DOWN') {
      if (packetHop) packetHop.textContent = 'HOP 2/3: INTER-SATELLITE LINK DOWN';
      if (packetStatus) {
        packetStatus.textContent = 'Halting at SAT-1. Persisting to SQLite WAL Persistent Spool...';
        packetStatus.style.color = 'var(--accent-amber)';
      }
      fetchTelemetry();
      await sleep(1800);
      inFlightAnimationActive = false;
      return;
    }

    if (packetHop) packetHop.textContent = `HOP 2/3: Inter-Satellite Crosslink SAT-1 -> SAT-2 (${activeIslRangeKm.toFixed(0)} km)`;
    if (packetStatus) {
      packetStatus.textContent = 'Forwarding envelope via space optical/RF crosslink (zero intermediate decryption)...';
      packetStatus.style.color = 'var(--accent-cyan)';
    }
    await sleep(1000);

    // Hop 3: SAT-2 -> GSB (Downlink)
    if (packetHop) packetHop.textContent = 'HOP 3/3: Downlink SAT-2 -> Ground Station Bravo (Canberra)';
    if (packetStatus) packetStatus.textContent = 'Receiving bundle at GSB Canberra. Engaging L3/L4 verifier...';
    await sleep(900);

    // Destination Verification & Invariant Checking
    if (hasFault || scenario === 'ntt_transient') {
      if (packetHop) packetHop.textContent = 'L4 ANOMALY: NTT TWIDDLE INVARIANT VIOLATION';
      if (packetStatus) {
        packetStatus.textContent = 'Invariant r != t*zeta detected! Localized register rollback K=1 engaged...';
        packetStatus.style.color = 'var(--accent-amber)';
      }
      await sleep(1100);
      if (packetHop) packetHop.textContent = 'L4 RECOVERY: RETRY K=1 VERIFIED';
      if (packetStatus) {
        packetStatus.textContent = 'Decapsulation retry succeeded. ML-DSA signature authentic. Plaintext accepted.';
        packetStatus.style.color = 'var(--accent-green)';
      }
    } else if (scenario === 'ntt_persistent') {
      if (packetHop) packetHop.textContent = 'L4 FAIL-STOP: PERSISTENT NTT FAULT';
      if (packetStatus) {
        packetStatus.textContent = 'Retry budget exceeded (K > 2). Engaging implicit rejection suppression.';
        packetStatus.style.color = 'var(--accent-red)';
      }
      await sleep(1400);
      inFlightAnimationActive = false;
      return;
    } else if (scenario === 'replay_attack') {
      if (packetHop) packetHop.textContent = 'L6 SECURITY: REPLAY ATTACK DETECTED';
      if (packetStatus) {
        packetStatus.textContent = 'Sequence ID already present in persistent filter. Discarding duplicate envelope.';
        packetStatus.style.color = 'var(--accent-red)';
      }
      await sleep(1400);
      inFlightAnimationActive = false;
      return;
    } else if (scenario === 'tamper_sig') {
      if (packetHop) packetHop.textContent = 'L3 INTEGRITY: SIGNATURE VERIFICATION FAILED';
      if (packetStatus) {
        packetStatus.textContent = 'ML-DSA-65 signature corrupted in transit. Discarding untrusted bundle.';
        packetStatus.style.color = 'var(--accent-red)';
      }
      await sleep(1400);
      inFlightAnimationActive = false;
      return;
    } else {
      if (packetHop) packetHop.textContent = 'DELIVERED: E2E POST-QUANTUM VERIFIED';
      if (packetStatus) {
        packetStatus.textContent = 'ML-DSA-65 Valid | ML-KEM-768 Decaps Valid | AES-GCM Tag Authentic';
        packetStatus.style.color = 'var(--accent-green)';
      }
    }

    // Return ACK animation across reverse path
    returnAckActive = true;
    refreshScene();
    await sleep(900);
    returnAckActive = false;
    refreshScene();

    await sleep(1500);
    if (packetHud) packetHud.style.display = 'none';
    inFlightAnimationActive = false;
  }

  // --- Real-Time Telemetry Polling ---
  async function fetchTelemetry() {
    try {
      const qRes = await fetch('/api/queue');
      const qData = await qRes.json();
      if (qData.queues) {
        qData.queues.forEach(q => {
          queueTelemetry[q.relay_eid] = { pending: q.pending_bundles, kb: q.storage_kb };
        });
      }

      const nRes = await fetch('/api/nodes');
      const nData = await nRes.json();
      if (nData.ground_stations) {
        nData.ground_stations.forEach(g => {
          nodesTelemetry[g.eid] = g;
        });
      }
      if (nData.satellite_relays) {
        nData.satellite_relays.forEach(s => {
          nodesTelemetry[s.eid] = s;
        });
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
        animatePacketDispatch(msg.record.envelope_id, '', msg.record.fault_recovered, msg.record.scenario);
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
    getSatelliteCatalog: () => satelliteCatalog,
    getGroundStations: () => GROUND_STATIONS,
    setIslState: (state) => {
      activeIslState = state;
      refreshScene();
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init3DGlobe);
  } else {
    init3DGlobe();
  }
})();
