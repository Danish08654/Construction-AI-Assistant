import os
import json
import pickle
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

Path("knowledge_base/documents").mkdir(parents=True, exist_ok=True)
Path("knowledge_base/index").mkdir(parents=True, exist_ok=True)

#  Construction Knowledge Base 
# Synthetic but realistic construction domain documents

CONSTRUCTION_DOCUMENTS = [

#  Building Codes 
{
"title": "IBC 2021 — Occupancy Classifications",
"category": "building_codes",
"content": """
INTERNATIONAL BUILDING CODE 2021 — OCCUPANCY CLASSIFICATIONS

Section 302: Classification Required
All buildings and structures must be classified by the Building Official
according to their use or the character of occupancy.

OCCUPANCY GROUPS:
A — Assembly (A-1 through A-5)
  A-1: Theaters, concert halls. Sprinklers required when occupant load exceeds 300.
  A-2: Restaurants, nightclubs. Occupant load factor: 15 sq ft per person.
  A-3: Churches, community halls. Exit access travel distance: 200 ft unsprinklered.
  A-4: Arenas, skating rinks. Special structural requirements for large spans.
  A-5: Outdoor assembly. Wind and weather exposure requirements apply.

B — Business
  Offices, banks, professional services. Floor area ratio typically 5:1 in commercial zones.
  Minimum plumbing: 1 water closet per 25 occupants for first 50, 1 per 50 thereafter.

E — Educational
  Schools, day care. Occupant load: 20 sq ft per person in classrooms.
  All E occupancies require two means of egress from every classroom.
  Corridor widths minimum 44 inches.

F — Factory and Industrial
  F-1 Moderate Hazard: Woodworking, upholstery. Auto sprinkler if over 12,000 sq ft.
  F-2 Low Hazard: Foundries, gypsum board manufacturing.

H — High Hazard
  H-1 through H-5 based on material quantities. Deflagration hazard requires
  explosion venting per NFPA 68.

I — Institutional
  I-1: Supervised residential care. Sprinklers required throughout.
  I-2: Hospitals, nursing homes. Fire-rated construction, Type I or II only.
  I-3: Prisons. Security vestibule requirements.
  I-4: Day care facilities for >5 persons.

M — Mercantile
  Retail stores, markets. Occupant load: 30 sq ft per person.
  Travel distance to exits: 200 ft unsprinklered, 250 ft sprinklered.

R — Residential
  R-1: Hotels, motels. Sprinklers required throughout per NFPA 13.
  R-2: Apartments, condos (3+ units). Separation between units: 1-hour fire-rated.
  R-3: Single-family, two-family. IRC governs in most jurisdictions.
  R-4: Residential care, 6-16 persons.

S — Storage
  S-1 Moderate Hazard: Auto repair shops, lumber. Height limits apply.
  S-2 Low Hazard: Parking garages. Open parking structures exempt from sprinklers
      if 20% of wall area is open and building height under 75 ft.

U — Utility and Miscellaneous
  Accessory structures, fences, tanks. Minimal code requirements.
"""
},

{
"title": "IBC 2021 — Fire Resistance and Construction Types",
"category": "building_codes",
"content": """
IBC 2021 FIRE RESISTANCE RATINGS AND CONSTRUCTION TYPES

CONSTRUCTION TYPES (Chapter 6):

Type I — Fire Resistive
  IA: Structural frame 3-hour rating. Floors/roofs 2-hour.
      Tallest buildings — no height limit in most occupancies.
  IB: Structural frame 2-hour. Floors/roofs 2-hour.
      Height limit: varies by occupancy, typically unlimited for B, R-2.

Type II — Non-Combustible
  IIA: Structural elements 1-hour rated.
  IIB: No fire-resistance rating required for structural elements.
       Height limit: typically 4-11 stories depending on occupancy.

Type III — Ordinary
  IIIA: Exterior walls non-combustible, interior 1-hour rated.
  IIIB: Exterior walls non-combustible, interior not rated.
       Common for low-rise commercial and mixed-use.

Type IV — Heavy Timber (HT)
  Minimum 8x8 inch columns, 6x10 inch beams.
  Exterior walls non-combustible.
  Mass timber construction qualifies under Type IV-A, B, C provisions added 2021.

Type V — Wood Frame
  VA: All elements 1-hour fire rated. Maximum 3 stories for R-2.
  VB: No fire resistance required. Maximum 2 stories, 9,000 sq ft for R-2.
      Most common for single-family residential.

FIRE-RESISTANCE RATINGS BY ELEMENT:
Bearing walls exterior: Type IA = 3hr, IIA = 1hr, IIIA = 2hr, VA = 1hr
Non-bearing walls exterior: 0hr for most types if >30ft from lot line
Floor construction: Type I = 2hr, Type II = 1hr (IIA), 0hr (IIB)
Roof construction: Type IA = 1.5hr, others typically 0-1hr

FIRE WALLS vs FIRE BARRIERS vs FIRE PARTITIONS:
Fire Wall: Creates separate buildings. Rating: 2-4 hour. Structural independence required.
Fire Barrier: Separates fire areas within building. Rating: 1-3 hour.
Fire Partition: Separates dwelling units, corridors. Rating: 0.5-1 hour.
Smoke Barrier: Limits smoke movement. Rating: 1 hour minimum.
"""
},

{
"title": "Residential Building Permits — Requirements and Process",
"category": "permits",
"content": """
RESIDENTIAL BUILDING PERMIT REQUIREMENTS

WHEN A PERMIT IS REQUIRED:
- New construction of any structure
- Additions increasing floor area or changing footprint
- Structural repairs or modifications
- Electrical work beyond simple fixture replacement
- Plumbing work beyond fixture replacement (new lines, re-routing)
- HVAC installation or replacement of major components
- Roofing replacement (most jurisdictions — check locally)
- Decks attached to dwelling over 200 sq ft or 30 inches above grade
- Retaining walls over 4 feet from bottom of footing to top of wall
- Swimming pools
- Demolition of structures

WHEN A PERMIT IS NOT REQUIRED (typical exemptions):
- Painting, papering, tiling, carpeting, cabinets, countertops
- Prefabricated swimming pools under 24 inches deep
- Swings, playground equipment
- Window replacement (same size, no structural change)
- Fences under 6 feet high (varies by jurisdiction)

PERMIT APPLICATION REQUIREMENTS:
1. Completed application form
2. Site plan showing property lines, setbacks, existing structures
3. Construction drawings (may require architect/engineer stamp for commercial)
4. Energy compliance forms (IECC compliance)
5. Soils report if required (expansive soils, hillside sites)
6. Structural calculations for non-prescriptive designs
7. Application fee (typically $500-$5,000 depending on project value)

PERMIT FEES (typical calculation):
Valuation-based: 0.5%-2% of construction value
Flat fee table: Small projects have fixed fees
Unit-based: Per square foot or per unit

INSPECTION SEQUENCE:
1. Footing inspection — before pouring concrete
2. Foundation inspection — walls formed, before backfill
3. Underground plumbing — before covering
4. Rough framing — all structural framing complete
5. Rough electrical — wiring complete before insulation
6. Rough plumbing — supply and drain lines
7. Rough mechanical — HVAC ducts and equipment
8. Insulation inspection — before drywall
9. Drywall nailing inspection (some jurisdictions)
10. Final inspection — all work complete

COMMON PERMIT DELAYS:
- Incomplete drawings or specifications
- Missing engineer stamp on required documents
- Zoning violations discovered during review
- Environmental review requirements triggered
- HOA approval not obtained
- Prior unpermitted work discovered

SETBACK REQUIREMENTS (typical residential):
Front yard: 15-25 feet from property line
Side yard: 5-10 feet from property line
Rear yard: 20-25 feet from property line
Corner lots: Two front yards typically apply
Accessory structures: Often 3-5 feet from property lines
"""
},

{
"title": "Foundation Systems — Types, Selection, and Requirements",
"category": "structural",
"content": """
FOUNDATION SYSTEMS FOR RESIDENTIAL AND COMMERCIAL CONSTRUCTION

SHALLOW FOUNDATIONS:

Spread Footings (Isolated Column Footings)
  Used for individual columns. Size based on column load and allowable soil pressure.
  Typical allowable bearing pressure: 1,500-3,000 psf for undisturbed native soil.
  Minimum depth: 12 inches below finish grade, or below frost line.
  Frost depth by region: Northern US 42-60 inches, Midwest 36-48 inches,
  South 0-12 inches, Pacific Coast 12-18 inches.

Continuous Wall Footings
  Support load-bearing walls. Width typically 2x wall thickness minimum.
  For 8-inch masonry wall on 1,500 psf soil: 16-inch wide footing minimum.
  Reinforcement: minimum #4 bars at 12 inches on center each way.

Slab-on-Grade
  Monolithic: Footing and slab poured together. Used in warm climates.
  Thickened-edge: 24-inch deep perimeter with 4-inch interior slab.
  Rebar: #4 at 18 inches OC or 6x6 W1.4xW1.4 WWF minimum.
  Vapor barrier: 10-mil polyethylene under all slabs on grade.
  Subbase: 4 inches compacted gravel minimum.

Mat/Raft Foundation
  Entire building footprint becomes one large slab.
  Used when soil capacity is low or column loads are high.
  Typical for soft clays, filled sites, earthquake zones.

DEEP FOUNDATIONS:

Drilled Piers (Caissons)
  Drilled 12-36+ inches diameter, filled with concrete and rebar.
  Used for high loads, expansive soils, sites with poor near-surface soils.
  Bell-bottom piers: wider base for increased bearing.
  Skin friction: adds capacity in cohesive soils.

Driven Piles
  Steel H-piles: high loads, deep bearing.
  Concrete piles: 12-24 inch diameter, precast or cast-in-place.
  Friction piles: capacity from side friction, not tip bearing.
  Installation: use pile driving equipment, monitor blow counts.

Helical Piles
  Screwed into ground using hydraulic torque motor.
  Immediate loading allowed — no concrete cure time.
  Ideal for light commercial, additions, underpinning.
  Capacity: 10-150 tons depending on diameter and configuration.

SOIL INVESTIGATION:
Geotechnical report required for: commercial projects, hillside sites,
areas with known expansive or compressible soils, sites near water.
Standard Penetration Test (SPT): blow count indicates soil density.
N-value 0-4: very loose/soft, N 10-30: medium, N>50: dense/hard.
"""
},

{
"title": "Concrete Mix Design and Specifications",
"category": "materials",
"content": """
CONCRETE MIX DESIGN AND SPECIFICATIONS

COMPRESSIVE STRENGTH REQUIREMENTS (f'c):
Residential footings and slabs: 2,500-3,000 psi minimum
Commercial slabs on grade: 3,000-4,000 psi
Structural columns and beams: 4,000-5,000 psi
High-rise structures: 6,000-10,000 psi
Precast/prestressed: 5,000-8,000 psi
Bridge decks: 4,000-5,000 psi with air entrainment

WATER-CEMENT RATIO (W/C):
Lower W/C = stronger, more durable concrete.
W/C 0.40: high durability, 5,000+ psi (suitable for freeze-thaw exposure)
W/C 0.45: moderate durability, 4,000 psi
W/C 0.50: standard, 3,000-3,500 psi
W/C 0.60: minimum quality, 2,500 psi
Never exceed 0.65 for structural concrete.

MIX PROPORTIONS (by weight, Type I Portland cement):
Standard 3,000 psi: Cement 517 lb, Water 260 lb, Sand 1,270 lb, Aggregate 1,940 lb
High-strength 5,000 psi: Cement 752 lb, Water 300 lb, Sand 1,100 lb, Aggregate 1,800 lb

ADMIXTURES:
Water Reducer/Plasticizer: reduces water 5-10% maintaining workability.
High-Range Water Reducer (Superplasticizer): 12-30% water reduction.
Air Entrainer: improves freeze-thaw resistance. Target air 4-7% for exposure.
Accelerator (calcium chloride): speeds set in cold weather. Max 2% by weight cement.
Retarder: slows set in hot weather, long hauls.
Fly Ash (Class C or F): replaces 15-30% cement. Improves workability, long-term strength.
Silica Fume: 5-10% replacement. Dramatically improves strength and permeability.

SLUMP REQUIREMENTS:
Walls and columns: 3-4 inches
Slabs on grade: 2-3 inches
Footings: 1-3 inches
Pumped concrete: 4-5 inches
Self-consolidating concrete: spread 18-26 inches

CURING REQUIREMENTS:
Minimum 7 days moist curing for Type I cement.
Temperature must stay above 50°F during curing.
Methods: water curing (ponding, spraying), curing compounds, wet burlap.
High early strength (Type III): minimum 3 days curing.
Fly ash mixes: extend curing to 14 days.

COLD WEATHER CONCRETING (ACI 306):
Do not place on frozen ground.
Heat aggregates and water when ambient temperature below 40°F.
Protect placed concrete from freezing for minimum 3 days.
Minimum concrete temperature at placement: 55°F for members >12 inches.

HOT WEATHER CONCRETING (ACI 305):
Maximum concrete temperature at placement: 90°F (some specs 95°F).
Chill water or use ice as mixing water.
Schedule pours for early morning.
Use retarder admixtures.
"""
},

{
"title": "Steel Framing — Structural Steel Specifications",
"category": "materials",
"content": """
STRUCTURAL STEEL SPECIFICATIONS AND REQUIREMENTS

STEEL GRADES (ASTM):
A36: Fy = 36 ksi. General structural use. Most common for plates, angles.
A572 Grade 50: Fy = 50 ksi. Wide flange beams and columns. Most common today.
A992: Fy = 50 ksi min, Fu = 65 ksi. Required for wide flange shapes in seismic.
A500 Grade B: Fy = 46 ksi. Round and rectangular HSS (tubes).
A500 Grade C: Fy = 50 ksi. HSS (higher strength option).
A53 Grade B: Fy = 35 ksi. Pipe sections.
A325/A490: High-strength bolts for structural connections.

WIDE FLANGE (W-SHAPE) SELECTION:
Rule of thumb for floor beams: depth ≈ span/20 for steel.
W16x26 to W24x55: typical floor beams 20-40 ft spans.
W8x31 to W14x90: typical columns 1-5 stories.
W33 to W40: transfer girders, long spans.

DEFLECTION LIMITS (L = span length):
Live load: L/360 for floor beams (0.033 inches per foot of span)
Total load: L/240 for floors
Roof beams: L/180 for live load
Cantilevers: L/180 live, L/120 total

CONNECTION TYPES:
Simple shear connections: angles, single plates (shear tabs), end plates.
Moment connections: fully restrained, used for frames resisting lateral loads.
Bolted connections: A325 or A490 bolts, snug-tight or pretensioned.
Welded connections: fillet welds most common, groove welds for moment.

STANDARD BOLT DIAMETERS: 3/4", 7/8", 1", 1-1/8"
MINIMUM EDGE DISTANCE: 1.25 x bolt diameter from center to edge
MINIMUM BOLT SPACING: 2.67 x bolt diameter center to center

WELD SIZES:
Minimum fillet weld for 1/4" material: 1/8"
Minimum fillet weld for 1/2" material: 3/16"
Maximum fillet weld at plate edge: thickness minus 1/16"
E70XX electrodes: 70 ksi tensile strength (most common).

FIREPROOFING REQUIREMENTS:
Structural steel requires fireproofing in most occupancies.
Spray-applied fireproofing (SFRM): most common, 1/2" to 2" thick.
Intumescent paint: expands when heated, architecturally exposed steel.
Board protection: drywall enclosure, used for columns.
Thickness by rating: 1-hour typically 3/8", 2-hour typically 1", 3-hour 1.5"
"""
},

{
"title": "Electrical — NEC 2023 Residential Requirements",
"category": "electrical",
"content": """
NATIONAL ELECTRICAL CODE 2023 — RESIDENTIAL REQUIREMENTS

SERVICE ENTRANCE:
Minimum service size: 100 ampere for new single-family dwellings.
Recommended: 200 ampere for modern homes with EV charging and heat pumps.
Service conductor clearances:
  - From grade to service drop: 10 ft minimum (over driveways: 12 ft)
  - From roof: 8 ft minimum (3 ft if slope exceeds 4:12)
  - From windows: 3 ft minimum horizontally

BRANCH CIRCUITS:
Kitchen small appliances: Two 20-amp circuits minimum (outlets only, no lighting).
Laundry: One 20-amp circuit dedicated to laundry area.
Bathroom: 20-amp circuit shared among all bathrooms acceptable, or dedicated per bath.
Garage: 20-amp circuit for receptacles.
Outdoor receptacles: 20-amp circuit.
General lighting: 15-amp or 20-amp circuits throughout home.

RECEPTACLE SPACING:
No point on wall should be more than 6 feet from a receptacle.
Every wall space 2 feet or wider requires a receptacle.
Countertops: receptacle every 4 feet (measured along wall).
Kitchen countertop receptacles: within 24 inches of each counter section end.
Bathrooms: one receptacle within 36 inches of basin.
Outdoors: receptacle at each entrance 6.5 feet or less above grade.

GFCI PROTECTION REQUIRED:
Bathrooms, garages, outdoors, crawl spaces, unfinished basements,
kitchen countertops within 6 feet of sink, boathouses, swimming pools,
sump pump receptacles, rooftop receptacles, dishwashers.

AFCI PROTECTION REQUIRED (NEC 2023):
Virtually all 15 and 20 amp branch circuits in dwelling units:
Bedrooms, family rooms, living rooms, parlors, libraries, dens,
sunrooms, recreation rooms, closets, hallways, laundry areas, kitchens.
AFCI + GFCI combination devices available and increasingly common.

SMOKE DETECTORS (NFPA 72):
Required in every sleeping room.
Outside each sleeping area within 21 feet of door.
On every level including basement.
Interconnected: when one sounds, all sound.
Power: primary AC with battery backup.
Carbon monoxide detectors: required within 10 feet of sleeping areas.

PANEL REQUIREMENTS:
Working space: 30 inches wide x 36 inches deep x 6.5 feet high minimum.
Dedicated panel space: no storage permitted in working space.
Labeling: all circuits must be legibly identified.
"""
},

{
"title": "Plumbing — Residential Code Requirements",
"category": "plumbing",
"content": """
RESIDENTIAL PLUMBING CODE REQUIREMENTS (UPC/IPC)

MINIMUM FIXTURE REQUIREMENTS BY OCCUPANCY:
Single Family Dwelling:
  1 water closet, 1 lavatory, 1 bathtub or shower, 1 kitchen sink required.
  Laundry: receptacle for clothes washer if laundry area provided.

WATER SUPPLY PIPING:
Minimum pipe sizes:
  Water service from street: 3/4" minimum (1" recommended for 2+ baths)
  Cold water main in house: 3/4"
  Branch to fixtures: 1/2" minimum, 3/4" for water heater
  Individual fixtures: 1/2"

Pressure requirements:
  Minimum: 15 psi at fixtures
  Maximum: 80 psi (pressure reducing valve required if street pressure exceeds 80 psi)
  Water hammer arrestors required for quick-closing valves

DRAIN, WASTE, VENT (DWV) PIPE SIZING:
Water closet: 3" drain minimum
Bathtub/shower: 1.5" drain minimum
Lavatory: 1.25" drain minimum
Kitchen sink: 1.5" drain minimum
Washing machine: 2" standpipe, 2" drain
Building drain: 3" minimum, 4" if 2+ water closets

FIXTURE UNIT VALUES:
Water closet: 4 DFU (drainage fixture units)
Bathtub: 2 DFU
Shower: 2 DFU
Lavatory: 1 DFU
Kitchen sink: 2 DFU
Dishwasher: 2 DFU
Clothes washer: 3 DFU

VENTING REQUIREMENTS:
Every trap must be vented.
Individual vent pipe: same size as drain served, minimum 1.25"
Vent stack: 3" minimum for buildings with more than 2 water closets
Vent termination: 6 inches above roof, 12 inches above snow accumulation
Distance from window: 10 feet horizontal, or 3 feet above

WATER HEATER REQUIREMENTS:
Temperature and pressure relief valve required on all water heaters.
Relief valve discharge pipe: full size of valve outlet, terminate 6" above floor drain.
Seismic strapping: required in seismic zones C, D, E — two straps, upper 1/3 and lower 1/3.
Expansion tank: required on all closed systems (when backflow preventer installed).
Clearances: 18 inches from floor for gas units in garage, or raise on platform.

SLOPE REQUIREMENTS FOR DRAIN PIPES:
3" and smaller: 1/4" per foot minimum slope
4" and larger: 1/8" per foot minimum slope
"""
},

{
"title": "Construction Cost Estimation Guide",
"category": "cost_estimation",
"content": """
CONSTRUCTION COST ESTIMATION — 2025 REFERENCE GUIDE

RESIDENTIAL CONSTRUCTION COSTS (per square foot, US national average):

Single-Family Homes:
  Economy/Basic: $100-$150/sq ft
  Standard: $150-$250/sq ft
  Mid-range: $250-$350/sq ft
  Custom/High-end: $350-$500/sq ft
  Luxury: $500-$1,000+/sq ft

Multifamily (per unit):
  Garden apartments: $120-$180/sq ft
  Mid-rise (4-8 stories): $180-$280/sq ft
  High-rise (9+ stories): $280-$450/sq ft

COMMERCIAL CONSTRUCTION COSTS (per square foot):
Office (suburban): $150-$250/sq ft
Office (urban high-rise): $350-$600/sq ft
Retail shell: $100-$200/sq ft
Restaurant (full build-out): $350-$600/sq ft
Industrial warehouse: $50-$120/sq ft
Medical office: $300-$600/sq ft
Hospital: $600-$1,200/sq ft
School (K-12): $250-$450/sq ft
Hotel: $200-$450/sq ft

COST BREAKDOWN BY TRADE (typical residential):
Foundation: 8-12% of total
Framing/Structure: 15-20%
Roofing: 5-8%
Exterior finishes (siding, windows, doors): 10-15%
Plumbing: 8-12%
Electrical: 8-12%
HVAC: 8-12%
Insulation: 2-4%
Drywall: 5-7%
Interior finishes (flooring, paint, trim): 10-15%
Kitchen and baths: 10-20% (varies greatly)
Landscaping and site work: 5-10%

SOFT COSTS (add to hard construction costs):
Architecture and engineering: 8-15% of construction cost
Permits and fees: 1-3% of construction cost
Geotechnical investigation: $3,000-$15,000
Survey: $1,500-$5,000
Testing and inspections: $2,000-$10,000
Construction management: 5-10% of construction cost
Contingency: 10-15% for new construction, 15-20% for renovation

UNIT COSTS FOR COMMON ITEMS:
Concrete footing: $15-$30/linear foot
Concrete slab: $6-$12/sq ft (including forming and reinforcing)
Lumber framing: $4-$8/sq ft of framed floor area
Exterior sheathing: $1.50-$3.00/sq ft
Asphalt shingles: $4-$8/sq ft installed
Metal roofing: $10-$20/sq ft installed
Fiberglass insulation batts: $1.50-$3.50/sq ft
Spray foam insulation: $3-$7/sq ft
Drywall: $2-$4/sq ft installed
Hardwood flooring: $8-$15/sq ft installed
Tile flooring: $10-$20/sq ft installed
Paint interior: $2-$5/sq ft of wall area

LABOR RATES (hourly, US national average 2025):
Carpenter journeyman: $35-$65/hr
Electrician journeyman: $40-$80/hr
Plumber journeyman: $45-$85/hr
Mason: $40-$75/hr
Ironworker: $40-$80/hr
Laborer: $20-$35/hr
Project manager: $75-$150/hr
Superintendent: $60-$120/hr

COST ESCALATION FACTORS:
Urban premium (NYC, SF, Boston): 1.5-2.5x national average
California: 1.3-1.8x
High seismic zone: add 5-15% for structural upgrades
Historic renovation: add 20-40% over new construction
LEED certified: add 2-8% premium
"""
},

{
"title": "HVAC Systems — Selection and Sizing",
"category": "mechanical",
"content": """
HVAC SYSTEM SELECTION AND SIZING GUIDE

SYSTEM TYPES:

Forced Air (Split System)
  Most common for residential. Central air handler with ductwork.
  Gas furnace + AC: most common in cold/hot climates.
  Heat pump: efficient in moderate climates, COP 2.5-4.5.
  Sizing: Manual J load calculation required.
  Rule of thumb: 400-600 sq ft per ton of cooling (varies with climate).
  1 ton = 12,000 BTU/hr.

Hydronic (Hot Water) Systems
  Boiler heats water, distributed via pipes to radiators or radiant floor.
  Gas or oil boiler: 80-98% efficiency (AFUE).
  Radiant floor: highest comfort, slow response.
  Baseboard radiation: lower cost.
  Fan coil units: cooling also possible.

Mini-Split (Ductless)
  Outdoor compressor with one or more indoor air handlers.
  No ductwork required — ideal for additions, older homes.
  SEER rating 15-30+ (higher is more efficient).
  Multi-zone systems: 2-8 indoor units per outdoor unit.
  Typical cost: $3,000-$8,000 per zone installed.

Packaged Units
  All components in one cabinet on roof or ground.
  Common in commercial, Sunbelt residential.
  Rooftop units (RTU): 3-25 tons for commercial.

Variable Refrigerant Flow (VRF)
  Commercial/high-end residential.
  Heat recovery systems can cool one zone while heating another.
  Energy efficient in mixed-use buildings.

SIZING CALCULATIONS:
Manual J: ACCA standard for residential load calculations.
Factors: climate data, insulation levels, window area/orientation,
         infiltration, occupants, internal gains.

Approximate cooling loads:
  Well-insulated home: 15-20 BTU/hr per sq ft
  Average home: 20-30 BTU/hr per sq ft
  Poorly insulated: 30-40 BTU/hr per sq ft

EFFICIENCY RATINGS:
SEER2 (cooling): minimum 14.3 North, 15.2 South (2023+)
HSPF2 (heat pump heating): minimum 7.5
AFUE (furnace): minimum 80%, high efficiency 95-98%
EER2: instantaneous efficiency at peak conditions

DUCTWORK:
Sheet metal: most durable, use for trunk lines.
Flex duct: branches and connections, maximum 6 ft straight lengths.
Duct sizing: 0.08 inches W.C. friction rate per 100 ft (residential).
Supply air: 400-500 CFM per ton of cooling.
Return air: match supply, minimum one return per floor.
Duct leakage: maximum 4% total leakage to outside (Title 24, CA).

VENTILATION (ASHRAE 62.2):
Mechanical ventilation required when tightened beyond 3 ACH50.
Whole-house ventilation: 0.01 CFM/sq ft + 7.5 CFM per occupant.
Bath exhaust: 50 CFM intermittent or 20 CFM continuous.
Kitchen exhaust: 100 CFM intermittent or 25 CFM continuous.
ERV/HRV: recommended for tight construction, recovers 70-80% of energy.
"""
},

{
"title": "Accessibility — ADA and Fair Housing Requirements",
"category": "accessibility",
"content": """
ADA AND ACCESSIBILITY REQUIREMENTS FOR CONSTRUCTION

ADA STANDARDS FOR ACCESSIBLE DESIGN (2010):

WHEN ADA APPLIES:
Places of public accommodation (Title III): All new construction.
Commercial facilities: New construction and alterations.
Residential: Fair Housing Act applies to multifamily (4+ units).
Government buildings (Title II): All facilities.

ACCESSIBLE ROUTES:
Minimum width: 36 inches (44 inches preferred).
At doorways: 32 inches minimum clear width.
Changes in level: 1/4 inch vertical, 1/2 inch beveled max without ramp.
Slopes: Maximum 1:20 (5%) for accessible route without ramp provisions.
Cross slope: maximum 1:48 (2%).

RAMPS:
Maximum slope: 1:12 (8.33%).
Minimum width: 36 inches between handrails.
Maximum rise per run: 30 inches (then require landing).
Landings: 60 inches minimum length at top and bottom.
Handrails: required both sides when rise exceeds 6 inches.
Handrail height: 34-38 inches above ramp surface.

PARKING:
1-25 total spaces: 1 accessible space required.
26-50 spaces: 2 accessible spaces.
51-75: 3 spaces. 76-100: 4 spaces.
Van accessible spaces: 1 per 6 accessible spaces, 8-foot aisle.
Accessible space dimensions: 8 feet wide + 5-foot access aisle.
Van accessible: 8 feet wide + 8-foot access aisle.
Location: Shortest accessible route to entrance.

DOOR REQUIREMENTS:
Minimum clear width: 32 inches (32" clear when open 90 degrees).
Maneuvering clearance: 18 inches latch side for pull, 12 inches for push.
Door hardware: lever handles, not round knobs.
Opening force: maximum 5 lbs for interior doors.
Thresholds: 1/2 inch maximum, beveled.

RESTROOMS:
Turning radius: 60-inch diameter circle or T-turn space.
Water closet height: 17-19 inches.
Grab bars: 42 inches on side wall, 36 inches on rear wall.
Lavatory: knee clearance 27 inches high, 30 inches wide, 19 inches deep.
Mirror: bottom edge maximum 40 inches from floor.
Accessible stall: 60 inches wide x 56 inches deep minimum.

FAIR HOUSING ACT (multifamily 4+ units, ground floor always):
Accessible building entrance on accessible route.
Accessible common areas.
Doorways: 36-inch nominal (32 inches clear).
Accessible route throughout unit.
Reinforced walls for grab bars.
Accessible switches, outlets, thermostats (15-48 inches AFF).
Kitchen/bath usable by wheelchair user.
"""
}
]


