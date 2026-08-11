# Deeplus Strong Eq/Ord Coherence Closure R1

Status: `LOCAL_DESIGN_CANDIDATE_NOT_PUBLISHED`

This decision closes the design ambiguity inside `TCC-P1-003`; it does not
close that feature P1 or claim product implementation.

## Decision

User-defined strong comparison is homogeneous. After alias and type-argument
normalization, a user `Eq<Rhs>` or `Ord<Rhs>` conformance is admitted only when
`Rhs` is the exact `Self` type. This makes reflexivity, symmetry, transitivity,
antisymmetry and totality laws belong to one nominal domain and keeps the
left-owner ground-key rule coherent.

The machine disposition is `NORMALIZED_RHS_MUST_EQUAL_SELF`.

A heterogeneous strong comparison is possible only through one compiler- or
Prelude-sealed bilateral family. The family owns an unordered normalized type
pair, both oriented witnesses, one normalization domain, Eq symmetry, Ord sign
reversal and the requirement that `compare == 0` agrees with the same Eq
relation in both orientations. Current Deeplus registers no such family. A
single user-owned `Eq<B>` or a pair of unrelated `Eq` rows cannot create one.

The machine disposition is `SEALED_BILATERAL_FAMILY_ONLY`.

Intrinsic-reserved pairs remain outside conformance lookup. Float and Complex
partial equality does not manufacture strong Eq, and Complex has no Ord.
Rational and eligible ordered Enum values retain their homogeneous strong
Eq/Ord profiles. This change adds no glyph, conversion, fallback, runtime
lookup, witness priority or product-support claim.

Semantic P0 remains zero, the exact 22 feature P1 remain OPEN, and product
lanes remain `15_OF_15_NOT_RUN`.

## Failure boundary

`STRONG_COMPARISON_RHS_NOT_ADMITTED` rejects a user or derived strong
comparison whose normalized right type is not Self or whose domain is not
eligible for strong comparison. `STRONG_COMPARISON_BILATERAL_FAMILY_INVALID`
rejects a purported sealed heterogeneous family lacking its shared family
identity, reverse witness, normalization domain or bilateral laws. Both occur
before ordinary conformance locality, overlap and witness selection.
