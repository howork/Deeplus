# Deeplus 0.1.2-baseline.r51f3 Design Gallery

This curated gallery teaches both current Deeplus responsibilities and removed-surface boundaries. Product parser/checker execution is NOT_RUN.

## G-R51f-001 — Map String key uses explicit indexing

- outcome: `accept`
- source: `EX-R51f-001`
- evidence: `design-static; product NOT_RUN`

```deeplus
let options = #map{ "timeout": 30 }
let timeout = options["timeout"]
```

## G-R51f-002 — Map dot-key projection is not member lookup

- outcome: `reject`
- source: `EX-R51f-002`
- evidence: `design-static; product NOT_RUN`

```deeplus
let options = #map{ "timeout": 30 }
let timeout = options.timeout
```

## G-R51f-003 — Explicit assignment replaces increment

- outcome: `accept`
- source: `EX-R51f-003`
- evidence: `design-static; product NOT_RUN`

```deeplus
var value = 0
value = value + 1
```

## G-R51f-004 — Postfix increment is not current

- outcome: `reject`
- source: `EX-R51f-004`
- evidence: `design-static; product NOT_RUN`

```deeplus
var value = 0
value++
```

## G-R51f-005 — Ordinary recursive function

- outcome: `accept`
- source: `EX-R51f-005`
- evidence: `design-static; product NOT_RUN`

```deeplus
public def sumTo(n: Int) -> Int = {
    if n <= 0 { return 0 }
    return n + sumTo(n - 1)
}
```

## G-R51f-006 — Tail-recursion callable kind is not current

- outcome: `reject`
- source: `EX-R51f-006`
- evidence: `design-static; product NOT_RUN`

```deeplus
public def#tailrec sumTo(n: Int) -> Int = {
    return if n <= 0 then 0 else n + sumTo(n - 1)
}
```

## G-R51f-007 — Raw String can carry pattern text

- outcome: `accept`
- source: `EX-R51f-007`
- evidence: `design-static; product NOT_RUN`

```deeplus
let patternText = raw"[A-Z]+"
```

## G-R51f-008 — Regex literal prefix is not current

- outcome: `reject`
- source: `EX-R51f-008`
- evidence: `design-static; product NOT_RUN`

```deeplus
let pattern = #regex"[A-Z]+"
```

## G-R51f-009 — Explicit expected List union

- outcome: `accept`
- source: `EX-R51f-009`
- evidence: `design-static; product NOT_RUN`

```deeplus
let values: List<Int | String> = [1, "two"]
```

## G-R51f-010 — Automatic heterogeneous List union is absent

- outcome: `reject`
- source: `EX-R51f-010`
- evidence: `design-static; product NOT_RUN`

```deeplus
let values = [1, "two"]
```

## G-R51f3-011 — Named-rest and named unfold remain different channels

- outcome: `accept`
- source: `EX-R51a1-NEW-003`
- evidence: `design-static; product NOT_RUN`

```deeplus
def command(name: String, args...: String, options***: Record) -> Unit = {
    dispatch(name, *args, **options)
}
```

## G-R51f3-012 — Sealed hierarchy is module-closed

- outcome: `accept`
- source: `EX-R49B-SEALED-001`
- evidence: `design-static; product NOT_RUN`

```deeplus
module expr
public sealed class Expr {
}
public final class Literal : Expr {
}
public open class Binary : Expr {
}
```

## G-R51f3-013 — Conformance creates explicit witness evidence

- outcome: `accept`
- source: `EX-R48C-083`
- evidence: `design-static; product NOT_RUN`

```deeplus
public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

public conformance UserId conforms Display {
    +def display+() -> String
        throws Never
        effects {}
    = {
        return self.raw
    }
}
```

## G-R51f3-014 — Borrow Facet preserves object identity

- outcome: `accept`
- source: `EX-R51a1-FACET-P-001`
- evidence: `design-static; product NOT_RUN`

```deeplus
let printable: Facet<borrow any Printable> = facet[borrow user as Printable]
let text = printable ~ print()
```

## G-R51f3-015 — Typed labeled materialization preserves construction authority

- outcome: `accept`
- source: `EX-R51a1-015`
- evidence: `design-static; product NOT_RUN`

```deeplus
public schema Request {
    url: String
    timeout: Int = 30
}
let request = Request${
    url: endpoint
}
```

## G-R51f3-016 — Pure call-by-need binding

- outcome: `accept`
- source: `EX-R51a1-LAZY-P-001`
- evidence: `design-static; product NOT_RUN`

```deeplus
let#lazy model: Result<Model, error ParseError> = parseResult(text)
inspect(model)
inspect(model)
```

## G-R51f3-017 — Async task and actor minimum core

- outcome: `accept`
- source: `EX-R48E1-030`
- evidence: `design-static; product NOT_RUN`

```deeplus
public protocol Work {
    request compute(input: Job) -> Result
}
public actor Worker {
    +request compute(input: Job) -> Result = {
        return process(input)
    }
}
public def#async run(job: Job) -> Result
    throws Never
    effects {task}
= {
    return await task {
        Worker!() ~ compute(job)
    }
}
```

## G-R51f3-018 — Bitfield checked raw conversion

- outcome: `accept`
- source: `EX-R51a1-BITFIELD-P-003`
- evidence: `design-static; product NOT_RUN`

```deeplus
let raw: UInt32 = header.raw
let ::ok(decoded) = PacketHeader::fromRaw(raw)
else ::err(error) => throw error
```
