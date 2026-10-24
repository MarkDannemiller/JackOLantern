# inbox/

Everything that arrives from outside, as received, before it is filed.

<!--
WHY THIS FOLDER EXISTS

The moment a received file is edited in place, you lose the ability to answer
"what did they actually send us?" That question gets asked during every
disagreement about scope, every fab issue, and every handoff. This folder is
the answer.

THE RULES

1. Anything received from outside lands here FIRST. A CAD file, a spec, a
   mechanical drawing, a BOM, a photo of a bench setup, a PDF of a
   requirements doc.
2. It is recorded in manifest.json BEFORE it is used: source, date, sha256.
3. It is NEVER edited in place. Not to fix a unit, not to rename a layer, not
   to repair a mesh. If it needs changing, derive a new file where it is
   used (in protoboard/, or notes/client-files/ for a document) and record
   what it came from.
4. Once it is filed, the copy here STAYS. The manifest entry plus the
   original is the evidence trail. Deleting it to save space is a false
   economy - most of these are kilobytes, and the ones that are not belong in
   LFS anyway.

Received CAD in particular: it lives here permanently. Geometry WE author
lives in the stack project (protoboard/src/...), which can reference this
file but never edits it.
-->

## manifest.json

Every file here has an entry. The manifest is append-only.

Entry shape:

| Field | What it holds |
|---|---|
| `file` | The filename as stored in this folder. |
| `source` | Where it came from. A person, a company, a URL, a vendor portal. Be specific enough to ask a follow-up question. |
| `received` | ISO date, `YYYY-MM-DD`. |
| `sha256` | The hash of the file exactly as received. This is the whole point. |
| `bytes` | File size. |
| `what` | One line: what this is and what it was sent for. |
| `filed_to` | Where the derived or usable version ended up, if anywhere. Empty if it is reference only. |

Example:

```json
{
  "file": "customer-enclosure-rev3.step",
  "source": "Jordan at Acme, emailed 2026-09-18",
  "received": "2026-09-18",
  "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "bytes": 4183920,
  "what": "Their existing enclosure. Board has to fit the boss pattern on the floor.",
  "filed_to": "protoboard/src/enclosure/enclosure.uhd.ts"
}
```

Compute the hash before anything else touches the file:

```
sha256sum inbox/customer-enclosure-rev3.step
```

## Naming

Keep the sender's filename if it is already ASCII, lowercase-safe, and
reasonable - a filename is itself evidence. If it is not, rename it and
record the original in the `what` field. Never use `< > : " / \ | ? *`, and
watch the 28-character discipline that applies to the project slug, since
these paths nest deep.
