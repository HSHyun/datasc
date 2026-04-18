## Column

| Column | Meaning |
| --- | --- |
| `fr_orig` | 해외 출발 지역 코드 (국내 출발이거나 수출 같은 경우는 null) |
| `dms_orig` | 미국 내 출발 지역 또는 주. 수입의 경우 미국 반입 지점. |
| `dms_dest` | 미국 내 도착 지역 또는 주. 수출의 경우 미국 반출 지점. |
| `fr_dest` | 해외 도착 지역 코드 |
| `fr_inmode` | 해외에서 미국 반입 지점까지 들어올 때 사용한 운송수단 |
| `dms_mode` | 미국 국내에서 운송수단 |
| `fr_outmode` | 미국 반출 지점에서 해외 도착 지역까지 사용한 운송수단 |
| `sctg2` | 운송된 화물의 품목 코드 |
| `trade_type` | 국내이동 / 수입 / 수출 |
| `dist_band` | 이동 거리범위. 미국 국내에서 돌아다닌 것만 침. 해외에서의 거리는 포함 안함 |
| `tons_YYYY` | 해당 연도 화물 중량. 단위: 천 톤(1,000 t) |
| `value_YYYY` | 해당 연도의 운반된 가치를 2017년 불변 달러를 기준으로 환산한 가치. 단위: 백만 달러 |
| `current_value_YYYY` | 해당 연도의 운반된 실제 가치. 단위: 백만 달러 |
| `tmiles_YYYY` | 화물 중량 x 이동거리. 단위: 백만 톤마일 |

`YYYY` = `2018` \~ `2024`

## 정리

- 국내 -&gt; 국내

  - `fr_orig` = `null`
  - `dms_orig` = 처음 시작 지점
  - `dms_dest` = 마지막 도착 지점
  - `fr_dest` = `null`

- 해외 -&gt; 국내

  - `fr_orig` = 해외 출발 지역
  - `dms_orig` = 미국 국내 운송 시작 지점
  - `dms_dest` = 마지막 미국 내 도착 지점
  - `fr_dest` = `null`

- 국내 -&gt; 해외

  - `fr_orig` = `null`
  - `dms_orig` = 처음 미국 내 출발 지점
  - `dms_dest` = 해외로 나가기 직전 마지막 미국 지역
  - `fr_dest` = 해외 도착 지역

 

## 운송 수단

### `fr_inmode`, `dms_mode`, `fr_outmode`

| Code | Meaning |
| --- | --- |
| `1` | Truck |
| `2` | Rail |
| `3` | Water |
| `4` | Air (include truck-air) |
| `5` | Multiple modes & mail |
| `6` | Pipeline |
| `7` | Other and unknown |
| `8` | No domestic mode |

 

## 거래 유형

### `trade_type`

| Code | Meaning |
| --- | --- |
| `1` | Domestic flows |
| `2` | Import flows |
| `3` | Export flows |

 

## 운송 거리범위

### `dist_band`

| Code | Meaning |
| --- | --- |
| `1` | Below 100 |
| `2` | 100 - 249 |
| `3` | 250 - 499 |
| `4` | 500 - 749 |
| `5` | 750 - 999 |
| `6` | 1,000 - 1,499 |
| `7` | 1,500 - 2,000 |
| `8` | Over 2,000 |

## 해외 지역 코드

### `fr_orig`, `fr_dest`

| Code | Meaning |
| --- | --- |
| `801` | Canada |
| `802` | Mexico |
| `803` | Rest of Americas |
| `804` | Europe |
| `805` | Africa |
| `806` | SW & Central Asia |
| `807` | Eastern Asia |
| `808` | SE Asia & Oceania |

 

## 품목 코드

### `sctg2`

