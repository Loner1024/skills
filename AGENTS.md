# Working in this repository

This repository is the public home of the skills (`skills/<name>/`). It is content only: no package
manager, no build step, no test runner. Verify a figure with
`python3 skills/tech-diagrams/scripts/self_check.py <source> --png <render>`.

## Publishing a skill change

Amp serves personal skills from its own hosted Git repository, so a change here is not live in Amp
until it is copied there. After pushing a change under `skills/` to `main`, run:

```bash
scripts/sync-to-amp-skills.sh
```

It copies every skill (text files only - Amp serves no binaries), commits, and pushes to the
maintainer's personal skills repository. It adds and updates; it never deletes, so a skill created
in Amp by hand survives a sync. The same script is what the daily schedule on the maintainer's
thread runs, so this step is a convenience for the common case, not the only path.

Run `scripts/sync-to-amp-skills.sh --dry-run` to see what would change without committing.
