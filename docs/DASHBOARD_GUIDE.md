# ASTRA-Sec: Mission Control Operations & Observability Guide

The ASTRA-Sec Mission Control dashboard provides a high-density, real-time observability environment inspired by NASA Open MCT and operational aerospace ground consoles.

---

## 1. Accessing Mission Control

Start the server from the repository root:
```bash
make dashboard
```

Point any modern WebGL-capable browser to:
**`http://127.0.0.1:8000`**

---

## 2. Interface Layout & Navigation (3-Column Architecture)

```
+----------------------------------------------------------------------------------------------------+
| TOP HEADER: Brand, Subsystem Badges, Master Health Indicator, Telemetry Clock (UTC)               |
+----------------------------------------------------------------------------------------------------+
| LEFT COLUMN (280px)     | CENTER COLUMN (Viewport)               | RIGHT COLUMN (340px)            |
| - Node Status (GSA,     | - Interactive 3D Earth & Spacecraft    | - 8-Stage Security Pipeline     |
|   SAT-1, SAT-2, GSB)    | - Real-time SGP4 Astrodynamics HUD     | - L4 NTT Butterfly Monitor      |
| - Link Outage Status    | - Node Inspector Overlay               | - DTN Storage & Wire Meter      |
| - Dispatch Configuration| - Flight Command Dispatcher            | - Tab: Timeline, Life, Forensic |
+----------------------------------------------------------------------------------------------------+
| BOTTOM STRIP: Interactive Flight Command Bar (Scenario Select, Dispatch, Outage Toggle)           |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. The 3D Geospatial Scene & Spacecraft Models

### 3.1 Network Entities Rendered
1. **Ground Station Alpha (GSA)**: Svalbard SvalSat tracking station (78.23° N, 15.41° E). Rendered as an aerospace geodesic radome on a cylindrical base.
2. **SAT-1 (Relay Alpha)**: Polar Sun-Synchronous LEO (~550 km, 97.4° inc). Rendered with a metallic gold foil MLI bus, dual 3-panel solar array wings, and a steerable parabolic dish.
3. **SAT-2 (Relay Bravo)**: Inclined LEO Relay Constellation (~550 km, 45.0° inc). Rendered with an octagonal titanium bus, dual 2-panel solar wings, dual feed horns, and cross-dipole antennas.
4. **Ground Station Bravo (GSB)**: Canberra Deep Space Complex (-35.40° S, 148.98° E). Rendered as a 34-meter beam waveguide parabolic tracking dish on a dual-axis azimuth/elevation gimbal fork.
5. **ISS (Zarya Reference Target)**: Low Earth Orbit reference space station (420 km, 51.64° inc).

### 3.2 Camera Controls
Click the bottom-left camera buttons to position the viewport:
- **`🌐 Orbit View`**: Global framing showing both orbital planes and Earth.
- **`🛰️ SAT-1`**: Focuses on SAT-1 in its polar orbital plane.
- **`🛰️ SAT-2`**: Focuses on SAT-2 in its inclined orbital plane.
- **`📡 GSA`**: Focuses on Svalbard tracking station.
- **`🏢 GSB`**: Focuses on Canberra deep space dish.
- **`🛰️ ISS Ref`**: Focuses on the ISS reference station.
- **`Auto-Rotate: ON/OFF`**: Toggles slow orbital turntable rotation.

---

## 4. Flight Command Scenarios

Select any of the 6 pre-configured operational scenarios in the Flight Command Strip:

| Scenario | Architectural Subsystem Exercised | Visual & Telemetry Outcome |
| :--- | :--- | :--- |
| **1. Nominal E2E Transmission** | Full 7-layer pipeline (FIPS 203/204, AES-GCM, BPv7) | Bundle traverses GSA $\rightarrow$ SAT-1 $\rightarrow$ SAT-2 $\rightarrow$ GSB; signature and AEAD verified; green ACK return arc. |
| **2. ISL Outage & Spooling** | Layer 5/6 DTN persistent spooling (SQLite WAL) | Crosslink severed; packet halts at SAT-1; queued into SQLite WAL storage; spool counter increments. |
| **3. NTT Transient SEU** | Layer 4 dual-transform invariant check ($r \equiv t\zeta$) | Bit-flip detected; amber alert; localized register rollback $K=1$ succeeds; decapsulation accepted. |
| **4. Persistent Fault Fail-Stop** | Layer 4 retry budget exhaustion ($K > 2$) | Repeated bit-flips exceed budget; fail-stop implicit rejection suppression engaged; red alert. |
| **5. Anti-Replay Attack** | Layer 6 persistent sequence filter | Duplicate sequence ID injected; packet discarded before crypto decapsulation; anti-replay alert. |
| **6. Tampered Signature** | Layer 3 ML-DSA-65 verification | 1 bit corrupted in signature; packet dropped at destination; signature failure alert. |

---

## 5. Telemetry Panels & Tabs

- **PQC Security Pipeline (Stages 1–8)**: Real-time visual progress through ADU create $\rightarrow$ KEM encap $\rightarrow$ HKDF $\rightarrow$ AEAD encrypt $\rightarrow$ DSA sign $\rightarrow$ BPv7 framing $\rightarrow$ DTN spool $\rightarrow$ Decaps / Verify.
- **NTT Invariant Monitor**: Displays active Kyber modulus ($q=3329$), live butterfly counters ($9,856$), invariant violation events, and rollback status.
- **DTN Spool Meter**: Displays persistent SQLite WAL storage bytes and pending bundle counts for each relay.
- **Timeline & Audit Tabs**: Switch between Live Event Timeline, Envelope Lifecycle Trace, System Health Diagnostics, and Cryptographic Forensic Journal.