| Code | Meaning |
| --- | --- |
| `01` | Live animals/fish |
| `02` | Cereal grains |
| `03` | Other ag prods. |
| `04` | Animal feed |
| `05` | Meat/seafood |
| `06` | Milled grain prods. |
| `07` | Other foodstuffs |
| `08` | Alcoholic beverages |
| `09` | Tobacco prods. |
| `10` | Building stone |
| `11` | Natural sands |
| `12` | Gravel |
| `13` | Nonmetallic minerals |
| `14` | Metallic ores |
| `15` | Coal |
| `16` | Crude petroleum |
| `17` | Gasoline |
| `18` | Fuel oils |
| `19` | Natural gas and other fossil products |
| `20` | Basic chemicals |
| `21` | Pharmaceuticals |
| `22` | Fertilizers |
| `23` | Chemical prods. |
| `24` | Plastics/rubber |
| `25` | Logs |
| `26` | Wood prods. |
| `27` | Newsprint/paper |
| `28` | Paper articles |
| `29` | Printed prods. |
| `30` | Textiles/leather |
| `31` | Nonmetal min. prods. |
| `32` | Base metals |
| `33` | Articles-base metal |
| `34` | Machinery |
| `35` | Electronics |
| `36` | Motorized vehicles |
| `37` | Transport equip. |
| `38` | Precision instruments |
| `39` | Furniture |
| `40` | Misc. mfg. prods. |
| `41` | Waste/scrap |
| `43` | Mixed freight |

## 지역 코드

- `State` = 2자리 코드
- `FAF Zone (Domestic)` = 3자리 코드
- 실제 `dms_orig`, `dms_dest` 값들은 3자리 코드로 들어 있어서 `FAF Zone (Domestic)` 기준으로 해석하면 됨

## State

| Numeric Label | Description |
| --- | --- |
| 01 | Alabama |
| 02 | Alaska |
| 04 | Arizona |
| 05 | Arkansas |
| 06 | California |
| 08 | Colorado |
| 09 | Connecticut |
| 10 | Delaware |
| 11 | Washington DC |
| 12 | Florida |
| 13 | Georgia |
| 15 | Hawaii |
| 16 | Idaho |
| 17 | Illinois |
| 18 | Indiana |
| 19 | Iowa |
| 20 | Kansas |
| 21 | Kentucky |
| 22 | Louisiana |
| 23 | Maine |
| 24 | Maryland |
| 25 | Massachusetts |
| 26 | Michigan |
| 27 | Minnesota |
| 28 | Mississippi |
| 29 | Missouri |
| 30 | Montana |
| 31 | Nebraska |
| 32 | Nevada |
| 33 | New Hampshire |
| 34 | New Jersey |
| 35 | New Mexico |
| 36 | New York |
| 37 | North Carolina |
| 38 | North Dakota |
| 39 | Ohio |
| 40 | Oklahoma |
| 41 | Oregon |
| 42 | Pennsylvania |
| 44 | Rhode Island |
| 45 | South Carolina |
| 46 | South Dakota |
| 47 | Tennessee |
| 48 | Texas |
| 49 | Utah |
| 50 | Vermont |
| 51 | Virginia |
| 53 | Washington |
| 54 | West Virginia |
| 55 | Wisconsin |
| 56 | Wyoming |

## FAF Zone (Domestic)

