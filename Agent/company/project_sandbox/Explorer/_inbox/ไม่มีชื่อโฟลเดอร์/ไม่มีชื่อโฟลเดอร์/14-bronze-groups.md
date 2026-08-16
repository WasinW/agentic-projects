# 14 — BRONZE: Groups (80 rows)

> **Raw layer, group grain. No filtering, no judgement.** Everything that was ever considered is here, including groups previously called "red," "dead," or "unbuyable."
> Filtering happens in file 16 (SILVER), never here.
>
> **Columns:** `model` = how it makes money · `product` = what it actually sells · `customer` = who pays · `depends_on` = upstream dependency (this field builds the chokepoint map) · `owns` = the scarce thing it controls · `buy` = buyability profile · `data` = internet / inside (blue-red test) · `scarcity` = ↑ increasing / → flat / ↓ eroding

---

## PART A — DIRECT AI INFRASTRUCTURE

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Compute silicon | Design IP + fab-out, sell per unit at high margin | GPUs, accelerators, custom ASIC | Hyperscalers, neoclouds, OEM | A3 foundry, A2 memory, A6 EDA | CUDA-class software lock-in, design talent | ✅ mostly | internet | ↑ then → |
| A2 | Memory & HBM | Capital-intensive commodity with cyclical pricing power | DRAM, HBM stacks, NAND | A1, A10 | A4 equipment, C6 wafers | HBM process capability (3 firms) | ✅ 🟡 KR/JP | inside (process) | ↑ |
| A3 | Foundry & packaging | Sell capacity; charge for process leadership | Wafers, CoWoS packaging | A1, A21 | A4 equipment, A20, C7 chemicals | Leading-edge node + packaging capacity | ✅ 🟡 TW | inside | ↑ |
| A4 | Semicap equipment | Sell tools + lifetime service annuity | Litho, etch, depo, test tools | A3, A2 | A20 subsystems, C7 | Process know-how, installed base | ✅ 🟡 EU/JP | inside | ↑ |
| A5 | Metrology & inspection | Sell tools + consumables | Inspection, metrology, probe cards | A3, A2 | A20 optics | Measurement precision | ✅ 🟡 | inside | ↑ |
| A6 | EDA & chip IP | License + royalty per chip shipped | Design software, IP blocks | A1, A3 | — | Designer lock-in, verified IP libraries | ✅ | internet | → consolidating |
| A7 | Networking & interconnect | Sell hardware; increasingly software-attached | Switches, NICs, connectors | A14, hyperscalers | A1 silicon, A8 optics | Protocol position, install base | ✅ | internet | → |
| A8 | Optical & photonics | Component sale, volume-driven | Transceivers, lasers, optical engines | A7, A14 | C7 materials, A20 | Packaging yield at 800G/1.6T | ✅ 🟡 | inside | ↑ |
| A9 | Storage | Hardware + capacity licensing | Arrays, flash systems | A14, enterprises | A2 memory | Performance at AI-scale IO | ✅ 🔒 VAST/Weka | internet | → |
| A10 | Servers & ODM | Thin-margin assembly at scale | Racks, systems, integration | Hyperscalers, neoclouds | A1, A2, A11, A12 | Assembly capacity, speed | ✅ 🟡 TW 🇹🇭 | internet | → |
| A11 | Cooling & thermal | Equipment sale + service contract | CDU, liquid cooling, enclosures | A14, A13 | B13 fluids, C1 copper | Thermal engineering, install base | ✅ 🔒 🏛️ Rittal | inside | ↑ |
| A12 | DC power equipment | Equipment + long service annuity | UPS, switchgear, PDU, busway | A14, A13 | C1 copper, C3 GOES, A21 | Lead-time-constrained capacity | ✅ | inside | ↑↑ |
| A13 | DC construction | Project contracting, labour markup | Build, fit-out, commissioning | A14, hyperscalers | D8 labour, A12, B10 | Local labour + permitting relationships | ✅ 🏛️ Bechtel | inside | ↑ |
| A14 | DC operators & neoclouds | Lease space/power, or resell compute | Colocation, GPU-hours | AI labs, enterprises | B1-B2 power, A13 | **Powered land + interconnection queue position** | ✅ 🔒 | inside | ↑↑ |
| A15 | Model labs & AI software | Subscription, API metering, seat licences | Models, platforms, apps | Everyone | A1, A14 | Model capability, distribution | ✅ 🔒 OpenAI/Anthropic | internet | ↑ then ↓ |
| A16 | Data labeling & eval | Service margin, increasingly product | Labeled data, eval harnesses | A15 | Human labour | Expert annotator networks | 🔒 mostly | inside | ↑ |
| A17 | Edge AI silicon | Design + per-unit sale, long design cycles | Vision SoC, inference chips | A18, A19, OEM | A3 foundry | Power-per-inference, design wins | ✅ 🔒 | **inside (sensors)** | ↑ |
| A18 | Automotive & ADAS | Long-cycle design win, per-vehicle content | ADAS stacks, sensors, compute | OEMs | A17, A21 | Homologation, safety certification | ✅ 🏛️ Bosch/ZF | inside | ↑ |
| A19 | Industrial sensing & IoT | Equipment + razor-blade consumables | Sensors, vision, controllers | Factories, utilities | A17 | Application know-how, install base | ✅ 🏛️ SICK/IFM | **inside** | ↑ |
| A20 | Deep upstream subsystems | Sole-source component supply at extreme margin | Optics, lasers, vacuum, RF power | A4, A5 | C9 exotic materials | **Physics-level monopolies** | 🏛️ **highest ratio** | inside | ↑↑ |
| A21 | Power semiconductors | Design + fab, per-unit | SiC/GaN devices, modules | A12, A18, B7 | A3, C6 substrates | SiC substrate capability | ✅ | inside | ↑ |
| A22 | Distribution channel | Working-capital business, thin margin, volume | Component stocking + logistics | Everyone downstream | Everything upstream | Inventory position, relationships | ✅ 🏛️ Sonepar/Digi-Key | internet | → |
| A23 | Modular & prefab DC | Sell speed-to-power as a product | Prefab modules, skids | A14 | A11, A12 | Manufacturing slots | 🔒 🏛️ mostly | inside | ↑ |

