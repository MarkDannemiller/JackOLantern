---
id: 2026-10-24-joyful-jack
title: Joyful Jack
kind: internal
owner: MarkDannemiller
status: review
phase: research
gate: G-PLAN
stage: G0
hardware: protoboard
current_revision: none
tags: [animatronic, halloween, robot-arm, milwaukee-m18, raspberry-pi]
linear:
dogfood: false
created: 2026-10-24
updated: 2026-10-25
lesson:
# --- contract fields (leave empty for internal and demo projects) ---
client:
contract_status:
contract_type:
budget:
active_quote:
outcome:
posted_date:
applied_date:
start_date:
due_date:
---

<!--
FRONTMATTER CONTRACT. Tooling reads these keys: do not rename or drop one,
leave it empty instead. `projects.mjs new` fills the {{...}} placeholders.

  id                 the folder and repo name exactly: YYYY-MM-DD-slug
  title              what we call this, in plain words
  kind               contract | internal | demo (the hub group it sits in)
  owner              who is responsible for it
  status             scoping | building | review | released | parked | closed
  phase              research | design | manufacturing | testing. Starts at
                     research. Moves only on the phase's exit condition: an
                     agreed brief (and, for a contract, an accepted quote)
                     out of research, G-LAYOUT out of design, parts in hand
                     out of manufacturing, a written carry-forward out of
                     testing. A respin goes back to design, not to research.
  gate               G-PLAN | G-LCSC | G-PARTS | G-SCHEMATIC | G-LAYOUT |
                     G-RELEASE | G-FIRST-ARTICLE | G-BRING-UP. Starts at
                     G-PLAN. An agent never crosses a human sign-off gate.
  stage              product stage gate, G0 through G10. Starts at G0.
  hardware           protoboard (the stack project is in protoboard/) | none
  current_revision   none until a design release is cut, then the release
                     version (see REVISIONS.json)
  tags               lowercase, e.g. [client, wearable, nfc]
  linear             the Linear project or issue, if there is one
  dogfood            true: run this project as a stack dogfood project even on a
                     release build (the stack-dogfooding skill; feedback goes to
                     feedback/stack.jsonl). A development build turns it on anyway.
  created / updated  YYYY-MM-DD. Bump `updated` whenever this file changes.
  lesson             ONE line, filled at close: the thing the next project
                     should know. LESSONS.md holds the rest.

  Contract fields (kind: contract):
  client             company, then the contacts by name (details in client.md)
  contract_status    lead | quoted | won | lost | active | delivered | closed
  contract_type      fixed | hourly | milestone | retainer
  budget             what the client said they can spend, and what was
                     invoiced and paid, with dates
  active_quote       the quote number in force, e.g. Q-2026-ACME-02 (quotes/)
  outcome            won/lost and why, in one line, with the date
  posted_date        when the job was posted or the lead came in
  applied_date       when we applied or sent the first quote
  start_date         when the work started
  due_date           the delivery date we agreed to
-->

# Joyful Jack

<!--
The DURABLE record: what this is and where it stands. The LIVE state - what
is true right now and what to do next - is worklog.md. A fresh session reads
worklog.md first, then this file. Keep this body short.
-->

## What this is

Joyful Jack is a pumpkin-head animatronic character. The head already exists
from 2023 (Raspberry Pi 4B, PCA9685 servo board driving eyes, lids, jaw and neck
pitch, a stepper for neck yaw, LED eyes, a camera with face tracking, voice lines).
Its Python code and history were carried over from github.com/MarkDannemiller/JackOLantern
into `protoboard/software/head/`. This project adds a legless torso on a ballasted
base (a paint bucket of concrete), Milwaukee M18 battery power inside the torso for
long unattended runs, and two motorised arms with character hands. It is designed
at three price points: Beginner (under $500), Midrange (up to $1200) and Maxed
(humanoid hands). Plan: [`research/20261024-plan.md`](./research/20261024-plan.md).

## Where the rest lives

| For | Read |
|---|---|
| Live state and next actions | [`worklog.md`](./worklog.md) |
| The client: contacts, requirements in their words, acceptance criteria, comms log, open questions | [`client.md`](./client.md) |
| Quotes, one folder per quote | [`quotes/`](./quotes/) |
| Documents sent to the client | [`deliverables/`](./deliverables/) |
| Meetings, conversations, contact profiles, client documents | [`notes/`](./notes/) |
| Research: links, questions, papers, concepts | [`research/`](./research/) |
| Everything received from outside, as received | [`inbox/`](./inbox/) |
| The hardware: system model, parts, checks, engineering brief and decisions, design releases | [`protoboard/`](./protoboard/) (a Protoboard stack project) |
| Design revisions: what was ordered, delivered and learned | [`REVISIONS.json`](./REVISIONS.json) |
| What this project taught | [`LESSONS.md`](./LESSONS.md) |
| What the Protoboard stack got wrong or made hard here (dogfooding) | [`feedback/stack.jsonl`](./feedback/) |

## Sign-offs

<!-- Every human sign-off gate this project has crossed, newest last. An agent
can record a sign-off a person gave; it never gives one. Typical entries: the
brief agreed (research exit), the quote accepted, G-LAYOUT, G-RELEASE on an
exact release, delivery accepted by the client. -->

| Gate | What was signed | By | Date |
|---|---|---|---|
| | | | |