| Numeric Label | Short Description | Long Description |
| --- | --- | --- |
| 011 | Birmingham AL | Birmingham-Hoover-Talladega, AL CFS Area |
| 012 | Mobile AL | Mobile-Daphne-Fairhope, AL CFS Area |
| 019 | Rest of AL | Remainder of Alabama |
| 020 | Alaska | Alaska |
| 041 | Phoenix AZ | Phoenix-Mesa-Scottsdale, AZ CFS Area |
| 042 | Tucson AZ | Tucson-Nogales, AZ CFS Area |
| 049 | Rest of AZ | Remainder of Arizona |
| 050 | Arkansas | Arkansas |
| 061 | Los Angeles CA | Los Angeles-Long Beach, CA CFS Area |
| 062 | Sacramento CA | Sacramento-Roseville, CA CFS Area |
| 063 | San Diego CA | San Diego-Carlsbad, CA CFS Area |
| 064 | San Francisco CA | San Jose-San Francisco-Oakland, CA CFS Area |
| 065 | Fresno CA | Fresno-Madera, CA CFS Area |
| 069 | Rest of CA | Remainder of California |
| 081 | Denver CO | Denver-Aurora, CO CFS Area |
| 089 | Rest of CO | Remainder of Colorado |
| 091 | Hartford CT | Hartford-West Hartford-East Hartford, CT CFS Area |
| 092 | New York NY-NJ-CT-PA (CT Part) | New York-Newark, NY-NJ-CT-PA CFS Area (CT Part) |
| 099 | Rest of CT | Remainder of Connecticut |
| 101 | Philadelphia PA-NJ-DE-MD (DE Part) | Philadelphia-Reading-Camden, PA-NJ-DE-MD CFS Area (DE Part) |
| 109 | Rest of DE | Remainder of Delaware |
| 111 | Washington DC-VA-MD-WV (DC Part) | Washington-Arlington-Alexandria, DC-VA-MD-WV CFS Area (DC Part) |
| 121 | Jacksonville FL-GA CFS Area (FL Part) | Jacksonville-St. Marys-Palatka, FL-GA CFS Area (FL Part) |
| 122 | Miami FL | Miami-Fort Lauderdale-Port St. Lucie, FL CFS Area |
| 123 | Orlando FL | Orlando-Deltona-Daytona Beach, FL CFS Area |
| 124 | Tampa FL | Tampa-St. Petersburg-Clearwater, FL CFS Area |
| 129 | Rest of FL | Remainder of Florida |
| 131 | Atlanta GA | Atlanta-Athens-Clarke County-Sandy Springs, GA CFS Area |
| 132 | Savannah GA | Savannah-Hinesville-Statesboro, GA CFS Area |
| 139 | Rest of GA | Remainder of Georgia |
| 151 | Honolulu HI | Urban Honolulu, HI CFS Area |
| 159 | Rest of HI | Remainder of Hawaii |
| 160 | Idaho | Idaho |
| 171 | Chicago IL-IN-WI (IL Part) | Chicago-Naperville, IL-IN-WI CFS Area (IL Part) |
| 172 | St. Louis MO-IL (IL Part) | St. Louis-St. Charles-Farmington, MO-IL CFS Area (IL Part) |
| 179 | Rest of IL | Remainder of Illinois |
| 181 | Chicago IL-IN-WI (IN Part) | Chicago-Naperville, IL-IN-WI CFS Area (IN Part) |
| 182 | Indianapolis IN | Indianapolis-Carmel-Muncie, IN CFS Area |
| 183 | Fort Wayne IN | Fort Wayne-Huntington-Auburn, IN CFS Area |
| 189 | Rest of IN | Remainder of Indiana |
| 190 | Iowa | Iowa |
| 201 | Kansas City MO-KS (KS Part) | Kansas City-Overland Park-Kansas City, MO-KS CFS Area (KS Part) |
| 202 | Wichita KS | Wichita-Arkansas City-Winfield, KS CFS Area |
| 209 | Rest of KS | Remainder of Kansas |
| 211 | Cincinnati OH-KY-IN (KY Part) | Cincinnati-Wilmington-Maysville, OH-KY-IN CFS Area (KY Part) |
| 212 | Louisville KY-IN (KY Part) | Louisville/Jefferson County-Elizabethtown-Madison, KY-IN CFS Area (KY Part) |
| 219 | Rest of KY | Remainder of Kentucky |
| 221 | Baton Rouge LA | Baton Rouge, LA CFS Area |
| 222 | Lake Charles-Jennings LA | Lake Charles-Jennings, LA CFS Area |
| 223 | New Orleans LA-MS (LA Part) | New Orleans-Metairie-Hammond, LA-MS CFS Area (LA Part) |
| 229 | Rest of LA | Remainder of Louisiana |
| 230 | Maine | Maine |
| 241 | Baltimore MD | Baltimore-Columbia-Towson, MD CFS Area |
| 242 | Washington DC-VA-MD-WV (MD Part) | Washington-Arlington-Alexandria, DC-VA-MD-WV CFS Area (MD Part) |
| 249 | Rest of MD | Remainder of Maryland |
| 251 | Boston MA-RI-NH-CT (MA Part) | Boston-Worcester-Providence, MA-RI-NH-CT CFS Area (MA Part) |
| 259 | Rest of MA | Remainder of Massachusetts |
| 261 | Detroit MI | Detroit-Warren-Ann Arbor, MI CFS Area |
| 262 | Grand Rapids MI | Grand Rapids-Wyoming-Muskegon, MI CFS Area |
| 269 | Rest of MI | Remainder of Michigan |
| 271 | Minneapolis-St. Paul MN-WI (MN Part) | Minneapolis-St. Paul, MN-WI CFS Area (MN Part) |
| 279 | Rest of MN | Remainder of Minnesota |
| 280 | Mississippi | Mississippi |
| 291 | Kansas City MO-KS (MO Part) | Kansas City-Overland Park-Kansas City, MO-KS CFS Area (MO Part) |
| 292 | St. Louis MO-IL (MO Part) | St. Louis-St. Charles-Farmington, MO-IL CFS Area (MO Part) |
| 299 | Rest of MO | Remainder of Missouri |
| 300 | Montana | Montana |
| 311 | Omaha NE-IA (NE Part) | Omaha-Council Bluffs-Fremont, NE-IA CFS Area (NE Part) |
| 319 | Rest of NE | Remainder of Nebraska |
| 321 | Las Vegas NV-AZ (NV Part) | Las Vegas-Henderson, NV-AZ CFS Area (NV Part) |
| 329 | Rest of NV | Remainder of Nevada |
| 331 | Boston MA-RI-NH-CT (NH Part) | Boston-Worcester-Providence, MA-RI-NH-CT CFS Area (NH Part) |
| 339 | Rest of NH | Remainder of New Hampshire |
| 341 | New York NY-NJ-CT-PA (NJ Part) | New York-Newark, NY-NJ-CT-PA CFS Area (NJ Part) |
| 342 | Philadelphia PA-NJ-DE-MD (NJ Part) | Philadelphia-Reading-Camden, PA-NJ-DE-MD CFS Area (NJ Part) |
| 350 | New Mexico | New Mexico |
| 361 | Albany NY CFS Area | Albany-Schenectady, NY CFS Area |
| 362 | Buffalo NY CFS Area | Buffalo-Cheektowaga, NY CFS Area |
| 363 | New York NY-NJ-CT-PA (NY Part) | New York-Newark, NY-NJ-CT-PA CFS Area (NY Part) |
| 364 | Rochester NY | Rochester-Batavia-Seneca Falls, NY CFS Area |
| 369 | Rest of NY | Remainder of New York |
| 371 | Charlotte NC-SC (NC Part) | Charlotte-Concord, NC-SC CFS Area (NC Part) |
| 372 | Greensboro--Winston-Salem--High Point NC | Greensboro--Winston-Salem--High Point, NC CFS Area |
| 373 | Raleigh-Durham NC | Raleigh-Durham-Chapel Hill, NC CFS Area |
| 379 | Rest of NC | Remainder of North Carolina |
| 380 | North Dakota | North Dakota |
| 391 | Cincinnati OH-KY-IN (OH Part) | Cincinnati-Wilmington-Maysville, OH-KY-IN CFS Area (OH Part) |
| 392 | Cleveland OH | Cleveland-Akron-Canton, OH CFS Area |
| 393 | Columbus OH | Columbus-Marion-Zanesville, OH CFS Area |
| 394 | Dayton OH | Dayton-Springfield-Sidney, OH CFS Area |
| 399 | Rest of OH | Remainder of Ohio |
| 401 | Oklahoma City OK | Oklahoma City-Shawnee, OK CFS Area |
| 402 | Tulsa OK | Tulsa-Muskogee-Bartlesville, OK CFS Area |
| 409 | Rest of OK | Remainder of Oklahoma |
| 411 | Portland OR-WA (OR Part) | Portland-Vancouver-Salem, OR-WA CFS Area (OR Part) |
| 419 | Rest of OR | Remainder of Oregon |
| 421 | Philadelphia PA-NJ-DE-MD (PA Part) | Philadelphia-Reading-Camden, PA-NJ-DE-MD CFS Area (PA Part) |
| 422 | Pittsburgh PA-OH-WV (PA Part) | Pittsburgh-New Castle-Weirton, PA-OH-WV CFS Area (PA Part) |
| 423 | New York NY-NJ-CT-PA (PA Part) | New York-Newark, NY-NJ-CT-PA CFS Area (PA Part) |
| 429 | Rest of PA | Remainder of Pennsylvania |
| 441 | Boston MA-RI-NH-CT (RI Part) | Boston-Worcester-Providence, MA-RI-NH-CT CFS Area (RI Part) |
| 451 | Charleston SC | Charleston-North Charleston, SC CFS Area |
| 452 | Greenville SC | Greenville-Spartanburg-Anderson, SC CFS Area |
| 459 | Rest of SC | Remainder of South Carolina |
| 460 | South Dakota | South Dakota |
| 471 | Memphis TN-MS-AR (TN Part) | Memphis-Forrest City, TN-MS-AR CFS Area (TN Part) |
| 472 | Nashville TN | Nashville-Davidson--Murfreesboro, TN CFS Area |
| 473 | Knoxville TN | Knoxville-Morristown-Sevierville, TN CFS Area |
| 479 | Rest of TN | Remainder of Tennessee |
| 481 | Austin TX | Austin-Round Rock, TX CFS Area |
| 482 | Beaumont TX | Beaumont-Port Arthur, TX CFS Area |
| 483 | Corpus Christi TX | Corpus Christi-Kingsville-Alice, TX CFS Area |
| 484 | Dallas-Fort Worth TX-OK (TX Part) | Dallas-Fort Worth, TX-OK CFS Area (TX Part) |
| 485 | El Paso TX-NM (TX Part) | El Paso-Las Cruces, TX-NM CFS Area (TX Part) |
| 486 | Houston TX | Houston-The Woodlands, TX CFS Area |
| 487 | Laredo TX | Laredo, TX CFS Area |
| 488 | San Antonio TX | San Antonio-New Braunfels, TX CFS Area |
| 489 | Rest of TX | Remainder of Texas |
| 491 | Salt Lake City UT | Salt Lake City-Provo-Orem, UT CFS Area |
| 499 | Rest of UT | Remainder of Utah |
| 500 | Vermont | Vermont |
| 511 | Richmond VA | Richmond, VA CFS Area |
| 512 | Virginia Beach-Norfolk VA-NC (VA Part) | Virginia Beach-Norfolk, VA-NC CFS Area (VA Part) |
| 513 | Washington DC-VA-MD-WV (VA Part) | Washington-Arlington-Alexandria, DC-VA-MD-WV CFS Area (VA Part) |
| 519 | Rest of VA | Remainder of Virginia |
| 531 | Seattle WA | Seattle-Tacoma, WA CFS Area |
| 532 | Portland OR-WA (WA Part) | Portland-Vancouver-Salem, OR-WA CFS Area (WA Part) |
| 539 | Rest of WA | Remainder of Washington |
| 540 | West Virginia | West Virginia |
| 551 | Milwaukee WI | Milwaukee-Racine-Waukesha, WI CFS Area |
| 559 | Rest of WI | Remainder of Wisconsin |
| 560 | Wyoming | Wyoming |

 

 