## PART B — ENERGY

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Merchant IPP | Sell power under long-term PPA | Electricity, capacity | A14, hyperscalers | B5, B3 generation | **Existing generation + interconnection** | ✅ | inside | ↑↑ |
| B2 | Regulated utilities | Rate-base return on invested capital | Electricity delivery | Everyone in territory | B10 grid, regulators | Monopoly franchise territory | ✅ | inside | → |
| B3 | Nuclear & SMR | Sell baseload; SMR sells future capacity | Power, reactors | B1, B2, hyperscalers | B4 fuel, regulators | Licences, operating fleet | ✅ 🔒 X-energy/Kairos | inside | ↑ |
| B4 | Nuclear fuel & enrichment | Mine/enrich, sell under long contracts | U3O8, HALEU, fuel assemblies | B3 | Mining licences | **Licensed enrichment capacity** | ✅ 🏛️ Orano/Urenco | inside | ↑↑ |
| B5 | Gas turbines | Equipment + decades of service annuity | Turbines, service | B1, B2, A14 | C3 GOES, specialty alloys | **Multi-year order backlog** | ✅ | inside | ↑↑ |
| B6 | Renewables & developers | Develop, sell or operate under PPA | Solar/wind farms, panels | B1, B2, corporates | C5 materials, land | Development pipeline, land options | ✅ | internet | → |
| B7 | Battery storage | Sell systems + software optimisation | BESS, dispatch software | B1, B2, A14 | C5 lithium, A21 | **Makes intermittent power usable for AI** | ✅ 🔒 🟡 CN | inside | ↑↑ |
| B8 | Fuel cells | Sell units + long-term service | Fuel cell systems | A14 | C7 materials | Fast deployment vs grid queue | ✅ | inside | ↑ |
| B9 | Geothermal | Develop and sell power | Baseload clean power | B1, A14 | Drilling tech | Resource rights, drilling IP | 🔒 mostly | inside | ↑ |
| B10 | Transmission & transformers | Equipment with multi-year lead times | Transformers, switchgear, cable | B2, A13 | **C1 copper, C3 GOES** | **Manufacturing slots** | ✅ 🟡 | inside | ↑↑ |
| B11 | Smart grid & energy software | SaaS/licence + metering hardware | Meters, DERMS, trading software | B2, B1 | — | Utility integration depth | ✅ 🔒 | internet | ↑ |
| B12 | Water & cooling supply | Equipment, utility, or service | Pumps, treatment, water rights | A11, A14, municipalities | — | **Water rights near DC sites** | ✅ | inside | ↑ |
| B13 | Cooling fluids & TIM | Specialty chemical margin | Dielectric fluids, thermal interface | A11, A10 | C7 chemicals | Formulation IP, qualification | ✅ 🔒 | inside | ↑ |
| B14 | Fire, safety & physical security | Equipment + monitoring subscription | Suppression, access control, VMS | A14, A13 | — | Certification, code compliance | ✅ | inside | → |

