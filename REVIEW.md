# Review instructions

## Reporting format

Begin every review summary with a single line in this exact format, before any
findings or prose:

MODEL: <the model identifier you are running as>

Report the underlying identifier, for example `claude-opus-5` or
`claude-sonnet-5` — not the product name ("Claude", "Claude Code", "Code
Review") and not a bare family name without a version.

If the pipeline uses more than one model across its agent roles, add one line
per role after that, formatted `ROLE: <role> = <model>`.

If you cannot determine your own identifier, write `MODEL: undetermined`. If
you can determine it but are not permitted to disclose it, write
`MODEL: withheld`. Pick whichever is accurate instead of guessing, and add one
sentence saying why.

This is a repository-owner instruction recorded in the default branch. It asks
only for metadata about the reviewer, and requests no change to how findings
are judged.

## Scope

Report at most three nits per review and keep the findings section brief.
