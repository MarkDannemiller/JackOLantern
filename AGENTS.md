# Joyful Jack

This repo is one Delta Robotics engagement: a internal project. It holds the
engagement record (client, quotes, deliverables, notes, the worklog) at the
root, and the hardware in `protoboard/`, a Protoboard stack project. It is
private and team-only, and it is usually checked out as a submodule of the hub
(`protoboard-projects/projects/internal/2026-10-24-joyful-jack`), whose own guidance and
tools then apply too. Everything here must also make sense when the repo is
cloned on its own.

## Start and end of every session

1. **Start:** read `worklog.md` `## Current State`, then `project.md`. That is
   enough to resume cold. For client work, read `client.md` before you change
   scope or write to the client.
2. **End:** overwrite `## Current State` so it matches reality, and add a
   session entry at the top of `## Sessions`. From the hub root, take a
   checkpoint: `node tools/projects.mjs checkpoint joyful-jack --reason "..."`.

## Where things go

| What | Where | Owned by |
|---|---|---|
| What this is, status, phase, gate, contract fields | `project.md` (frontmatter is read by tools) | engagement |
| Live state and next actions | `worklog.md` | engagement |
| Client contacts, requirements in their words, acceptance criteria, comms log | `client.md` | engagement |
| Quotes (`quote.json`, `working.md`, the PDF) | `quotes/q-<number>/` | engagement |
| Documents sent to the client, as sent | `deliverables/YYYY-MM-DD-<name>/` | engagement |
| Meetings, conversations, contact profiles, client documents | `notes/` | engagement |
| Sources read, open and answered questions | `research/` | engagement |
| Anything received from outside, unedited, with its hash | `inbox/` + `inbox/manifest.json` | engagement |
| Design revisions ordered or delivered, and what came back | `REVISIONS.json` | engagement |
| One-line lessons | `LESSONS.md` | engagement |
| Stack feedback: bugs, friction, gaps and workarounds met in the stack (dogfooding) | `feedback/stack.jsonl` (+ `feedback/evidence/`) | engagement |
| System model, parts, part evidence, checks, CAD and circuit sources, firmware | `protoboard/` | the stack |
| Engineering brief, design decisions, product description | `protoboard/docs/` | the stack |
| Manufacturing package and design releases | `protoboard/` (`protoboard release`) | the stack |

**Hardware work happens in `protoboard/`, under the stack's guidance**
(`protoboard/AGENTS.md`, its skills and `protoboard doctor`). Do not keep a
second copy of anything the stack owns at the root: no root `parts/`, no
root brief or decisions file, no `design/` tree, no exported board copies.
One home per record. If `project.md` says `hardware: none`, there is no
stack project yet; `protoboard init protoboard --name joyful-jack` makes one.

## Dogfooding the stack

When `protoboard doctor` reports a **development build**, or `project.md` says
`dogfood: true`, load the hub's `stack-dogfooding` skill: the user is a stack
maintainer, and every bug, friction, gap and workaround you meet in the stack
goes into `feedback/stack.jsonl` as it happens (`projects.mjs feedback add`;
blockers are said in chat at once). Never patch the stack from here, and never
file Linear issues yourself: a maintainer's triage does that.

## Rules

- **Never cross a human sign-off gate.** An agent records a sign-off a person
  gave (project.md, Sign-offs); it never gives one. It never places an order,
  starts a machine or sends anything to the client.
- **Received files are evidence.** They land in `inbox/` first, get a
  manifest entry (source, date, sha256) and are never edited in place.
- **Deliverables are frozen once sent.** A correction is a new dated folder.
- **Quotes** are built with the hub's `quote` skill; an issued quote is never
  edited in place.
- **Internal stays internal.** `quotes/*/working.md`, `notes/tips/` and the
  pricing and margin notes never reach a deliverable or a quote PDF.
- **Regenerable output is not committed** unless the stack says it is part of
  a release. Large files go in LFS (see `.gitattributes`).