def build_knowledge_base():
    """
    Build FAISS vector store from construction documents.
    Uses HuggingFace sentence-transformers — no API key needed.
    """
    print("Building construction knowledge base...")
    print(f"Documents: {len(CONSTRUCTION_DOCUMENTS)}")

    # Create LangChain documents
    docs = []
    for doc_data in CONSTRUCTION_DOCUMENTS:
        doc = Document(
            page_content=doc_data["content"],
            metadata={
                "title":    doc_data["title"],
                "category": doc_data["category"],
                "source":   f"Construction Reference — {doc_data['title']}"
            }
        )
        docs.append(doc)

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks created: {len(chunks)}")

    # Load embedding model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Build FAISS index
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Save index
    index_path = "knowledge_base/index"
    vectorstore.save_local(index_path)
    print(f"FAISS index saved to: {index_path}")

    # Save document metadata
    metadata = [
        {
            "title":    d["title"],
            "category": d["category"],
            "chunks":   len([c for c in chunks
                             if c.metadata["title"] == d["title"]])
        }
        for d in CONSTRUCTION_DOCUMENTS
    ]
    with open("knowledge_base/metadata.json", "w") as f:
        import json
        json.dump(metadata, f, indent=2)

    print(f"\nKnowledge base built successfully!")
    print(f"Total chunks indexed: {len(chunks)}")
    print(f"Index location: {index_path}")
    return vectorstore


if __name__ == "__main__":
    build_knowledge_base()