"""Action implementations grouped by domain.

Layout
------
* ``state/``     — config, paths, checkpoints, researcher interaction.
* ``data/``      — data ops, profiling, intake autofill.
* ``exec/``      — script execution (py/r/julia/bash), notebooks/Rmd,
                   background tasks, environment snapshots.
* ``search/``    — literature + web search providers, paper downloads.
* ``research/``  — reasoning + iterative planning + tool/method research.
* ``audit/``     — synthesis / power / assumption / figure / citation audits.
* ``synthesis/`` — paper, poster, dashboard, verified-citations.
* ``memory/``    — append-only logs, decisions, hypotheses.
* ``protocol.py``— the protocol loader (sits at top level — fundamental).
"""