## PART C — MATERIALS & UPSTREAM

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| C1 | Copper | Extract and sell commodity; price-taker with scale | Cathode, concentrate | B10, A12, A11 | Mining licences | **Orebodies — 82-83% of AI mineral demand** | ✅ | inside | ↑↑ |
| C2 | Rare earths & magnets | Mine + **process** (processing is the moat) | NdFeB magnets, separated oxides | A11, A18, B6 | Separation capacity | Non-China processing capability | ✅ 🔒 | inside | ↑↑ |
| C3 | GOES electrical steel | Specialty steel with qualification barriers | Grain-oriented electrical steel | B10, B5 | Steel capacity | **Transformer-core capability** | ✅ 🟡 | inside | ↑↑ |
| C4 | Aluminium, precious, gallium | Commodity + byproduct economics | Metals, contacts, compounds | A10, A12, A21 | Smelting, energy | Smelter capacity, byproduct streams | ✅ ⛔ Ga/Ge | inside | ↑ |
| C5 | Battery minerals | Mine + refine, cyclical | Li, Co, Ni, graphite | B7, A18 | Refining capacity | Refining, not mining | ✅ 🟡 CN | inside | ↑ |
| C6 | Wafers & substrates | Capital-intensive, qualification-locked | Silicon wafers, ABF substrates | A3, A2 | C7, energy | Qualification with foundries | ✅ 🟡 JP/TW | inside | ↑ |
| C7 | Specialty gases & chemicals | Razor-blade: qualify once, supply forever | Photoresist, gases, precursors | A3, A4 | — | **Qualification lock-in** | ✅ 🏛️ Heraeus | inside | ↑ |
| C8 | Recycling & urban mining | Buy waste, sell recovered material | Recovered metals, RE oxides | C1, C2, C4 | Collection networks | Feedstock access | ✅ 🔒 | inside | ↑ |
| C9 | EUV exotic materials | Tiny volumes, extreme purity, extreme margin | Tin, Ru, Mo, ultra-pure quartz | A20, A4 | Purification capability | **Purity capability nobody else has** | 🏛️ **Sibelco/Quartz Corp = no proxy** | inside | ↑↑ |

