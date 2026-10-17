# SpaceY Intelligence — Data Dictionary & Schema Specification

## 1. Feature Classification & Leakage Control

Features are strictly categorized by their availability at prediction time:
- **`PRE_LAUNCH_SAFE`**: Features fully determined and contracted prior to vehicle liftoff. Permitted for predictive modeling.
- **`POST_LAUNCH_OUTCOME`**: Telemetry and recovery outcomes observed only during or after flight. **Excluded from training features** to prevent data leakage.
- **`METADATA_AUDIT`**: Identifiers, dates, and documentation tags preserved for dimensional SQL exploration.

---

## 2. Feature Schema Table

| Feature Name | Data Type | Units / Format | Allowed Values / Bounds | Leakage Category | Description |
|---|---|---|---|---|---|
| `FlightNumber` | `integer` | Sequence # | $\ge 1$ | `PRE_LAUNCH_SAFE` | Sequential launch count in the SpaceX launch history. Captures macro organizational learning and fleet iteration. |
| `Date` | `string` | ISO `YYYY-MM-DD` | Historical dates | `METADATA_AUDIT` | Scheduled launch date. |
| `Year` | `integer` | Year | $2010 - 2029$ | `METADATA_AUDIT` | Calendar year of mission liftoff. |
| `PayloadMass` | `float` | Kilograms (kg) | $0.0 - 25,000.0$ | `PRE_LAUNCH_SAFE` | Total mass of satellites, cargo, and deployers delivered to orbit. |
| `LaunchSite` | `categorical` | String | `CCAFS SLC 40`, `KSC LC 39A`, `VAFB SLC 4E` | `PRE_LAUNCH_SAFE` | Designated orbital launch complex. |
| `Orbit` | `categorical` | String | `LEO`, `ISS`, `GTO`, `PO`, `SSO`, `GEO`, `MEO`, `HEO`, `ES-L1`, `VLEO`, `SO` | `PRE_LAUNCH_SAFE` | Targeted orbital trajectory and insertion energy regime. |
| `Flights` | `integer` | Count | $1 - 25$ | `PRE_LAUNCH_SAFE` | Flight count of this specific first-stage booster ($1 = \text{maiden}$, $\ge 2 = \text{reused}$). |
| `GridFins` | `binary` | $\{0, 1\}$ | $1 = \text{Yes}, 0 = \text{No}$ | `PRE_LAUNCH_SAFE` | Vehicle equipped with steerable hypersonic grid fins for aerodynamic reentry steering. |
| `Legs` | `binary` | $\{0, 1\}$ | $1 = \text{Yes}, 0 = \text{No}$ | `PRE_LAUNCH_SAFE` | Vehicle equipped with deployable carbon-fiber landing legs. |
| `Block` | `integer` | Version | $1 - 5$ | `PRE_LAUNCH_SAFE` | Booster engine and thermal architecture block revision. |
| `Reused` | `binary` | $\{0, 1\}$ | $1 = \text{Yes}, 0 = \text{No}$ | `PRE_LAUNCH_SAFE` | Indicates whether the booster stage is flight-proven ($1$) or newly manufactured ($0$). |
| `Latitude` | `float` | Degrees North | Verified coordinates | `METADATA_AUDIT` | Geographic latitude of the launch complex. |
| `Longitude` | `float` | Degrees West | Verified coordinates | `METADATA_AUDIT` | Geographic longitude of the launch complex. |
| `LandingOutcome`| `categorical` | String | `Success (ASDS)`, `Success (RTLS)`, `Failure`, `No Attempt`, `Ocean Splash` | `POST_LAUNCH_OUTCOME` | Descriptive landing result string. |
| `Class` | `binary` | $\{0, 1\}$ | $1 = \text{Success}, 0 = \text{Failure / Loss}$ | **TARGET VARIABLE** | Binary classification target: $1$ if booster was recovered, $0$ if crashed, lost, or expended. |
| `Era` | `categorical` | String | `Foundational Development (2010-2020)`, `Modern Operational (2023-2024)` | `METADATA_AUDIT` | Dataset origin and technological maturity partition. |

---

## 3. Launch Site Master Coordinates

- **CCAFS SLC 40**: Latitude `28.561857`, Longitude `-80.577366` (Cape Canaveral Space Force Station, FL)
- **KSC LC 39A**: Latitude `28.608058`, Longitude `-80.603956` (Kennedy Space Center, FL)
- **VAFB SLC 4E**: Latitude `34.632834`, Longitude `-120.610746` (Vandenberg Space Force Base, CA)