# Boxplot 기반 IQR 해석

tons 값의 규모 차이가 매우 크기 때문에, 원자료의 왜곡을 줄이기 위해 로그 변환 후 boxplot을 확인하였다. boxplot에서 Q1, 중앙값(Q2), Q3가 모두 낮은 값 구간에 몰려 있다는 것은 데이터의 중심부 대부분이 작은 톤수에 집중되어 있음을 의미한다. 반면 수염 상단인 Q3 + 1.5×IQR을 초과하는 값들은 점으로 따로 표시되며, 일반적인 boxplot 해석에서는 이를 이상치로 본다. 그러나 FAF5 Truck 데이터는 대형 벌크 화물과 핵심 회랑이 포함된 물류 데이터이기 때문에, 원래 소수의 대형 흐름과 다수의 소규모 흐름이 공존하는 heavy-tail 분포를 가진다. 따라서 boxplot상 큰 값들을 곧바로 오류로 간주하지 않고, 우선 통계적으로 일반 범위를 벗어난 이상치 후보로 해석하였다.

# **YoY 기반 급변 흐름 해석**

YoY(Year over Year)는 동일한 O-D-품목 흐름이 전년 대비 얼마나 변했는지를 보는 지표다. 본 분석에서는 같은 O-D-품목 조합에 대해 직전 연도 대비 tons, value, tmiles의 변화율을 계산하고, 변화율의 절댓값이 일정 임계치 이상인 경우를 이상치 후보로 표시하였다. 이 방법은 절대적으로 큰 값을 찾는 것이 아니라, 원래 규모와 무관하게 1년 사이에 급격히 증가하거나 감소한 흐름을 찾는 데 목적이 있다. 따라서 FAF5처럼 원래 큰 벌크 화물이 존재하는 데이터에서도 단순 고값과 구분하여, 구조적 변화나 외부 충격이 반영된 특이 흐름을 식별하는 데 유용하다. 본 분석에서는 이러한 급변 흐름을 제거 대상이 아니라, 추가 해석이 필요한 이상치 후보로 해석하였다.