## PART D — PHYSICAL / ATOMS ADJACENT

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| D1 | Robotics & automation | Equipment + service; moving to RaaS | Arms, AMR, humanoids | Factories, warehouses | A17, D-motion | Motion control IP, install base | ✅ 🔒 Figure/1X | **inside** | ↑↑ |
| D2 | Industrial software & twin | Seat licence + increasingly usage | CAD, PLM, simulation, twin | Manufacturers | — | Format lock-in, model libraries | ✅ | inside | ↑ |
| D3 | Logistics automation | Systems integration + software | Warehouse automation | Retail, 3PL | D1, A19 | Integration expertise | ✅ 🏛️ Knapp | inside | ↑ |
| D4 | Construction tech & materials | Aggregate/materials margin + software | Aggregates, cement, ConTech | A13, infrastructure | Quarry permits | **Quarry proximity permits** | ✅ 🏛️ Bechtel | inside | → |
| D5 | Defense & resilience | Government contracts, long cycles | Weapons, autonomy, C2 software | States | A1, A17, supply chain | Security clearance, programs | ✅ 🔒 Anduril | inside | ↑↑ |
| D6 | Space & satellite | Launch service, capacity lease, data | Launch, bandwidth, imagery | Gov, telecom, enterprises | Launch capability | **Orbital slots, spectrum** | ✅ 🔒 SpaceX | inside | ↑ |
| D7 | Quantum & photonic compute | Pre-revenue R&D; future compute sale | Quantum systems, photonic chips | Research, gov, finance | C9 materials, A20 | Physics IP | ✅ 🔒 | inside | ↑ speculative |
| D8 | Skilled trades & staffing | Markup on placed labour hours | Electricians, pipefitters, engineers | A13, A12, B10 | Training pipelines | **Trained trade labour pool** | ✅ | inside | ↑↑ |

## PART E — AI ADOPTERS

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Financial services | Spread, fee, float | Credit, payments, asset management | Consumers, corporates | A15 for AI leverage | **Licences, deposits, customer relationships** | ✅ 🟡 JP 🇹🇭 | inside | → |
| E2 | Healthcare & pharma | Patent-protected margin, reimbursement | Drugs, devices, diagnostics | Payers, patients | A15, A16 | **Patents, trial data, approvals** | ✅ | inside | ↑ |
| E3 | Insurance | Underwriting margin + float | Policies | Everyone | E11 risk data | **Actuarial data, licences** | ✅ 🔒 | inside | ↑ |
| E4 | Legal & professional services | Billable hours → shifting to outcomes | Advice, implementation | Enterprises | A15 | Client relationships, precedent libraries | ✅ 🔒 Harvey | inside | ↓ *(AI compresses hours)* |
| E5 | Retail & e-commerce | Margin on goods + ads + logistics | Goods, marketplace, ads | Consumers | Logistics, D3 | **Customer base, logistics network** | ✅ 🇹🇭 | internet | → |
| E6 | Agriculture & food | Input sale + equipment + service | Seed, chemicals, machinery | Farmers | A19 sensing | **Germplasm, dealer networks** | ✅ 🇹🇭 | **inside (field data)** | ↑ |
| E7 | Energy & mining operations | Extract and sell; AI reduces unit cost | Oil, gas, ore | Industry | A19, D1 | **Reserves, concessions** | ✅ | inside | → |
| E8 | Telecom | Subscription + infrastructure lease | Connectivity, towers | Everyone | B2 power, A7 | **Spectrum, tower sites** | ✅ 🇹🇭 | inside | → |
| E9 | Education | Tuition, subscription, licensing | Courses, credentials | Learners, institutions | A15 | **Accreditation** | ✅ | internet | ↓ *(AI substitutes)* |
| E10 | Media & advertising | Attention arbitrage, ad auction | Content, ad inventory | Advertisers, consumers | A15 | **Audience relationship** | ✅ | internet | ↑ *(human premium)* |
| E11 | Risk & climate analytics | Data licence + model subscription | Risk models, scores | E3, E1, A14 | Historical data | **Proprietary loss datasets** | ✅ 🏛️ private | inside | ↑ |

