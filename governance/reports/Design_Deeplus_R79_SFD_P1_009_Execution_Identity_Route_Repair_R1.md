# R79 SFD-P1-009 execution identity route repair

## Verdict

`LOCAL_EXECUTABLE_ROUTE_REPAIRED_SFD_P1_OPEN`

The former route required repository `HEAD` to equal
`f509fce5df6c16b77d3accdccde4c640b093da0a`. That commit is valid immutable
design provenance, but it contains neither the SFD route sources nor the frozen
fixture bundle. The requirement therefore made an authorized target-bound run
structurally impossible.

R79 separates the two identities:

- `historical_provenance_commit` remains the immutable `f509...` commit;
- `baseline_commit` in an execution receipt is the full commit of the observed
  clean checkout that owns every implementation and fixture input;
- approval of that observed target is external and post-commit, so no source
  file must predict the SHA of the commit that contains itself.

## Execution gate

Before loading fixtures or publishing output, the bounded CLI now requires:

1. a full lowercase 40-character commit identity;
2. no staged or tracked worktree delta;
3. every listed implementation and fixture path to exist in that commit.

The implementation, current pointer, compiler binary, toolchain, target triple,
environment and fixture digests remain execution-bound. Untracked build/output
files do not change the tracked execution target.

## Governance fence

This repair removes only the impossible-route blocker. `SFD-P1-009` remains
`OPEN`; its execution receipt count remains zero until a separately authorized
target run is recorded and reviewed. The exact feature P1 set remains 22 OPEN,
semantic P0 remains zero, all 15 product lanes remain `NOT_RUN`, and this local
candidate performs no GitHub publication or production implementation.
