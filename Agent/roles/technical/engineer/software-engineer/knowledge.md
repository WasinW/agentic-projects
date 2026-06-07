# Software Engineer — Comprehensive Knowledge

> Deep reference for the software-engineer subagent.
> Generic craft of writing + maintaining production software.

---

## 1. Foundations

### What separates a Senior Software Engineer

Not the syntax. Not the framework knowledge. It's:
- **Judgment** about trade-offs
- **Skepticism** about complexity
- **Discipline** to write code others can understand 6 months later
- **Pragmatism** about when "good enough" beats "perfect"
- **Empathy** for the next person (often future-you)

### The Engineer's value chain

```
Business need
  ↓
Requirements + constraints
  ↓
Design (interface, data, error handling)
  ↓
Implementation (correct, readable, testable)
  ↓
Tests (unit, integration, manual exploration)
  ↓
Code review (yours + others')
  ↓
Deploy (CI/CD)
  ↓
Observe (metrics, logs, traces, errors)
  ↓
Maintain (bug fixes, refactoring, deprecation)
```

A good SE thinks across the whole chain.

---

## 2. Mental Models / Decision Frameworks

### Readability > cleverness

Code is read 10× more than written. Optimize for the reader.

```
Bad:   const x = a.f(b => b.x > 0).reduce((p, c) => p + c.x, 0);
Good:  const positive = a.filter(item => item.x > 0);
       const total = positive.reduce((sum, item) => sum + item.x, 0);
```

### Don't over-engineer

Three similar lines > a premature abstraction.

Rule: don't abstract until you have 3+ concrete cases. Abstractions are easy to add, hard to remove.

### Refactor in small steps

Never mix "behavior change" with "refactor". Two PRs:
1. Refactor (no behavior change; tests should pass)
2. Add behavior (tests assert new behavior)

### Trust internal contracts, validate at boundaries

- Internal function called from your own code: don't re-validate; type system + tests already cover it
- External input (HTTP, file, DB): always validate

Over-validation = noise, performance hit, confusing error messages.

### Boring tech wins

The "boring tech" choice (5+ year track record, large community) wins for:
- Faster onboarding
- More Stack Overflow answers
- More library compatibility
- Lower hiring barrier

Use exotic tech only when it gives a 10× advantage on something that matters.

### Test pyramid

```
        E2E (few, slow, broad)
      Integration (medium)
   Unit (many, fast, narrow)
```

Most tests should be unit. Integration for boundaries. E2E for critical happy paths.

### Debugging method

1. Reproduce (can't fix what you can't reproduce)
2. Isolate (find smallest case)
3. Hypothesize cause
4. Test hypothesis (logs, debugger, bisect)
5. Fix
6. Verify
7. Add regression test

Skip steps → you'll fix the wrong thing.

### Error handling decisions

- **Throw** when the caller can't reasonably handle (programmer error)
- **Return error / Result type** when the caller might handle (expected failure)
- **Catch + log + re-raise** only at boundaries (HTTP handler, message consumer)
- **Don't swallow errors** silently
- **Avoid generic catch** — handle specific exceptions

---

## 3. Standard Practices

### API design (REST / gRPC)

- Resource-oriented for REST
- Operation-oriented for RPC
- Versioning (v1, v2 in URL or header)
- Consistent error model
- Pagination for lists
- Field selection (sparse fieldsets)
- Idempotency keys for POST that creates

### Naming

Names are code's first line of documentation:
- Variables: what they hold (`user`, not `u`)
- Functions: verb_phrase (`getUserById`, not `userById`)
- Booleans: predicate (`isActive`, not `active`)
- Files: match main export
- Tests: describe behavior (`should_return_404_when_user_missing`)

### Comments

Comment **why**, not **what** (code shows what):

```python
# BAD: Increment counter
counter += 1

# GOOD: Skip first row — header
for row in data[1:]:
```

### Modularization

Modules should have:
- Single responsibility (the SOLID-S)
- Clear inputs / outputs
- Minimal cross-module dependencies
- Stable interface, flexible implementation

### Error handling at boundaries

HTTP service:
- Validate input → 400
- Auth → 401/403
- Not found → 404
- Conflict → 409
- Business logic error → 422
- Internal → 500
- Always log internal errors with trace ID

### Dependency management