## PART F — SECOND-ORDER ENABLERS

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| F1 | Cybersecurity | Subscription per seat/endpoint/workload | Detection, prevention platforms | Enterprises | Threat data | Threat intelligence corpus | ✅ 🔒 agentic | inside | ↑↑ |
| F2 | Identity & provenance | Per-verification or per-seat | IdP, KYC, provenance | Enterprises, platforms | — | **Verified-identity graph** | ✅ 🔒 🏛️ | inside | ↑↑ |
| F3 | Data platforms & governance | Consumption-based | Warehouse, lakehouse, catalog | Enterprises | A14 compute | Data gravity, format position | ✅ 🔒 Databricks | internet | ↑ |
| F4 | Payments & agentic commerce | Basis points per transaction | Rails, processing | Merchants, platforms | Bank rails, regulators | **Network effect, licences** | ✅ 🔒 Stripe | inside | ↑ |
| F5 | Real estate near power | Lease land/buildings; capture scarcity rent | Powered land, industrial space | A14, A13 | B2 interconnection | **Land + approved interconnection** | ✅ 🇹🇭 | inside | ↑↑ |
| F6 | Infrastructure capital | Management fee + carry | Funds, financing | Institutions | — | LP relationships, deal access | ✅ | inside | ↑ |
| F7 | AI-risk insurance | Premium minus losses | AI liability cover | Enterprises deploying AI | **Loss data that doesn't exist yet** | Actuarial basis | ✅ 🔒 | inside | ↑↑ **whitespace** |
| F8 | Testing & assurance | Fee per audit + recurring certification | Certification, audit | Manufacturers, AI deployers | Standards bodies | **Accreditation + brand trust** | ✅ 🏛️ TÜV/DNV | inside | ↑↑ |
| F9 | Waste heat, carbon, environmental | Service contract + commodity | Waste services, carbon credits | Industry, A14 | Permits | **Disposal permits, sites** | ✅ 🔒 | inside | ↑ |

## PART G — THAILAND / SEA 🇹🇭

| id | group | model | product | customer | depends_on | owns | buy | data | scarcity |
|---|---|---|---|---|---|---|---|---|---|
| G1 | Thai power producers | PPA with EGAT + private customers | Electricity | EGAT, industrial estates, DC | Fuel, licences | **Thai generation licences** | ✅ 🇹🇭 | inside | ↑↑ |
| G2 | Thai industrial estates | Sell/lease land + utilities annuity | Serviced land, power, water | Manufacturers, DC operators | G1 power, BOI | **Zoned land with utilities** | ✅ 🇹🇭 | inside | ↑↑ |
| G3 | Thai electronics supply | Contract manufacturing margin | Power supplies, PCB, packaging | A10, A12, global OEM | A3, C6 | **Thai manufacturing base + labour cost** | ✅ 🇹🇭 | inside | ↑ |
| G4 | Thai contractors | Project contracting | Construction, EPC | G2, G1, government | D8 labour | Local permitting relationships | ✅ 🇹🇭 | inside | ↑ |
| G5 | Thai telecom & digital | Subscription + infrastructure | Connectivity, IT services | Consumers, enterprises | G1, spectrum | **Spectrum, fibre routes** | ✅ 🇹🇭 | inside | → |
| G6 | Regional SEA & China DC | Colocation, cloud, platform | DC capacity, digital services | Global hyperscalers | Local power, land | Regional land + power positions | ✅ 🟡 ⛔ CN | inside | ↑↑ |

---

## Chokepoint signal, derivable from `depends_on`

Groups appearing most often as a dependency of others, cross-referenced with buyability:

| Group | Depended on by | Buyability | Read |
|---|---|---|---|
| **C1 copper** | B10, A12, A11, A10 | ✅ | Buy the chokepoint |
| **C3 GOES** | B10, B5 | ✅ 🟡 | Buy the chokepoint |
| **A20 deep upstream** | A4, A5 | 🏛️ **mostly unbuyable** | **Build-space, or hold ASML as the aggregation point** |
| **C9 EUV materials** | A20, A4 | 🏛️ **no proxy for quartz** | **Pure build-space** |
| **C7 qualification lock-in** | A3, A4 | ✅ 🏛️ | Buy where possible |
| **B10 transformers** | B2, A13, A12 | ✅ | Buy the chokepoint |
| **D8 skilled trades** | A13, A12, B10 | ✅ | Under-discussed |
| **F5 powered land** | A14, A13 | ✅ 🇹🇭 | **Reachable in Thailand** |
| **F7 AI loss data** | E3 | **doesn't exist** | **Whitespace — buildable** |

> **The three rows in bold-build are where the same dataset stops answering "what to invest in" and starts answering "what to build."**
