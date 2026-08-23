# Deterministic Core Test Matrix

## Evidence boundary

This is an AI-assisted design draft. The `Review status` column distinguishes
scenarios the user has reasoned through from candidates that still need user
review. The matrix is not evidence that the scheduling engine has been
implemented or independently mastered.

The current code only implements two small calculation helpers with nine
passing `unittest` checks. None of the scheduling scenarios below is automated
yet.

## Priority rule v0.1 - reviewed 2026-08-23

1. Reject invalid input before scheduling.
2. Exclude tasks with no remaining work.
3. Sort tasks by earlier deadline.
4. For equal deadlines, sort by higher importance.
5. If both are equal, sort by `task_id` ascending as the stable tie-breaker.
6. Allocate work only inside valid availability windows and respect minimum and
   maximum session lengths.
7. Report work that cannot be scheduled instead of pretending it is complete.

Remaining effort affects feasibility, splitting, and capacity warnings. It does
not change the priority order in this first candidate rule.

## Scenario matrix

| ID | Scenario | Key input | Expected result | Rule or invariant checked | Review status |
|---|---|---|---|---|---|
| S01 | One task fits exactly | T1 has 60 minutes remaining, deadline 12:00, availability 10:00-11:00, minimum 30, maximum 60 | Schedule T1 from 10:00-11:00; zero minutes unscheduled | Block stays inside availability and before deadline; allocation does not exceed remaining work | User confirmed |
| S02 | Capacity is insufficient after partial completion | T1 estimate 120, completed 30, deadline 12:00, availability 10:00-11:00 | Schedule 60 minutes; report 30 minutes unscheduled with `INSUFFICIENT_CAPACITY` | Remaining work is 90 minutes; the system reports rather than hides the shortfall | User confirmed |
| S03 | Equal deadline, different importance | T1 and T2 each need 60 minutes and have deadline 15:00; importance is 5 for T1 and 3 for T2; only 10:00-11:00 is available | Schedule T1; report all 60 minutes of T2 as unscheduled | Higher importance breaks an equal-deadline tie | User confirmed |
| S04 | Full priority tie | T1 and T2 have equal deadline, importance, and remaining work; only one 60-minute window exists | Schedule T1 first because `T1` sorts before `T2` | Stable `task_id` tie-breaker makes repeated output deterministic | User confirmed |
| S05 | Window is shorter than the minimum session | T1 needs 60 minutes, minimum session is 30, availability is 10:00-10:20 | Create no block; report all 60 minutes with `SESSION_TOO_SHORT` | The scheduler does not create an ineffective undersized block | User confirmed |
| S06 | No window exists before the deadline | T1 needs 60 minutes, deadline 11:00, only availability is 11:30-12:30 | Create no block; report all 60 minutes with `NO_WINDOW_BEFORE_DEADLINE` | Work is never silently placed after its deadline | User confirmed |
| S07 | Earlier deadline versus higher importance | T1 needs 60 minutes, deadline 11:00, importance 2; T2 needs 60 minutes, deadline 15:00, importance 5; only 10:00-11:00 is available | Schedule T1; report T2 as unscheduled | Earlier deadline takes priority over higher importance | User confirmed |
| S08 | Task is already complete | T1 estimate and completed minutes are both 60 | Create no block and report zero remaining and zero unscheduled minutes for T1 | Completed work is excluded rather than scheduled again | Confirmed in guided code |
| S09 | One task is split across two windows | T1 needs 90 minutes, minimum session 30, maximum 60; availability is 10:00-10:45 and 14:00-14:45 before the deadline | Create two 45-minute blocks; zero minutes unscheduled | Splitting is allowed and both blocks respect session limits | User confirmed |
| S10 | Maximum session length is respected | T1 needs 120 minutes, minimum session 30, maximum 45; availability is 10:00-12:30 | Create blocks of 45, 45, and 30 minutes; leave 30 minutes of availability unused | Every block stays between the minimum and maximum session length | User modified and confirmed |
| S11 | Multiple tasks never overlap | T1 and T2 each need 60 minutes; T1 deadline 12:00, T2 deadline 14:00; availability is 10:00-12:00 | Schedule T1 from 10:00-11:00 and T2 from 11:00-12:00 | Scheduled blocks do not overlap and follow deadline order | User confirmed |
| S12 | Availability window is malformed | One availability window starts at 11:00 and ends at 10:00 | Reject the planning request with a validation error | Invalid time boundaries are not silently corrected | User confirmed |
| S13 | Completed work exceeds the estimate | T1 estimate 120 and completed 130 | Reject T1 with `ValueError` before scheduling | Completed work cannot exceed estimated work | Confirmed in guided code |
| S14 | A missed window triggers replanning | Original plan used 10:00-11:00 for T1 and 11:00-12:00 for T2; the first window is missed, current time becomes 11:00, and availability is now 11:00-13:00; T1 deadline 12:00 and T2 deadline 14:00 | Recalculate from 11:00; schedule T1 from 11:00-12:00 and T2 from 12:00-13:00 | Replanning uses current state and never retains a block in the past | User confirmed |
| S15 | Repeated input is deterministic | Run the same validated request twice with the same rule version | Both results have identical block order, times, reason codes, and summary values | Same input and rule version produce the same output | User confirmed |

## Gate A use

All 15 rows were reviewed on 2026-08-23. The user independently modified S10
and explained the deadline, importance, stable tie-breaker, session-length, and
replanning decisions used in the matrix.

During implementation, convert each accepted row into one or more automated
tests. Gate A still requires those tests to pass against the deterministic core
and the user to explain the implemented data flow without reading the code.
