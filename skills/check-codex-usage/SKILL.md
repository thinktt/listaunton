---
name: check-codex-usage
description: Read current Codex account usage, report remaining allowance and reset times, and enforce a user-specified usage threshold during an active task. Use for Codex usage checks or a requested usage monitor, not general API billing estimates.
---

# Check Codex usage

Use the account's live usage-limit tool, not conversation token estimates.
Discover `mcp__codex_app__get_usage_limits` (or its available equivalent) and
call it with `{}`. This read is shared-account information, not task-specific
token consumption.

## Interpret the result

- Prefer `rateLimitsByLimitId` over the legacy `rateLimits` field. Select the
  bucket applicable to the active model/task. If several applicable buckets
  constrain it, report the restrictive one without mixing unrelated models.
- Identify a weekly window by `windowDurationMins` (normally 10080). It may
  be `primary` or `secondary`; do not assume `secondary` means weekly.
- `usedPercent` is consumed allowance. Compute remaining percentage as
  `max(0, min(100, 100 - usedPercent))`. Thus 1% used means 99% remaining;
  97% used means 3% remaining.
- Missing/null values mean unavailable, not zero. If the requested window
  cannot be identified, say so rather than using a shorter window as a proxy.
- `resetsAt` is a Unix timestamp in seconds. Show a clearly labeled timezone
  when reporting it. Include the check time when a stored reading is used.
- Credits, free resets, context size, and `get_goal` token counts are separate
  from weekly remaining allowance. Do not consume credits or resets merely
  to satisfy a usage-report or monitoring request.

Report only what is needed: window/bucket, used and remaining percentages,
and reset time if useful. Do not dump the account ID, credit balance, reset
credit IDs, or the whole tool response into a project log.

## User-specified threshold

A reporting request is read-only. Enforce a stop/pause only when the owner
or the active mission has supplied that rule. Do not impose a universal
threshold on unrelated tasks.

For a rule such as "pause at 3% remaining or lower", compare remaining
percentage with `<= 3`, not used percentage. When it triggers, start no new
substantial work, save a concise checkpoint, and use `update_goal` with
`status: paused` for the active goal when the owner's conditional pause
authorization applies. Report the returned status, then stop. Platform
budget-limit rules take precedence. Do not mark an unfinished goal complete.

If the reading fails, retry once. If still unknown, disclose the failure and
follow the mission's missing-data rule; never invent a percentage or claim a
threshold crossing. Do not use `blocked` without meeting its tool conditions.

## Delegated monitoring

When the owner explicitly requests a particular subagent, delegate the
usage checks to it instead of repeatedly waking the main model. Reuse an
existing suitable worker. For a requested Luna guard, the supported settings
are `model: gpt-6-luna`, `reasoning_effort: low`, `fork_turns: none`; provide
this skill and the applicable threshold, not the full project history.
Do not spawn workers merely because this skill was loaded.

Start with one live read to verify that the subagent can access the tool.
During an authorized active mission, follow the owner's requested cadence
(every 5 minutes for the listaunton queen mission),
using interruptible waits of at most 60 seconds rather than a busy loop,
and answer on-demand checks at iteration boundaries. It should send only
threshold alerts, failures, and requested readings to its parent. The parent
performs checkpointing and goal-state transitions, so the worker cannot
accidentally pause an unrelated child goal. No modeling or file edits belong
in the guard's assignment.

Stop the worker when the mission stops. An idle worker does not schedule
future checks by itself; a running session worker is not an independent
service guaranteed to survive turns or app restarts. Confirm its status and
restart or request a fresh check when needed. Keep any replaced main-chat
heartbeat paused. If delegation fails, disclose that and use a direct live
check rather than silently abandoning an active usage constraint.

## Optional scheduled monitoring

A skill does not execute continuously on its own. When scheduled monitoring
is requested and a subagent has not been selected instead, discover
`automation_update` and use a heartbeat attached to the current chat rather
than a new cron task. Inspect matching saved automations first and reuse one.
A 15-minute interval is a reasonable starting point unless the owner
specifies a different cadence. Do not claim the heartbeat itself runs on
Luna merely because its prompt names that model; verify supported settings.

Make the monitor conditional on the relevant mission being active, and stop
it when that mission completes or pauses. If monitoring is being prepared
before the mission starts, create it paused and state that clearly. Configure
notification behavior through the automation tool, respecting the owner's
preference; routine unchanged readings should not produce status chatter.
Escalate a threshold crossing or monitoring failure. A reset alone must not
resume a user-paused goal.

Keep the prompt small: read mission/goal status, fetch the applicable weekly
window, calculate remaining percentage, and enforce the explicit threshold.
Do not launch modeling, renders, new agents, or unrelated work from a usage
heartbeat. Store only a small normalized reading/checkpoint if needed.

Heartbeat timing is not a guaranteed in-turn interruption, and other chats
consume the same allowance. Keep a direct check at task/iteration boundaries
and before expensive work. Only claim the monitor is active after the tool
confirms it; if scheduling is unavailable, use direct checks and say so.