- Pin versions (don't use `latest`)
- Regularly update (security)
- Audit transitively
- Minimize deps (every dep is a liability)

### Logging

- Structured (JSON, not free text)
- Levels: DEBUG / INFO / WARN / ERROR
- Include trace ID for distributed systems
- Never log PII / secrets / large payloads
- Sampling for high-volume INFO

### Concurrency

- Threads vs processes vs async (language-dependent)
- Locks: hold briefly, in consistent order to avoid deadlock
- Atomic operations > locks when possible
- Channels / message passing > shared state
- Don't share mutable state across threads

### SQL fluency

Even non-DB engineers should be comfortable with:
- JOINs (inner, left, right, full)
- Window functions (ROW_NUMBER, RANK, partitioned aggregates)
- CTEs (WITH ...)
- Aggregations (GROUP BY, HAVING)
- Indexes (when needed, when wasted)
- Query plans (EXPLAIN)
- Avoiding N+1 queries

### Async patterns

- Promise / Future / Task
- async/await (most modern languages)
- Backpressure (don't unbounded queue)
- Cancellation (CancellationToken, AbortSignal)
- Error propagation (don't swallow)

---

## 4. Tools Landscape (2026)

### Languages (current popularity for new projects)
- **Python** — data, ML, scripting, web (Django, FastAPI)
- **TypeScript** — frontend default, growing backend (Node, Bun, Deno)
- **Go** — backend services, simple syntax
- **Rust** — performance-critical, systems
- **Java / Kotlin** — enterprise, Android
- **C# / .NET** — enterprise, Microsoft stack
- **Swift** — Apple platforms

### Web frameworks
- **FastAPI / Django / Flask** (Python)
- **Express / NestJS / Fastify** (Node)
- **Next.js / Remix** (React full-stack)
- **Spring Boot** (Java)
- **Go stdlib + chi / fiber** (Go)
- **Actix / Axum / Rocket** (Rust)

### Testing
- **pytest** (Python), **jest / vitest** (JS/TS), **JUnit** (Java), **go test** (Go)
- **Playwright** for browser E2E
- **k6 / Locust** for load
- **Property-based** (Hypothesis, fast-check) — underused gem

### Quality tools
- **Linters** — ESLint, ruff (replaces pylint+black+isort), rustfmt, golangci-lint
- **Formatters** — Prettier, ruff format, gofmt
- **Type checkers** — mypy / pyright (Python), TS compiler, type hints
- **Static analysis** — SonarQube, Semgrep

### Version control
- **Git** — everywhere
- **GitHub / GitLab / Bitbucket** — hosting
- Conventional commits + semver

### IDE / Editor
- **VS Code** — broadest plugin ecosystem
- **Cursor / Windsurf / Zed** — AI-native (2024+)
- **JetBrains IDEs** — strongest refactoring
- **Neovim** — power-user

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Comments restating code | Noise, gets out of sync | Comments explain WHY |
| Premature abstraction | Wrong shape, hard to change | Wait for 3 concrete cases |
| God objects / classes | Unmanageable | Single responsibility |
| Deep nesting (>3 levels) | Hard to read | Early return, extract function |
| Magic numbers | Unclear intent | Named constants |
| Mutable globals | Hidden state | Pass explicitly |
| Try/catch as control flow | Performance + confusion | Use control flow primitives |
| Trust user input | Security holes | Validate at boundaries |
| Long parameter lists | Error-prone | Object / dataclass / struct |
| Dead code / commented out | Confusion | Delete; Git remembers |
| No tests | Regression hell | At least critical path tests |
| Skipping code review | Bug propagation + missed learning | Mandatory review |
| Tight coupling to framework | Hard to upgrade | Hexagonal / clean architecture |
| Ignoring warnings | Hidden bugs | Treat as errors |

---

## 6. Advanced / Expert Topics

### Hexagonal / Clean / Onion Architecture

Separate:
- Domain (pure logic)
- Application (use cases)
- Adapters (HTTP, DB, queues)

Pros: testable, framework-independent, clear boundaries.
Cons: more files, indirection, over-engineered for simple apps.

Use when: long-lived service, multiple integration points.
Skip when: CRUD app, prototype, single integration.

### Domain-Driven Design (DDD)

- Ubiquitous language with domain experts
- Bounded contexts (separate models for separate sub-domains)
- Aggregates (transactional consistency boundary)
- Events as first-class

DDD shines for complex business logic. Overkill for CRUD.

### Functional patterns (regardless of language)

- Immutability (especially for shared state)
- Pure functions (easier to test + reason about)
- Composition over inheritance
- Higher-order functions (map, filter, reduce)
- Avoid mutating arguments

### Concurrency models

- Threads + locks (classic, easy to get wrong)
- Actor model (Erlang, Akka)
- CSP / channels (Go, Clojure core.async)
- Async/await (Python, JS, C#, Rust)
- STM (Clojure)
- Functional / immutable (Haskell, Elixir)

### Database design fundamentals

- Normalize first, denormalize for performance
- Primary keys: surrogate (UUID/serial) > natural
- Foreign keys + constraints
- Indexes: balance read speed vs write cost
- Transactions: BEGIN, validate, COMMIT
- Migrations forward-only, idempotent

### Caching strategies

- **Cache-aside** — app reads cache, falls back to DB
- **Read-through** — cache fetches on miss
- **Write-through** — write goes through cache
- **Write-back** — write to cache, async to DB (durability risk)
- **Refresh-ahead** — proactive refresh of hot keys

Cache invalidation is one of the two hard problems.

### Distributed systems realities

- **CAP theorem** — pick 2 of {Consistency, Availability, Partition tolerance}
- **At-least-once** > exactly-once in practice (idempotency required)
- **Eventual consistency** is fine for many use cases
- **Time is unreliable** — don't trust clocks across nodes
- **Network is unreliable** — retries, timeouts, circuit breakers

### Refactoring techniques

- Extract function / method
- Rename
- Move
- Inline
- Replace conditional with polymorphism
- Strangler fig (incremental rewrite)

Tools: IDE-assisted refactoring (JetBrains, VS Code).

### SOLID (the full set, practically)

The file already nods to **S** in modularization. Here's the whole thing — each as *one-line principle → common violation → fix*. SOLID is a set of smells-and-cures, not a checklist to satisfy.

- **S — Single Responsibility.** A unit should have one reason to change.
  - *Violation:* `User` class that validates, persists to DB, and renders HTML.
  - *Fix:* split into `User` (data), `UserRepository` (persistence), `UserView` (render). One axis of change each.
- **O — Open-Closed.** Open to extension, closed to modification.
  - *Violation:* `if shape == "circle" ... elif "square" ...` growing with every new shape.
  - *Fix:* a `Shape.area()` method per type; add a new type without touching the dispatcher. (Don't pre-build this for 2 shapes — see below.)
- **L — Liskov Substitution.** Subtypes must honor the base type's contract.
  - *Violation:* `Square extends Rectangle` but overriding `setWidth` also mutates height — breaks callers that assume independence.
  - *Fix:* don't model "is-a" by inheritance when the contract diverges. Prefer composition or a shared `Shape` interface.
- **I — Interface Segregation.** No client should depend on methods it doesn't use.
  - *Violation:* fat `Repository` interface with 20 methods; a read-only consumer must mock all 20.
  - *Fix:* split into `Reader` / `Writer` interfaces; clients depend only on what they call.
- **D — Dependency Inversion.** Depend on abstractions, not concretions.
  - *Violation:* service `new PostgresClient()` inline — untestable, locked to Postgres.
  - *Fix:* accept a `Store` interface via constructor; inject Postgres in prod, fake in tests. (This is the testability payoff that justifies hexagonal above.)

**When NOT to.** SOLID earns its keep in long-lived code with real variation. Cargo-culting it produces one-implementation interfaces, factories that build one thing, and indirection that hides the actual logic. Don't extract an interface for a single concrete type, don't split a 40-line class to chase "single responsibility," and don't add an abstraction before the second case exists (rule of 3 still wins). The principles are tools for managing *actual* change — not points to score.

Ref: [Fowler — InterfaceImplementationPair](https://martinfowler.com/bliki/InterfaceImplementationPair.html) (on the over-applied interface-per-class smell).

---

## 7. References

### Books
- **The Pragmatic Programmer** — Hunt, Thomas (classic)
- **Refactoring** — Martin Fowler
- **Designing Data-Intensive Applications** — Kleppmann
- **A Philosophy of Software Design** — John Ousterhout
- **Clean Code** — Robert Martin (controversial but read it)
- **Working Effectively with Legacy Code** — Michael Feathers
- **The Mythical Man-Month** — Brooks (timeless)

### Blogs
- **martinfowler.com**
- **ThoughtWorks Insights**
- **High Scalability**
- **dev.to / lobste.rs** for trending

### Standards
- **HTTP / REST best practices**
- **OpenAPI specification** for APIs
- **OAuth2 / OIDC** for auth

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | Implementation of design |
| Software architect / Tech lead | Code review, architectural questions |
| Data Engineer | Pipeline coding, contracts |
| ML Engineer | Model integration into apps |
| AI Engineer | LLM application coding |
| DevOps | CI/CD, observability instrumentation |
| Product / PM | Translate requirements to spec |
| QA | Test strategy + automation |

---

*Software engineering = craft + judgment + empathy. Code that survives is code you'd want to read in 6 months.*
