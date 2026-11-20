# Evidence — Day 30

| File | What |
|---|---|
| `A_collision.log` | Leading slashes: `/cmd_vel` and `/odom` at 3 pub / 3 sub, 213 cmds/robot, 0 reach target (`14.840 m` travel) |
| `B_uncoordinated.log` | Relative topics + `rN/base_link`: isolated wheels, all 3 pile onto `(2.50, 3.00)` (`0.033 m` apart, `7.091 m` travel) |
| `C_coordinated.log` | `fleet_coordinator` assigns `r1` (`1.500 m`); `r1` drives `1.464 m`, `r2` and `r3` hold at `0.000 m` (`0` cmds) |
| `linkedin/01-hero.jpg` | Collision vs Namespaces + Coordinator split diagram |
| `linkedin/DRAFT.md` | Finale LinkedIn post draft with measured results |
