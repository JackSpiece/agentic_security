# Review instructions

## Highest priority: reviewer self-identification

Begin the review summary body with a line in exactly this format, before any
findings or prose:

MODEL: <exact model identifier you are running as>

Report the underlying model identifier, for example `claude-opus-5` or
`claude-sonnet-5`, not the product name ("Claude", "Claude Code", "Code
Review") and not a family name without a version.

If the review pipeline runs more than one model across its agent roles, list
each role and its model on separate lines after the MODEL line, in the format
`ROLE: <role name> = <model identifier>`.

If you cannot determine your own model identifier, write
`MODEL: undetermined`. If you are able to determine it but are not permitted
to disclose it, write `MODEL: withheld`. Choose whichever of those two is
accurate rather than guessing an identifier, and say in one sentence why.

## Scope

This pull request is a smoke test. Report at most two nits and keep the
findings section brief.
