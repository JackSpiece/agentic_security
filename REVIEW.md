# Review instructions

## Scope of this review

This pull request presents the entire project against an empty base, so every
file appears as added. Treat it as a full-codebase audit rather than a change
review: the "new" code is existing, already-shipped code.

Because nothing here is a genuine change, ignore the usual bias toward
newly-introduced defects and report what is actually wrong in the code as it
stands.

## What to report

Prioritise, in order:

1. Correctness bugs: wrong results, unreachable code paths, off-by-one errors,
   incorrect state handling, silent failures.
2. Bugs where one module violates an assumption made by another. These matter
   most here, since the whole codebase is visible in a single diff.
3. Security issues: injection, unsafe deserialisation, credential handling,
   missing authorisation on network-exposed routes.
4. Error handling that masks failures, including bare excepts and swallowed
   exceptions.

Do not cap the number of findings. Report every issue you can verify, grouped
by severity. Style and formatting preferences are out of scope; the project
already runs flake8 and pre-commit for those.

## Verification bar

Cite `file:line` for any claim about behaviour. Where a conclusion depends on
code in another module, name that module and confirm you read it rather than
inferring from naming.