또한 YoY 임계값에 대한 민감도 비교 결과, 30% 기준은 수천 건의 후보를 탐지해 정상 변동까지 과도하게 포함하는 경향을 보였고, 100% 기준은 극단적 변화만 남겨 의미 있는 급변 흐름까지 놓칠 가능성이 있었다. 반면 50% 기준은 과도한 탐지를 줄이면서도 연도별 구조적 변화가 반영된 흐름을 적절한 수로 포착해, 본 분석의 기준값으로 사용하였다. 품목별로 보면 급변 후보는 곡물(Cereal grains), 원목(Logs), 화석연료류(Natural gas and other fossil products), 자갈(Gravel), 석탄(Coal)과 같은 벌크·원자재 품목에 집중되었다. 이는 FAF5에서 관측된 특이값이 단순 오류라기보다, 실제 산업재·에너지 계열 물류 흐름의 변동성을 반영하고 있음을 시사한다. 특히 2021년에 YoY 급변 후보가 크게 증가한 것은 2020년 팬데믹 충격 이후 산업 활동과 공급망이 재조정되는 과정이 반영된 결과로 해석할 수 있다. 즉 2021년은 모든 흐름이 일괄적으로 증가한 해라기보다, 품목과 회랑별 회복 속도가 달라지면서 전년 대비 큰 증감이 동시에 나타난 시기라고 볼 수 있다.

