# SpaceY Intelligence — Problem Statement & Business Context

## 1. Executive Context
SpaceY is a fictional commercial spaceflight and launch-services company competing with SpaceX in the orbital transport sector. In the commercial satellite and government spaceflight industry, pricing and launch economics are fundamentally dictated by **booster reusability**:
- An expendable Falcon 9-class rocket costs approximately **$50M to $62M** to manufacture brand new for every flight.
- Reusing the first-stage booster can reduce hardware replacement costs by **over 50%**, enabling contract prices below $70M while maintaining attractive gross margins.
- However, first-stage booster recovery is not guaranteed. Attempting recovery incurs:
  1. Performance penalties (propellant reserves withheld for the boost-back, entry, and landing burns, reducing maximum payload capacity).
  2. Marine operational costs (deploying autonomous drone ships, tugs, support vessels, and maritime personnel).
  3. Refurbishment and structural requalification costs.
  4. Ocean loss or crash risks in hostile sea states.

## 2. The Decision-Support Problem
When SpaceY bids on a proposed commercial launch contract or evaluates an operational mission scenario, leadership must answer:
1. **Recovery Feasibility**: Given the target orbit, payload mass, launch complex, and vehicle design block, what is the probability that the first stage can be successfully recovered?
2. **Economic Viability**: Based on that recovery probability, what is the expected mission cost? Does attempting recovery provide positive expected value compared to deliberately flying an expendable mission?
3. **Break-Even Threshold**: What minimum landing probability is required before attempting recovery becomes commercially rational?
4. **Attribution & Drivers**: Which technical and operational parameters are driving the prediction, and what sensitivity exists to atmospheric or orbital changes?

## 3. Transformation from Coursera/IBM Capstone
The Coursera/IBM Data Science Capstone explored this concept using historical SpaceX data. However, the original capstone suffered from key limitations:
- It relied on single-model prototypes without leakage-safe pipeline abstractions.
- Legacy student extensions scraped unpartitioned Wikipedia tables, creating massive class imbalance (313 successes vs. 2 failures) and misleading 98% accuracy claims.
- The payload mass feature was disconnected from model scoring due to string one-hot encoding bugs.
- Geospatial coordinates stacked all launch sites onto a single Cape Canaveral location.
- Business economics and decision-making frameworks were absent.

**SpaceY Intelligence** solves these challenges by transforming the capstone into a production-grade, modular, reproducible, testable, and interview-ready applied analytics platform.
