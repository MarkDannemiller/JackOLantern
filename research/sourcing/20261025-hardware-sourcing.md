# Joyful Jack: hardware sourcing for the remaining physical parts

Researched 2026-10-24 for fasteners, bearings, belt drive, servo mounting, springs, wiring, print material, extrusion, base and enclosure. The data is in `20261025-hardware-sourcing.json`: 196 entries, one per listing or reference, with vendor, part number, pack, price, URL, CAD and dimensions. This file only summarises it. Nothing was ordered.

**Counts:** 97 prices come from live listings, 27 from search snippets only ("snippet, unconfirmed"), and 72 are TBD. Of the TBD entries, 14 are reference data such as belt ratings, set-screw tables and computed belt centres, which have no price by nature. The other 58 are purchasable parts whose price could not be read. McMaster-Carr and Misumi (JavaScript pages or HTTP 403), SDP-SI (Cloudflare), Home Depot, Grainger, Powerwerx and most Amazon pages blocked the fetcher. Each of these is marked TBD with what would resolve it: usually opening the page in a browser or a Misumi configurator quote. This was a degraded fallback: web fetch was used without vendor APIs.

## Key dimensions for CAD

| What | Value | Source |
|---|---|---|
| STS3215 body | 45.2 x 24.7 x 35 mm; 25T spline, OD 5.9 mm; M3x6 horn screw; no mounting ears (8 x PA2.0 self-tapping case screws, rear idler 6 mm boss with PA3.0x5) | Feetech/Seeed ST-3215-C047 sheet |
| STS3215 horn | 19.2 mm disc (20 mm in SO-ARM100 STEP), 4 holes on a 14 mm bolt circle (2.5 mm holes in the STEP, the M3 tap-drill size) | Waveshare drawing, SO-ARM100 STEP |
| STS3250 | same envelope and spline; aluminium case, 4 x M2 tapped holes per face; horn bolt circle TBD (Feetech drawing) | Feetech |
| 25T aluminium horn (DS3235/DS3225MG/MG996R) | 20 mm disc, 4 x M3 tapped on a 14 mm bolt circle; DS3235 mounting holes 49.5 x 10 mm | listing / DS3235 drawing |
| Bearings ID x OD x W | 6802 15x24x5, 6803 17x26x5, 6804 20x32x7, 6704 20x27x4, 608 8x22x7, F688 8x16x5 (flange 18 x 1.1), F695 5x13x4 (flange 15 x 1.0); thrust 51105 25x42x11, 51106 30x47x11 | VXB and others |
| GT2 pitch diameters | 22T 14.006 mm, 60T 38.197 mm (computed; SDP-SI snippets give 14 and 38.2). Phidgets OD 13.51 / 37.69 mm | computed / Phidgets drawing |
| 22:60 centre distance | 220 mm belt: 67.92 mm (computed, rechecked); 200 mm: 57.73; 240 mm: 78.06; 280 mm: 98.25 | computed |
| Heat-set inserts (CNC Kitchen) | M3: OD 4.6, L 5.7, hole 4.0 mm, min wall 1.6 mm. M4: OD 6.3, L 8.1, hole 5.6 mm, min wall 2.1 mm | CNC Kitchen |
| 2020 extrusion | Misumi HFS5-2020: "slot width 6", 0.5 kg/m, cut 50-4000 mm; centre hole 4.2 mm (Misumi drawing, snippet). No vendor stated 6.2 mm. Adafruit 1221 centre hole about 4.45 mm | Misumi |
| 1 in floor flange | Anvil FIG 1190: 4 in OD, 4 x 1/4 in holes on a 3 in bolt circle; pipe OD 1.315 in (33.4 mm) | Anvil |
| Molex 5264 (Feetech "5264 3P") | 2.50 mm pitch; housing 50-37-5033, terminal 08-70-1040 (22-28 AWG) | Digi-Key |
| XT60 | 15.5 x 8.1 x 20.5 mm (Pololu #2175) | Pololu |
| Enclosure Hammond 1554N2GY | 120 x 120 x 61 mm outside, 112.91 x 106.91 x 54.50 mm inside (text from the PDF drawing; check it) | Hammond via Mouser |
| Cable glands | PG7: 3-6.5 mm cable, 12.5 mm hole. PG9: 4-8 mm cable, 15.2 mm hole | Alpha Wire via Mouser |

## CAD and licences

- **STS3215:** `https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/STEP/SO100/STS3215_03a.step`, from the TheRobotStudio SO-ARM100 repo. The repo's LICENSE file is **Apache License 2.0**. Waveshare also offers a STEP (ST3215-3D.zip) with no licence stated.
- **STS3250:** no CAD found. Model it from the STS3215 envelope until Feetech publishes one.
- **AmazingHand (Pollen Robotics):** STEP and STL are in `cad/step` and `cad/stl` of the pollen-robotics/AmazingHand repo, with a public Onshape document. Mechanical design is **CC BY 4.0**; software is **Apache-2.0**. The hand uses 8 Feetech SCS0009 servos.
- **goBILDA 8 mm REX shaft:** STEP available, terms not checked.

## Findings that affect the design

1. **The 6 mm GT2 belt is under-rated for the shoulder.** Gates gives 2M GT2 a recommended working tension of 111 N per 25.4 mm of width (Gates 17611-T, glass-fibre cord). That is about 26 N at 6 mm (computed), or about 0.50 N.m at the 60T output (computed). D7 has tier B needing about 59.7 kg.cm (about 5.9 N.m) at the shoulder, and the spring takes only about 3.2 N.m of it. The ultimate strength at 6 mm is about 1 kN (computed), so the belt will not snap, but it runs far past Gates' design tension and will stretch and skip teeth. Options:
   - 3M GT2 at 9 mm: about 180 N working (computed), with a larger 22T of PD 21.01 mm.
   - HTD-3M at 9 mm: about 101 N working.
   - A stronger spring, so the belt carries less of the load.

   Gates publishes no steel-cord data.
2. **Set-screw hubs:** Unbrako gives M3 0.87 N.m seating torque and 0.71 kN axial holding, M4 2.20 N.m and 1.70 kN. The Phidgets pulleys clamp with 2 x M4 into aluminium, and the TRM4000_0 shaft is round, so grind a flat or use a D-cut shaft. No metric 8 or 10 mm D-cut shaft was confirmed with a price: Misumi SFJ with a D-cut alteration needs a configurator quote.
3. **Phidgets TRM4500_0 is a 48 x 27 mm KFL08 two-bolt flange unit**, not a small flanged bearing. A pressed-in 608 or F688 is much smaller for a printed joint. The Phidgets 60T pulley has no flanges.
4. **Feetech servos ship without horns**, so buy or print them. Feetech cables come only in 300 mm and 900 mm 6-packs (Waveshare) or 15 cm; other lengths mean crimping Molex 5264.
5. **Shoulder springs:** Century Spring 90CS ($9.37, 0.625 in OD, 6.4 lb/in, 27 lbf max, which gives 4.8-6.0 N.m on a 40-50 mm lever, computed) or McMaster 9654K332 ($16.16 per 6, 19.5 lbf max, which gives 4.3 N.m at 50 mm, computed). The BOM's Grainger 1NAE3 could not be checked. A single stock torsion spring gives only about 2.1 N.m.
6. **Supplier changes:**
   - OpenBuilds shut down (announced May 2025).
   - Maker Store USA can't cut or tap at the moment, so it sells full lengths only. Use Misumi for tapped ends.
   - Maker Store drop-in tee nuts are M5 only, and Adafruit's M4 slim T-nut is out of stock.
7. **Base:** neither Home Depot nor Lowe's sells a 1/4 in birch 2x2 ft panel or a 24 in plywood round. The nearest round is a Woodpeckers 24 in x 1/2 in birch circle, about $41.61 (snippet).
8. **E-stop stations cost $79-108 complete.** A bare yellow box (Schneider XALK01H7) is $26.02, plus the existing button.
9. **Mouser obsoletes:** the Littelfuse 0257010/0257030 fuses and Panduit PV14-10R-L are obsolete; the entries use 0287010.PXCN, 0287030.PXCN and PV14-10R-C instead. Bussmann ATC-10 and ATC-30 prices may be per pack of 5.

## Entries by category

### fasteners (28)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Heat-set insert M3 standard (CNC Kitchen) | 3DJake (CNC Kitchen reseller, US site) | CNC Kitchen M3 Standard M3x5.7 | 100 | $11.18 | listing |
| Heat-set insert M3 standard (Prusa, CNC Kitchen design) | Prusa Research | Heat Set Inserts - M3 standard 100 pcs | 100 | $10.99 | listing |
| Heat-set insert M4 standard (CNC Kitchen) | 3DJake (CNC Kitchen reseller, US site) | CNC Kitchen M4 Standard M4x8.1 | 50 | $11.18 | listing |
| Heat-set insert M3 (ruthex RX-M3x5.7) | Amazon (ruthex) | RX-M3x5.7 / ASIN B08BCRZZS3 | 100 |  | TBD |
| Heat-set insert M4 (ruthex RX-M4x8.1) | Amazon (ruthex) | RX-M4x8.1 / ASIN B07YSV66Y5 | 50 |  | TBD |
| Heat-set insert assortment M2-M5 + tips (ruthex bundle) | Amazon (ruthex) | ASIN B0FCXXW62N | 270 |  | TBD |
| Tapered heat-set insert M3 (McMaster 94180A331) | McMaster-Carr | 94180A331 | TBD: McMaster page |  | TBD |
| Heat-set insert M3 5.7 mm (McMaster 94459A140) | McMaster-Carr | 94459A140 | 50 |  | TBD |
| Tapered heat-set insert M4 (McMaster 94180A351) | McMaster-Carr | 94180A351 | TBD: McMaster page |  | TBD |
| SHCS assortment M2-M5 stainless (NINDEJIN) | Amazon (NINDEJIN) | ASIN B09B1QFS7K | TBD: ~880 pcs per related listing; confirm |  | TBD |
| SHCS assortment M2.5-M8 stainless (HVAZI 135 pc) | Amazon (HVAZI) | ASIN B01N6ARAV5 | 135 |  | TBD |
| SHCS M3x8 18-8 SS (McMaster 91292A112) | McMaster-Carr | 91292A112 | 100 | $5.45 | snippet, unconfirmed |
| SHCS M3x10 18-8 SS (McMaster 91292A113) | McMaster-Carr | 91292A113 | TBD: McMaster page |  | TBD |
| SHCS M3x12 18-8 SS (McMaster 91292A114) | McMaster-Carr | 91292A114 | TBD: McMaster page |  | TBD |
| SHCS M3x16 18-8 SS (McMaster 91292A115) | McMaster-Carr | 91292A115 | TBD: McMaster page |  | TBD |
| SHCS M3x20 18-8 SS (McMaster 91292A123) | McMaster-Carr | 91292A123 | TBD: McMaster page |  | TBD |
| SHCS M4x16 18-8 SS (McMaster 91292A118) | McMaster-Carr | 91292A118 | TBD: McMaster page |  | TBD |
| SHCS M4x20 18-8 SS (McMaster 91292A121) | McMaster-Carr | 91292A121 | TBD: McMaster page |  | TBD |
| M5 low-profile screws (Maker Store) | Maker Store USA | SCREWS-M5-LP | 25 (6-25 mm lengths); 10 (27-65 mm) |  | TBD |
| M5 cap head bolts 10 pc (Maker Store) | Maker Store USA | M5 Cap Head Bolts - 10pc | 10 |  | TBD |
| M3 nylon-insert lock nut (McMaster 93625A100) | McMaster-Carr | 93625A100 | TBD: McMaster page |  | TBD |
| M4 nylon-insert lock nut (McMaster 93625A150) | McMaster-Carr | 93625A150 | TBD: McMaster page |  | TBD |
| Nylon-insert lock nut assortment M3-M12 304 SS (Vifmy) | Amazon (Vifmy) | ASIN B0F7JTY4QM | 140 |  | TBD |
| M3 flat washer (McMaster 98689A112) | McMaster-Carr | 98689A112 | TBD: McMaster page |  | TBD |
| M4 flat washer (McMaster 93475A230) | McMaster-Carr | 93475A230 | TBD: McMaster page |  | TBD |
| Flat washer assortment M1.6-M12 304 SS (MCMASKE) | Amazon (MCMASKE) | ASIN B0BG28SWLK | TBD: listing |  | TBD |
| Set screw holding power, metric (Unbrako) | Unbrako (reference) | Socket Set Screws - Metric spec sheet |  |  | TBD |
| Clamp-collar axial holding (Stafford), for comparison | Stafford Manufacturing (reference) | Axial Holding Power table |  |  | TBD |

### extrusion (14)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Drop-in tee nut M5, 10-pack (Maker Store) | Maker Store USA | HARD-TNUT-DROP10 | 10 | $11.93 | listing |
| M5 drop-in T-nut 2020, 100 pcs (Amazon) | Amazon | ASIN B0CG4VNT51 | 100 |  | TBD |
| Post-assembly spring nut M5 (Misumi HNTP5-5) | Misumi | HNTP5-5 (PACK-HNTP5 = 100) | 1 (or 100 as PACK-HNTP5) |  | TBD |
| Slim T-nut M4 for 20x20, 50 pcs (Adafruit 1157) | Adafruit | 1157 | 50 | $11.95 | listing |
| 2020 extrusion cut length (Misumi HFS5-2020) | Misumi | HFS5-2020-[L] (black: HFSB5-2020-[L]); e | 1 per length |  | TBD |
| 2020 extrusion Misumi-compatible cut, tapped both ends (Digmach) | Digmach | Misumi HFSB5-2020-xxx-TPW compatible | 1 | $7.95 | snippet, unconfirmed |
| V-Slot 20x20 (Maker Store, silver) | Maker Store USA | LR-2020-S | 1 |  | TBD |
| V-Slot 20x20 (Maker Store, black) | Maker Store USA | LR-2020-B | 1 |  | TBD |
| Slotted extrusion 20x20 610 mm (Adafruit 1221) | Adafruit | 1221 | 1 | $7.50 | listing |
| 80/20 20-2020 metric stock bar | Global Industrial (80/20 reseller) | 20-2020-6.05M | 1 | $81.95 | snippet, unconfirmed |
| Cast 90 deg corner bracket 20 series (Maker Store) | Maker Store USA | BRAC-90CAST | 1 | $1.80 | listing |
| Inside hidden corner bracket (Maker Store) | Maker Store USA | BRAC-INSIDE | 1 | $2.93 | listing |
| Universal L bracket double (Maker Store) | Maker Store USA | BRAC-L2 | 1 | $1.53 | listing |
| Corner brace 20x20 (Adafruit 1155) | Adafruit | 1155 | 1 | $0.95 | listing |

### bearings (18)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Flange bearing unit for 8 mm shaft (current BOM) | Phidgets | TRM4500_0 | 2 | $4.00 | listing |
| Pillow-block bearing for 8 mm shaft | Phidgets | TRM4501_0 | 2 | $4.25 | listing |
| 6802-2RS thin-section bearing 15x24x5 | VXB | Kit6993 | 10 | $29.99 | listing |
| 6803-2RS thin-section bearing 17x26x5 | VXB | 6803-2RS (10-pack) | 10 | $29.99 | listing |
| 6804-2RS thin-section bearing 20x32x7 | VXB | Kit1090 | 10 | $29.99 | listing |
| 6704-2RS extra-thin bearing 20x27x4 | VXB | Kit18219 | 1 | $9.99 | listing |
| 608-2RS bearing 8x22x7 | VXB | 1ASB | 10 | $14.99 | listing |
| F688-2RS flanged bearing 8x16x5 | VXB | kit970 | 10 | $49.99 | listing |
| F695 flanged bearing 5x13x4 | VXB | VXB0CRPG8XHS | 10 | $39.99 | listing |
| 51105 thrust ball bearing 25x42x11 | VXB | Kit7856 | 1 | $9.99 | listing |
| 51106 thrust ball bearing 30x47x11 | VXB | Kit7857 | 1 | $9.99 | listing |
| AXK2035 needle thrust bearing with AS2035 washers | VXB | VXB08FHTLDNZ | 5 | $39.99 | listing |
| F8-16M miniature thrust ball bearing 8x16x5 | VXB | VXB07W4PW6S1 | 10 | $39.99 | listing |
| Lazy-susan turntable bearing 140 mm | VXB | Kit12877 | 1 | $19.99 | listing |
| 8 mm precision ground rotary shaft (round, no flat) | Phidgets | TRM4000_0 |  | $6.50 | listing |
| 8 mm REX shaft 120 mm (round + 7 mm hex drive) | goBILDA | 2106-4008-1200 | 1 | $5.99 | listing |
| 8 mm or 10 mm D-profile shaft, McMaster | McMaster-Carr | TBD: metric 8/10 mm D-profile part numbe | 1 |  | TBD |
| 8 mm or 10 mm D-cut shaft, Misumi | Misumi | TBD: SFJ/PSFJ/SSFJ 8 or 10 with D-cut al | 1 |  | TBD |

### belt-drive (20)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| GT2 22T pulley, 8 mm bore (current BOM) | Phidgets | TRM4102_0 | 1 | $2.75 | listing |
| GT2 60T pulley, 8 mm bore (current BOM) | Phidgets | TRM4105_0 | 1 | $3.00 | listing |
| GT2 6 mm closed belt 220 mm (current BOM) | Phidgets | TRM4203_0 | 1 | $1.50 | listing |
| GT2 idler 44T, 8 mm bore | Phidgets | TRM4158_0 | 1 | $1.75 | listing |
| GT2 closed belts 6 mm wide, 180-296 mm | RobotDigg | <L>-2GT-6 | 1 | $0.45 | listing |
| GT2 closed belts 9 mm wide, 180-294 mm | RobotDigg | <L>-2GT-9 | 1 | $0.60 | listing |
| GT2 20T pulley, 5 mm bore | RobotDigg | GT2-20T-5B-6 | 1 | $1.10 | listing |
| GT2 20T pulley, 8 mm bore | RobotDigg | GT2-20T-8B-6 | 1 | $1.50 | listing |
| GT2 60T pulley, 8 or 10 mm bore, 6 mm belt | RobotDigg | GT2-60T-8B-6 / GT2-60T-10B-6 | 1 | $3.20 | listing |
| GT2 60T low-profile pulley, 8 or 10 mm bore, 9 mm belt | RobotDigg | LP2GT60-8B-9 / LP2GT60-10B-9 | 1 | $3.40 | listing |
| GT2 60T pulley, 10 mm bore, 9 mm belt (standard hub) | RobotDigg | GT2-60T-10B-9 | 1 | $6.40 | listing |
| GT2 idlers with bearings, 16T or 20T, toothed or smooth | RobotDigg | IP2GT-16T3B-7-T/-NO, IP2GT-20T5B-7-T/-NO | 1 | $1.60 | listing |
| GT2 20T pulley, 8 mm bore (Adafruit) | Adafruit | 1252 | 1 | $7.95 | listing |
| GT2 22T pulley, SDP-SI | SDP-SI | A 6D51M022DF0605 | 1 |  | TBD |
| GT2 60T pulley, SDP-SI (6 mm and 9 mm belt) | SDP-SI | A 6A51M060DF0606 / A 6A51M060DF0906 | 1 |  | TBD |
| Misumi GT2 timing pulleys | Misumi | TBD: GPA-series GT2 (2GT) code | 1 |  | TBD |
| McMaster GT2 (2MGT) pulleys and belts | McMaster-Carr | TBD | 1 |  | TBD |
| Gates 2M PowerGrip GT2 belt ratings (reference) | Gates (reference) | Synchronous Belt Data Summary 17611-T 3/ |  |  | TBD |
| Gates 3M HTD and 3M GT2 belt ratings (reference) | Gates (reference) | Synchronous Belt Data Summary 17611-T 3/ |  |  | TBD |
| 22:60 GT2 centre distances by belt length (computed reference) | computed | n/a |  |  | TBD |

### servo-mounting (10)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Feetech ST3215-C047 (STS3215 12 V 30 kg.cm) body and output | Feetech (datasheet via Seeed) | ST-3215-C047 |  |  | TBD |
| ST3215 2D outline drawing (Waveshare) incl. horn pattern | Waveshare | ST3215 (drawing title SCS215, 2022-06-08 |  |  | TBD |
| Feetech STS3250 12 V 50 kg.cm body and output | Feetech (datasheet via Evelta) | STS3250 |  |  | TBD |
| DS3235 coreless 35 kg servo body (DSSERVO) | DSSERVO (datasheet copy hosted by Univ. Rochester) | DS3235 / -180 / -270 |  |  | TBD |
| DS3225MG 25 kg servo body | DSSERVO (retailer listings) | DS3225MG |  |  | TBD |
| TowerPro MG996R body | TowerPro (datasheet copy hosted by Cornell) | MG996R |  |  | TBD |
| 25T aluminium round disc horn, 20 mm | generic (Probots listing used for specs) | 25T circular metal servo horn |  |  | TBD |
| Feetech FK-RP-001 round aluminium horn 20 mm | Botland (EU) | FK-RP-001 | 1 |  | TBD |
| ServoCity 1908 Series Servo Hub, 25T, 32 mm | ServoCity | 1908-0025-0032 | 1 | $8.99 | listing |
| Multi-function servo bracket + short U bracket kit (40x20x36 servos) | VXB | two sets pan tilt servo mount bracket fo | 2 |  | TBD |

### cad (3)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| STS3215 STEP model (TheRobotStudio SO-ARM100) | TheRobotStudio (GitHub) | STEP/SO100/STS3215_03a.step |  |  | TBD |
| STS3250 CAD | none found | STS3250 |  |  | TBD |
| AmazingHand CAD (Pollen Robotics) | Pollen Robotics (GitHub) | pollen-robotics/AmazingHand cad/ |  |  | TBD |

### springs (11)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Extension spring 0.625 OD, 27 lbf | Century Spring | 90CS | 1 | $9.37 | listing |
| Extension spring 0.75 OD, 22 lbf, long low-rate | Century Spring | 132CS | 1 | $11.84 | listing |
| Extension spring 0.5 OD, 17 lbf | Century Spring | 5357CS | 1 | $7.79 | listing |
| Extension spring 0.812 OD, 45 lbf, stiff | Century Spring | 5552CS | 1 | $9.05 | listing |
| Lee Spring stainless extension spring 0.5 OD | Lee Spring | MS24586-C207 | 1 | $22.83 | listing |
| McMaster-Carr extension spring 0.563 OD | McMaster-Carr | 9654K332 | 6 | $16.16 | listing |
| Existing BOM spring Grainger 1NAE3 | Grainger | 1NAE3 |  |  | TBD |
| Torsion spring 180 deg TO-5220RCS | Century Spring | TO-5220RCS | 1 | $6.43 | listing |
| Torsion spring 180 deg TO-1123CS | Century Spring | TO-1123CS | 1 | $7.10 | listing |
| McMaster gas spring 20 lbf, 7.48 in extended | McMaster-Carr (specs via third-party copy) | 4138T101 |  |  | TBD |
| Gas strut 10 in, 100 N, 2-pack | NIDAYE (seen on desertcart/Walmart) | NIDAYE 10in 100N | 2 |  | TBD |

### wiring (49)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| Silicone wire 12 AWG red+black | Amazon (BNTECHGO) | B01ABOPMEI | 2 x 10 ft |  | TBD |
| Silicone wire 14 AWG red+black | Amazon (BNTECHGO) | B017TFR6SM | TBD: length per colour on listing |  | TBD |
| Silicone wire 16 AWG red+black | Amazon (BNTECHGO) | B017TFR664 | 2 x 10 ft |  | TBD |
| Silicone wire 18 AWG red+black | Newegg (BNTECHGO) | TBD: Amazon ASIN not found | TBD |  | TBD |
| Silicone wire 20 AWG black spool | Amazon (BNTECHGO) | B01K4QVI46 | 100 ft |  | TBD |
| Silicone wire 22 AWG 7-colour kit | Amazon (BNTECHGO) | B08FMF3NBL | 7 x 50 ft |  | TBD |
| XT60 male-female pair | Pololu | 2175 | 1 pair | $2.95 | listing |
| Amass XT60H connectors, 5 sets | GetFPV (Amass) | Amass XT60H-M / XT60H-F (GetFPV SKU 1178 | 5 pairs |  | TBD |
| Amass XT30U connectors, 5 pairs | GetFPV (Amass) | Amass XT30U-M / XT30U-F | 5 pairs | $7.69 | snippet, unconfirmed |
| Powerpole PP15/45 housing, red | Mouser (Anderson) | 1327 | 1 | $0.73 | listing |
| Powerpole PP15/45 housing, black | Mouser (Anderson) | 1327G6 | 1 | $0.73 | listing |
| Powerpole 15 A contact | Mouser (Anderson) | 1332 | 1 | $0.55 | listing |
| Powerpole 30 A contact | Mouser (Anderson) | 1331 | 1 | $0.51 | listing |
| Powerpole 45 A contact | Mouser (Anderson) | 261G2 | 1 | $0.36 | listing |
| Powerpole 30 A sets, unassembled, 10 | Powerwerx | PP30-10 | 10 sets |  | TBD |
| Powerpole 15 A sets, unassembled, 10 | Powerwerx | PP15-10 | 10 sets | $12.99 | snippet, unconfirmed |
| Powerpole 45 A sets, unassembled, 10 | Powerwerx | PP45-10 | 10 sets | $19.99 | snippet, unconfirmed |
| Molex Mini-SPOX 3P receptacle housing | Digi-Key (Molex) | 0050375033 (50-37-5033) | 1 | $0.14 | listing |
| Molex Mini-SPOX crimp socket 22-28 AWG | Digi-Key (Molex) | 0008701040 (08-70-1040) | 1 | $0.23 | listing |
| Feetech 5264 3P servo cable 300 mm, 6 pcs | Waveshare | SR-Cable-5264-3PIN-300mm-6PCS | 6 | $1.99 | listing |
| Feetech 5264 3P servo cable 900 mm, 6 pcs | Waveshare | SR-Cable-5264-3PIN-900mm-6PCS | 6 | $3.99 | snippet, unconfirmed |
| Feetech 5264 3P cable 15 cm | aifitlab (Feetech) | FEETECH 5264 Terminal Cable 15 cm | 1 | $3.00 | snippet, unconfirmed |
| Servo extension 300 mm M-F | Pololu | 2184 | 1 | $4.64 | listing |
| Servo extension 600 mm M-F (nearest to 500 mm) | Pololu | 2185 | 1 | $6.58 | listing |
| JST-PH compatible 2.0 mm crimp kit | Adafruit | 4422 | 220 pcs | $8.95 | listing |
| JST-XH compatible 2.5 mm crimp kit | Adafruit | 4423 | '560 pcs' (itemised list sums to 360) | $24.95 | listing |
| Ferrule crimp kit, 1200 ferrules | Amazon (Preciva) | TBD: ASIN unconfirmed (B073TZ5BBG report | 1 kit |  | TBD |
| Heat shrink kit 3:1 adhesive-lined, 180 pcs | Amazon (Wirefy) | B084GDLSCK | 180 pcs |  | TBD |
| Heat shrink kit 2:1 assorted colour, 3M | Mouser (3M) | FP-301 KIT | 1 kit | $153.57 | listing |
| Braided expandable sleeving 1/4 in (~6 mm) | Altex (Techflex) | PTN0.25BK | per ft | $0.99 | snippet, unconfirmed |
| Braided expandable sleeving 3/8 in (~10 mm) | Techflex | PTN0.38BK | TBD |  | TBD |
| Braided expandable sleeving 1/2 in (~13 mm) | Techflex | PTN0.50BK | TBD |  | TBD |
| Cable drag chain 10x15 mm, 1 m | VXB | 10x15 drag chain PA66 | 1 m |  | TBD |
| Spiral wrap 1/4 in x 100 ft | Mouser (Panduit) | T25N-C | 100 ft | $160.68 | listing |
| Cable ties 99 mm miniature, 100 pk | Mouser (Panduit) | PLT1M-C | 100 | $21.20 | listing |
| Cable ties 188 mm standard, 100 pk | Mouser (Panduit) | PLT2S-C | 100 | $29.30 | listing |
| WAGO 221-412 lever splice 2-pos | Digi-Key (WAGO) | 221-412 | 1 | $0.62 | listing |
| WAGO 221-413 lever splice 3-pos | Digi-Key (WAGO) | 221-413 | 1 | $0.76 | listing |
| WAGO 221-415 lever splice 5-pos | Digi-Key (WAGO) | 221-415 | 1 | $1.17 | listing |
| 2-position barrier terminal block | Mouser (Cinch) | 2-140 | 1 | $10.68 | listing |
| DIN feed-through terminal block UK 5 N | Mouser (Phoenix Contact) | 3004362 | 1 | $3.20 | listing |
| ATO fuse 10 A, Littelfuse | Mouser (Littelfuse) | 0287010.PXCN | 1 | $0.36 | listing |
| ATO fuse 30 A, Littelfuse | Mouser (Littelfuse) | 0287030.PXCN | 1 | $0.36 | listing |
| ATC fuse 10 A, Bussmann | Mouser (Eaton Bussmann) | ATC-10 | Standard pack 5 (price basis unclear) | $4.03 | listing |
| ATC fuse 30 A, Bussmann | Mouser (Eaton Bussmann) | ATC-30 | Standard pack 5 (price basis unclear) | $5.20 | listing |
| Ring terminal 16-14 AWG #10 | Mouser (Panduit) | PV14-10R-C | 1 (pack 100) | $0.79 | listing |
| Ring terminal 16-14 AWG #8 | Mouser (Panduit) | PV14-8R-C | 1 (pack 100) | $1.21 | listing |
| Ring terminal 12-10 AWG #10 | Mouser (Panduit) | PV10-10R-L | 1 (pack 50) | $1.33 | listing |
| Ring terminal 12-10 AWG #8 | Mouser (Panduit) | PV10-8R-L | 1 (pack 50) | $1.29 | listing |

### printing (13)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| PETG 1 kg (Prusament) | Prusa Research (maker store) | Prusament PETG Jet Black 1kg | 1 | $23.99 | listing |
| PETG 1 kg (Polymaker) | MatterHackers | Polymaker PolyLite PETG 1.75mm 1kg | 1 | $21.99 | snippet, unconfirmed |
| PETG 1 kg (Elegoo Rapid PETG) | Amazon (ELEGOO official) | ELEGOO Rapid PETG 1.75mm 1kg | 4 |  | TBD |
| PLA+ 1 kg (eSUN) | MatterHackers | eSUN PLA+ Black 1.75mm 1kg | 1 | $22.99 | snippet, unconfirmed |
| PLA+ 1 kg (Elegoo) | Amazon (ELEGOO Official US) | ELEGOO PLA+ 1.75mm 1kg x4 | 4 | $36.99 | snippet, unconfirmed |
| PLA+ 1 kg (Overture) | Wood Art Supply | Overture PLA Plus 1.75mm 1kg Black | 1 | $15.99 | snippet, unconfirmed |
| CF-PETG 1 kg (Bambu Lab PETG-CF) | 3D Universe (US Bambu reseller) | Bambu Lab PETG-CF 1.75mm 1kg | 1 | $34.99 | snippet, unconfirmed |
| CF-PETG 1 kg (eSUN PETG-CF) | 3DJake | eSUN PETG-CF Black 1.75mm 1kg | 1 | $28.13 | snippet, unconfirmed |
| CF-PETG 0.5 kg (Polymaker Fiberon PETG-rCF08) | Polymaker (maker store) | Fiberon PETG-rCF08 1.75mm 0.5kg | 1 | $19.99 | listing |
| CF-PETG 1 kg (MatterHackers Build Series PETG-CF) | MatterHackers | MH Build Series PETG-CF Black 1.75mm 1kg | 1 | $35.99 | snippet, unconfirmed |
| CF-PET 0.5 kg (Polymaker Fiberon PET-CF17) | Polymaker (maker store) | Fiberon PET-CF17 1.75mm 0.5kg | 1 | $24.99 | snippet, unconfirmed |
| PA6-CF (Polymaker Fiberon PA6-CF20) | Polymaker (maker store) | Fiberon PA6-CF20 1.75mm | 1 | $39.99 | listing |
| PA6-CF 1 kg (Bambu Lab PA6-CF) | 3DJake | Bambu Lab PA6-CF Black 1kg | 1 | $79.80 | snippet, unconfirmed |

### base (15)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| 1 in x 36 in black steel pipe nipple (Plumbing Supply and More) | Plumbing Supply and More | MPN 585-360HC / SKU 11239 | 1 | $10.97 | listing |
| 1 in x 36 in Sch 40 black nipple (Global Industrial) | Global Industrial (MSI) | WBB3783128 / A277001636.0 | 1 | $20.25 | listing |
| 1 in black malleable floor flange (Anvil FIG 1190) | Dillon Supply | Anvil FIG 1190 1 in black (Dillon 291110 | 1 | $32.87 | snippet, unconfirmed |
| 1 in black floor flange (Pannext B-FLF10) | Walmart (Pannext) | B-FLF10 | 1 | $16.94 | snippet, unconfirmed |
| Kee Klamp 61-6 slip-on flange, 1 in pipe | Simplified Building | 61-6 | 1 |  | TBD |
| U-bolt for 1 in pipe, 1/4-20 extended thread (McMaster 8875T853) | McMaster-Carr | 8875T853 (5-pack possibly 8875T87) | 1 |  | TBD |
| 1/4 in birch plywood 2x4 ft (cut to 2x2) | Home Depot | Internet # 202088745 / model 1503008 | 1 |  | TBD |
| 1/4 in 2x2 ft sanded pine plywood | Home Depot | Internet # 205603419 | 1 |  | TBD |
| 3/4 in birch plywood 2x2 ft | Home Depot | Falken Design FALKENDESIGN-PW-Birch-A2-3 | 1 | $29.49 | snippet, unconfirmed |
| 24 in round birch disc 1/2 in | Wood Art Supply (Woodpeckers brand) | Woodpeckers wood circle 24 in x 1/2 in | 1 | $41.61 | snippet, unconfirmed |
| 24 in round Baltic birch panel 1/2 in | Trekell | Raw Round Wood Panel 1/2 in Baltic Birch | 1 | $98.99 | snippet, unconfirmed |
| 24 in round table top (laminate, not plywood) | Home Depot | Flash Furniture XURD24MBT (Internet # 30 | 1 | $40.71 | snippet, unconfirmed |
| Felt pads 2 in round, heavy duty | Home Depot | Everbilt 49927 (Internet # 203661116) | 4 | $5.27 | snippet, unconfirmed |
| Levelling feet 3/8-16 (10-pack) | Home Depot | Angel Sar ECPQ8508 (Internet # 331622743 | 10 | $58.33 | snippet, unconfirmed |
| Levelling mount 3/8-16 rubber base | McMaster-Carr | TBD: choose on page (Base Material: Rubb | 1 |  | TBD |

### misc (15)

| Item | Vendor | Part | Pack | Price | Status |
|---|---|---|---|---:|---|
| M18 battery wall mount (StealthMounts, 6-pack) | Tool Nut / Walmart | StealthMounts BM-MW18-BLK-6 | 6 | $24.99 | snippet, unconfirmed |
| M18 battery holder (printed, Printables 1118857) | Printables | model 1118857 | 1 | $0.00 | listing |
| M12/M18 locking battery wall mounts (printed, Printables 621105) | Printables | model 621105 | 1 | $0.00 | listing |
| Cable gland PG7 nylon | Mouser | Alpha Wire PPC7 BK080 (Mouser 602-PPC7-B | 1 | $2.97 | listing |
| Cable gland PG9 nylon | Mouser | Alpha Wire PPC9 BK080 (Mouser 602-PPC9-B | 1 | $3.38 | listing |
| E-stop enclosure, 1-hole yellow (Schneider XALK01H7) | Mouser | Schneider Electric XALK01H7 (Mouser 996- | 1 | $26.02 | listing |
| E-stop enclosure, 1-hole yellow (Eaton M22-IY1) | Mouser | Eaton M22-IY1 (Mouser 504-M22-IY1) | 1 | $89.97 | listing |
| E-stop station complete (IDEC FB1W-HW1B-V402R) | Mouser | IDEC FB1W-HW1B-V402R (Mouser 199-FB1WHW1 | 1 | $78.91 | listing |
| E-stop station complete (Schneider XALK178) | Mouser | Schneider Electric XALK178 (Mouser 996-X | 1 | $108.05 | listing |
| 35 mm DIN rail, 1 m | Digi-Key | Weidmuller 0514510000 (Digi-Key 281-1534 | 1 | $16.60 | listing |
| Electronics enclosure, PC 120x120x61 mm (Hammond 1554N2GY) | Mouser | Hammond 1554N2GY (Mouser 546-1554N2GY; D | 1 | $25.67 | listing |
| Electronics enclosure, PC 180x180x60 mm (Hammond 1554W2GY) | Mouser | Hammond 1554W2GY (Mouser 546-1554W2GY) | 1 | $35.65 | listing |
| Electronics enclosure, PC 120x65x40 mm (Hammond 1554C2GY) | Mouser | Hammond 1554C2GY (Mouser 546-1554C2GY) | 1 | $18.50 | listing |
| Electronics enclosure, ABS 112x85x44 mm (Hammond 1591XXSSBK) | Mouser | Hammond 1591XXSSBK (Mouser 546-1591XXSSB | 1 | $8.54 | listing |
| Electronics enclosure, ABS 221x150x64 mm (Hammond 1591XXFSBK) | Mouser | Hammond 1591XXFSBK (Mouser 546-1591XXFSB | 1 | $12.71 | listing |