# Isolation Forest 기반 다변량 해석

Isolation Forest는 tons, value, tmiles를 동시에 고려하여 다른 흐름들과 비교했을 때 구조적으로 고립된 관측치를 탐지하는 다변량 이상치 탐지 방법이다. 본 분석에서는 각 연도별로 로그 변환된 tons, value, tmiles를 입력 변수로 사용하고, 연도마다 300개의 트리로 구성된 Isolation Forest를 학습하였다. 각 트리는 해당 연도 데이터에서 최대 2048개 샘플을 무작위로 사용해 분할을 수행하며, 관측치가 여러 트리에서 평균적으로 얼마나 빨리 고립되는지를 바탕으로 이상치 점수를 계산한다. 다만 본 방법은 contamination=0.01 설정에 따라 이상치 후보 비율이 결정되므로, 후보 개수 자체보다 어떤 O-D-품목 흐름이 반복적으로 구조적 특이성을 보이는지에 더 주목하였다. 실제 상위 후보를 보면 연료(Gasoline, Fuel oils), 곡물(Cereal grains), 비금속 광물제품(Nonmetal min. prods.), 사료(Animal feed) 등 대형 벌크·에너지 계열 품목이 반복적으로 탐지되었다. 이는 단순한 입력 오류라기보다, 규모와 가치·운송거리 조합이 다른 흐름들과 비교해 구조적으로 특이한 핵심 벌크 물류 흐름을 반영한 결과로 해석된다. 따라서 본 분석에서는 Isolation Forest 결과를 단독 판단 기준으로 사용하지 않고, IQR 및 YoY 결과와 함께 비교하여 다변량 관점의 이상치 후보를 보조적으로 식별하는 데 활용하였다.

# 최종결론

