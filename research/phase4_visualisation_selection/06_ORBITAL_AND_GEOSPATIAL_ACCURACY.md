# ASTRA-Sec Phase 4: Orbital Mechanics and Geospatial Accuracy Analysis

## 1. Scientific Rigor in Space Network Visualization

A visual globe with rotating icons is not equivalent to an orbital simulation. In peer-reviewed aerospace and satellite security literature, misrepresenting simulated static endpoints as physical satellites without scientific grounding damages research credibility.

This document formalizes the mathematical distinctions between orbital models and defines how ASTRA-Sec will represent space-segment topology accurately.

---

## 2. Comparison of Orbital Modeling Levels

| Level | Modeling Paradigm | Coordinate Frame | Mathematical Basis | Scientific Validity |
| :--- | :--- | :--- | :--- | :--- |
| **Level 0** | **Static Geospatial Marker** | Earth-Fixed (ECEF: Lat, Lon, Alt) | Fixed geographic coordinates ($h = 550\text{ km}$). | Valid for illustrative network topology; invalid for real orbital dynamics. |
| **Level 1** | **Circular Keplerian Orbit** | Two-Body Central Force | Semi-major axis $a$, inclination $i$, RAAN $\Omega$, true anomaly $\nu$. | Approximate; ignores Earth oblateness ($J_2$), atmospheric drag, and solar pressure. |
| **Level 2** | **SGP4 / SDP4 Propagation** | True Equator, Mean Equinox (TEME / ECI) | NORAD Two-Line Element (TLE) set with $J_2, J_3, J_4$ geopotential perturbations and drag. | **High Aerospace Standard** for LEO / MEO satellites. |
| **Level 3** | **High-Precision Orbit Propagator (HPOP)** | Celestial Intermediate Origin (CIO / GCRF) | Full gravitational field (e.g. EGM2008 $70 \times 70$), third-body gravity, solar radiation pressure. | Flight-dynamics qualification standard (excessive overhead for web visualization). |

---

## 3. The SGP4 / TLE Pipeline Using `satellite.js`

To achieve **Level 2** scientific accuracy without placing computational load on the Python backend, `satellite.js` provides the client-side SGP4 mathematical engine.

### 3.1. Two-Line Element (TLE) Ingestion
A standard NORAD TLE represents a satellite's orbital state at an epoch:
```
1 25544U 98067A   26313.51234567  .00016717  00000-0  10270-3 0  9001
2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49815343482126
```

### 3.2. SGP4 Propagation Algorithm
1. `twoline2satrec()` parses the TLE into orbital inclination ($i_0$), eccentricity ($e_0$), argument of perigee ($\omega_0$), mean anomaly ($M_0$), mean motion ($n_0$), and BSTAR drag term ($B^*$).
2. `propagate(satrec, date)` calculates the satellite state vector (position $\vec{r}$ and velocity $\vec{v}$) in the TEME (True Equator, Mean Equinox) inertial coordinate system at time $t$.
3. `gstime(date)` computes Greenwich Mean Sidereal Time (GMST) $\theta_{gmst}$.
4. Position is transformed from TEME (Inertial) to ECEF (Earth-Centered, Earth-Fixed) via sidereal rotation:
   $$\begin{pmatrix} x_{ecef} \\ y_{ecef} \\ z_{ecef} \end{pmatrix} = \begin{pmatrix} \cos\theta & \sin\theta & 0 \\ -\sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{pmatrix} \begin{pmatrix} x_{teme} \\ y_{teme} \\ z_{teme} \end{pmatrix}$$
5. Geodetic coordinates (latitude $\phi$, longitude $\lambda$, altitude $h$) are calculated accounting for the WGS84 flattening factor:
   $$\lambda = \arctan\left(\frac{y_{ecef}}{x_{ecef}}\right), \quad \phi = \arctan\left(\frac{z_{ecef} + e'^2 b \sin^3 \theta}{p - e^2 a \cos^3 \theta}\right)$$

---

## 4. Architectural Separation in ASTRA-Sec

To maintain strict scientific honesty in research publications and live demonstrations:

```
+-----------------------------------------------------------------------------------+
|                           VISUALIZATION SCENE MODES                               |
+-----------------------------------------------------------------------------------+
|                                        |                                          |
|  MODE 1: EXPERIMENTAL TOPOLOGY VIEW    |  MODE 2: REALISTIC ORBITAL TRACKING VIEW |
|  - Explicitly labeled: SIMULATED       |  - Explicitly labeled: SGP4 PROPAGATED   |
|  - Nodes placed at fixed illustrative  |  - Satellites propagate along true LEO   |
|    geospatial positions for clean      |    trajectories from valid TLE sets.     |
|    packet routing demonstration.       |  - Ground tracks reflect real Earth      |
|  - 100% synchronized with Phase 2/3    |    rotation underneath orbital plane.    |
|    four-node testbed telemetry.        |  - ISL and Ground contacts open/close    |
|                                        |    based on line-of-sight elevation.     |
+-----------------------------------------------------------------------------------+
```

### Protocol Invariant:
The visualization interface must **never display random coordinates and label them as real satellite orbits**. The user must be provided a visible UI toggle between **"Experimental Testbed Topology"** (where node coordinates are configured to clearly show the 4-node store-and-forward flow) and **"SGP4 Constellation Propagation"** (where positions are calculated by `satellite.js`).
