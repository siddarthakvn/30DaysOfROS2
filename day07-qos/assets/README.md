# Assets — Day 07

Terminal evidence captured during local smoke runs:

| File | What it shows |
|---|---|
| `A_compatible.log` | Matched RELIABLE flow |
| `A_topic_info.txt` | Compatible QoS endpoints |
| `B1_mismatch.log` | BEST_EFFORT pub + RELIABLE sub → zero receives |
| `B1_topic_info.txt` | Both endpoints visible with incompatible reliability |
| `B2_fixed.log` | Matching BEST_EFFORT restores flow |
| `C_durability.log` | Late-join / durability cases |
| `C_topic_info.txt` | Durability settings from `--verbose` |

LinkedIn draft: [`linkedin/DRAFT.md`](linkedin/DRAFT.md)