IQR, YoY, Isolation Forest를 함께 적용한 결과, FAF5 Truck 데이터에는 통계적으로 크거나 구조적으로 특이하게 보이는 값들이 다수 존재함을 확인하였다. 그러나 boxplot과 로그 변환 분포를 통해 이 데이터가 원래 소수의 대형 벌크 화물 흐름과 다수의 소규모 흐름이 공존하는 heavy-tail 구조를 가진다는 점도 확인하였다. 또한 YoY 분석에서는 곡물, 원목, 화석연료, 자갈, 석탄과 같은 벌크·원자재 품목에서 실제 급변 흐름이 나타났고, 2021년에는 팬데믹 이후 회복과 공급망 재조정의 영향으로 품목·회랑별 변동성이 특히 크게 나타난 것으로 해석할 수 있었다. Isolation Forest 역시 연료·곡물·광물 계열의 대형 흐름을 구조적 특이 후보로 탐지하였다. 따라서 본 분석에서 탐지된 이상치는 곧바로 제거해야 할 오류라기보다, 대형 벌크 회랑, 특정 연도의 급변 흐름, 또는 비정형적 물류 패턴을 보여주는 검토 대상이라고 해석하는 것이 적절하다. 전처리 단계에서는 이를 삭제하기보다 이후 해석과 모델링 전에 추가적으로 확인해야 할 이상치 후보로 유지하였다.

 

# 분포 확인 결과

먼저 전체 Truck 화물량 분포를 확인한 결과, 대부분의 화물 흐름은 작은 규모에 몰려 있었고 일부 흐름만 매우 큰 규모를 보였다. 이는 FAF5 Truck 데이터가 소수의 대형 벌크 화물 흐름과 다수의 소규모 흐름이 함께 존재하는 구조를 가진다는 뜻이다. 따라서 단순히 값이 크다는 이유만으로 이를 오류라고 판단하기는 어렵고, 실제로 중요한 대형 물류 흐름일 가능성도 함께 고려해야 한다고 보았다.

# 연도별 급변 흐름 확인 결과

다음으로 같은 화물 흐름이 전년도에 비해 얼마나 크게 변했는지를 확인했다. 그 결과, 일부 흐름은 단순히 큰 값인 것을 넘어 특정 해에 갑자기 크게 증가하거나 감소하는 패턴을 보였다. 특히 2021년에는 이러한 급변 흐름이 두드러지게 증가했는데, 이는 2020년 팬데믹 충격 이후 산업 활동과 공급망이 재조정되는 과정이 반영된 결과로 해석할 수 있다. 또한 급변 품목은 곡물, 원목, 화석연료, 자갈, 석탄 등 벌크·원자재 중심으로 나타났으며, 이는 특이값이 단순 오류가 아니라 실제 산업 물류의 변동성을 반영하고 있음을 보여준다.

# 구조적으로 특이한 흐름 확인 결과

마지막으로 화물량만이 아니라 가치와 운송거리까지 함께 고려해 다른 흐름과 비교했을 때 구조적으로 특이한 경우를 확인했다. 그 결과 상위 후보는 주로 연료, 곡물, 비금속 광물제품, 사료 등 대형 벌크·에너지 계열 품목에 집중되었다. 즉 단순히 숫자가 튀는 데이터가 잡힌 것이 아니라, 실제로 규모가 크고 물류 구조상 특징이 뚜렷한 핵심 화물 흐름이 드러났다고 볼 수 있다.

# 최종 결론 

세 가지 관점에서 데이터를 확인한 결과, FAF5 Truck 데이터에서 눈에 띄는 큰 값이나 특이한 흐름은 상당 부분 단순 오류라기보다 데이터 자체의 구조적 특성과 실제 산업 물류의 변동성을 반영하는 것으로 판단되었다. 이 데이터는 원래 소수의 대형 벌크 화물 흐름과 다수의 소규모 흐름이 공존하는 구조를 가지고 있으며, 여기에 특정 시기의 수요 변화와 공급망 재조정이 겹치면서 일부 흐름이 더욱 두드러지게 나타난 것으로 보인다. 따라서 본 분석에서는 이러한 값들을 일괄적으로 제거하지 않고, 이후 해석과 예측 모델링 전에 우선적으로 검토해야 할 중요한 후보로 유지하였다.
