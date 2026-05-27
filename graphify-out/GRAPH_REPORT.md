# Graph Report - .  (2026-05-26)

## Corpus Check
- Corpus is ~12,590 words - fits in a single context window. You may not need a graph.

## Summary
- 294 nodes · 309 edges · 51 communities (39 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]

## God Nodes (most connected - your core abstractions)
1. `districts` - 11 edges
2. `DocTREngine` - 9 edges
3. `OCRResult` - 8 edges
4. `FieldExtractor` - 7 edges
5. `booth_name` - 6 edges
6. `booth_no` - 6 edges
7. `ac_name` - 6 edges
8. `ac_no` - 6 edges
9. `ExtractionJob` - 6 edges
10. `process_document()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `FieldExtractor` --uses--> `OCRResult`  [INFERRED]
  backend/app/core/extractor.py → backend/app/worker/ocr/base.py
- `startup_event()` --calls--> `User`  [INFERRED]
  backend/app/api/main.py → backend/app/db/models.py
- `startup_event()` --calls--> `get_password_hash()`  [INFERRED]
  backend/app/api/main.py → backend/app/core/auth.py
- `startup_event()` --calls--> `create_index()`  [INFERRED]
  backend/app/api/main.py → backend/app/core/search.py
- `login_for_access_token()` --calls--> `verify_password()`  [INFERRED]
  backend/app/api/main.py → backend/app/core/auth.py

## Communities (51 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (34): actual, cer, expected, match, actual, cer, expected, match (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (15): startup_event(), Base, log_action(), Logs an action to the audit_logs table., get_password_hash(), create_index(), index_voter(), Creates the voter index. (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (13): BaseModel, extract_fields(), FieldExtractor, FieldConfig, TemplateConfig, TemplateEngine, Config, ExtractionJobBase (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (20): target_ndk_api, assets, ar, cc, ld, android, c_compiler, link_mode_preference (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (13): search(), upload_document(), Searches for voters using fuzzy matching on full_name or voter_id., search_voters(), UserRole, main(), calculate_cer(), evaluate_fields() (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (6): ABC, OCREngine, OCRResult, DocTREngine, engine(), OCRPipeline

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (14): base_url, delay, districts, 502, 504, 505, 507, 508 (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.17
Nodes (11): _PluginRegistrant, register, dart:io, package:geolocator_android/geolocator_android.dart, package:geolocator_apple/geolocator_apple.dart, package:path_provider_android/path_provider_android.dart, package:path_provider_foundation/path_provider_foundation.dart, package:path_provider_linux/path_provider_linux.dart (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, prefer_related_applications, short_name (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.20
Nodes (9): assets, config, build_asset_types, linking_enabled, out_dir_shared, out_file, package_name, package_root (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): configVersion, flutterRoot, flutterVersion, generator, generatorVersion, packages, pubCache

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (3): login_for_access_token(), create_access_token(), verify_password()

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): build_end, build_start, code_assets, data_assets, dependencies

### Community 15 - "Community 15"
Cohesion: 0.40
Nodes (4): main, package:campaign_app/main.dart, package:flutter/material.dart, package:flutter_test/flutter_test.dart

### Community 16 - "Community 16"
Cohesion: 0.50
Nodes (3): assets_for_linking, status, timestamp

### Community 17 - "Community 17"
Cohesion: 0.50
Nodes (3): assets_for_linking, status, timestamp

### Community 18 - "Community 18"
Cohesion: 0.50
Nodes (3): registerPlugins, package:flutter_web_plugins/flutter_web_plugins.dart, package:geolocator_web/geolocator_web.dart

### Community 19 - "Community 19"
Cohesion: 0.50
Nodes (3): configVersion, packages, roots

### Community 20 - "Community 20"
Cohesion: 0.83
Nodes (3): get_token(), main(), upload_file()

## Knowledge Gaps
- **119 isolated node(s):** `match`, `cer`, `expected`, `actual`, `match` (+114 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `process_document()` connect `Community 1` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `startup_event()` connect `Community 1` to `Community 4`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `OCRResult` connect `Community 5` to `Community 2`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `DocTREngine` (e.g. with `OCREngine` and `OCRResult`) actually correct?**
  _`DocTREngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `OCRResult` (e.g. with `FieldExtractor` and `DocTREngine`) actually correct?**
  _`OCRResult` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `FieldExtractor` (e.g. with `OCRResult` and `TemplateConfig`) actually correct?**
  _`FieldExtractor` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `match`, `cer`, `expected` to the rest of the system?**
  _128 weakly-connected nodes found - possible documentation gaps or missing edges._