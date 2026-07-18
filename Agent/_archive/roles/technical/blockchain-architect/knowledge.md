# Blockchain Architect — Comprehensive Knowledge

> Deep reference for the blockchain-architect subagent. The **technical** side of web3 — chain selection, smart-contract architecture, on-chain/off-chain design, infra, security, scalability. Tokenomics / regulation / business-fit live with **blockchain-consultant**.

---

## 1. Foundations

### What a Blockchain Architect does

Designs **trust-minimized systems** where the data layer is a shared, append-only ledger that multiple parties can verify without trusting each other or a central operator.

The blockchain architect:
- Decides **whether** a problem actually needs a blockchain (most don't — see below)
- Selects chain / L2 / appchain and the on-chain vs off-chain split
- Designs the smart-contract system (upgradeability, access control, economic safety)
- Wires in off-chain infra: RPC, indexers, oracles, wallets, account abstraction
- Owns the **security posture** — because on-chain bugs are irreversible and adversaries are funded

### Not to be confused with

- **Blockchain Consultant** — business case, tokenomics, regulatory/legal fit, go-to-market. *They decide if it's worth doing; you decide how to build it.*
- **Solution Architect** — owns the off-chain system (APIs, DBs, cloud). You hand them the chain integration contract.
- **Security Engineer / Auditor** — does the deep threat model + formal audit. You design *for* auditability; they verify.
- **Smart-contract Engineer** — implements. You spec the architecture and review.

### When blockchain is actually warranted — be honest

The honest default is **you probably don't need one**. A blockchain is a slow, expensive, hard-to-change database with a global adversary. Use it only when **all** of these hold:

| Condition | If false → |
|---|---|
| Multiple parties who **don't trust each other** write shared state | Use a normal DB |
| No party should be the **central authority** / single admin | Use a normal DB with audit logs |
| **Immutability / verifiability** by third parties is a hard requirement | Use a signed append-only log (e.g. QLDB, Merkle log) |
| You need a **shared source of truth across org boundaries** | Use an API + DB owned by one party |
| Assets/value must move **without an intermediary settling** | Use existing payment rails |

If you can name a single trusted operator who *could* run the system, you don't need a blockchain — you need a database and maybe a signed audit trail. Say this out loud to stakeholders early; it saves quarters of wasted effort.

### Decentralization / trust model basics

- **Trust model** = "who can break or censor this, and what would it cost them?" Always answer this first.
- **Permissionless (public)** — anyone reads/writes/validates (Ethereum, Solana). Maximum trust-minimization, public data, gas costs.
- **Permissioned (consortium)** — known validators (Hyperledger, Besu). Faster/cheaper, but it's *governance theater* if one party controls the validator set — at that point a DB is honest-er.
- **Decentralization is a spectrum, not a checkbox.** Most "blockchain" projects are centralized in practice (single sequencer, admin keys, one RPC provider). That's fine — just don't market it as decentralized.

---

## 2. Mental Models / Decision Frameworks

### When-to-use-blockchain decision tree

```
Do mutually-distrusting parties write shared state?
  No  → Database. Stop.
  Yes → Is there an acceptable trusted operator?
          Yes → Database + signed audit log. Stop.
          No  → Do you need public verifiability / censorship resistance?
                  Yes → Public L1/L2
                  No  → Permissioned chain (and re-check: is it really needed?)
```

### L1 vs L2 vs Appchain

| Option | Use when | Trade-off |
|---|---|---|
| **L1 (Ethereum mainnet)** | Max security/liquidity, high-value settlement, RWA, blue-chip DeFi | Expensive gas, ~12s blocks |
| **L1 (Solana / alt-L1)** | High throughput, low fee, consumer apps, payments | Smaller tooling/security ecosystem, different model (non-EVM) |
| **L2 rollup (Base/Arbitrum/OP)** | 95% of new EVM apps — cheap, fast, inherits Ethereum security | Sequencer centralization, bridge dependency, withdrawal delays (optimistic) |
| **Appchain / L3** | Need custom gas token, throughput isolation, app-specific governance | You now operate infra + bootstrap your own security/liquidity |

**2026 default: build on an Ethereum L2.** The L2 market has consolidated hard — Base, Arbitrum, and Optimism process ~90% of L2 transactions, Base alone >60% and the only L2 that turned a profit in 2025. Dozens of niche rollups are becoming "zombie chains." Pick a survivor:
- **Base** — best consumer/retail distribution (Coinbase, 100M+ users), highest tx volume.
- **Arbitrum** — deepest DeFi liquidity, institutional default (GMX, Pendle, Aave).
- **Optimism / Superchain** — interop-focused, OP Stack ecosystem, good for app-chains-as-rollups.

Don't pick an L2 on TPS benchmarks — pick on **where your users and liquidity already are**.

### EVM vs non-EVM

| | EVM (Ethereum + L2s, Polygon, BNB, Avax) | Non-EVM (Solana, Aptos/Sui-Move, Cosmos) |
|---|---|---|
| Tooling | Largest — Foundry, viem, OpenZeppelin, every auditor | Smaller, fragmented |
| Talent | Abundant | Scarce |
| Composability | Massive existing DeFi/RWA ecosystem | Growing, more isolated |
| Performance | Lower per-chain (mitigated by L2s) | Higher (Solana parallel execution) |

**Default to EVM** unless you have a concrete throughput/UX need that Solana or Move solves and you can staff it. The EVM ecosystem advantage (auditors, libraries, indexers) usually outweighs raw performance.

### On-chain vs off-chain — what to store where

The single most important architectural decision. **On-chain is the most expensive storage in computing.** Rule: store the *minimum that needs consensus/verifiability*; everything else off-chain.

| Put on-chain | Put off-chain |
|---|---|
| Ownership / balances / state transitions | Images, video, large JSON, PII |
| Hashes / Merkle roots / commitments of off-chain data | The actual blob (IPFS/Arweave/S3) — store its hash on-chain |
| Access-control logic, settlement, escrow | Application UI/business logic |
| Events (for indexing) | Search indexes, analytics, feeds |

**Pattern**: store data off-chain (IPFS/Arweave for decentralized, S3 for not), put the **content hash** on-chain. You get verifiability without paying to store bytes. NFT metadata works this way; "fully on-chain NFTs" are a deliberate (costly) exception.

### Consensus trade-offs (one-liners)

- **PoW** — battle-tested, energy-heavy, slow finality. Bitcoin. Rarely your choice for new apps.
- **PoS** — Ethereum + most L1s. Good security/efficiency balance, faster finality.
- **PoA / permissioned BFT** — consortium chains, fast, but trust = the validator set.

### The Blockchain Trilemma

You can optimize **two** of {Decentralization, Security, Scalability} at L1; the third suffers. The modern answer is **modular scaling**: keep security+decentralization at L1, push scalability to L2 rollups (and DA layers). This is why "just use an L2" is the right default — it sidesteps the trilemma instead of fighting it.

### Custody models

| Model | Who holds keys | Use when |
|---|---|---|
| **Self-custody (EOA)** | User | Max sovereignty, crypto-native users |
| **Smart account (AA / ERC-4337)** | User + programmable rules | Best UX: gas sponsorship, social recovery, session keys |
| **MPC** | Key split across parties | No single point of compromise, institutional |
| **Custodial** | You / a custodian (Fireblocks, Coinbase) | Regulated, mainstream users, you accept liability |

**2026 default for consumer apps: smart accounts.** They remove seed-phrase friction (social recovery, sponsored gas) without you holding keys.

---

## 3. Standard Practices

### Smart contract design

- **Upgradeability** — contracts are immutable once deployed, so use a **proxy pattern** when you need to ship fixes: UUPS (recommended — upgrade logic in the implementation, cheaper) or Transparent proxy. Use **OpenZeppelin** proxies, never hand-roll. *But*: every upgrade path is also an attack surface and a centralization vector — for truly trust-minimized contracts, consider **immutable + new-deployment migration** instead.
- **Access control** — `Ownable` for single-admin (acceptable for early stage, disclose it), `AccessControl` (role-based) for production. Put admin keys behind a **multisig (Safe)** or timelock — never a single EOA.
- **Events** — emit an event for every state change. Events are how the off-chain world (indexers, frontends, monitoring) observes the chain. Under-emitting events is a design bug.
- **Checks-Effects-Interactions** — validate, then update state, *then* make external calls. This single ordering rule prevents most reentrancy.
- **Pull over push** — let users withdraw (pull) rather than the contract sending (push); avoids failed-transfer DoS and reentrancy.

### Security patterns (irreversible bugs = treat as life-critical)

- **Reentrancy** — Checks-Effects-Interactions + `ReentrancyGuard` on functions making external calls. Still the canonical bug.
- **Oracle safety** — never trust a spot price from a single DEX pool (flash-loan manipulable). Use **Chainlink** decentralized feeds or TWAPs; cross-check sources. Oracle manipulation is a top exploit class in 2025-2026.
- **Integer overflow** — Solidity ≥0.8 reverts on overflow by default; still be careful with `unchecked` blocks.
- **Access-control bugs** — missing/incorrect modifiers on privileged functions. The most common audit finding.
- **Front-running / MEV** — assume the mempool is public and adversarial; use commit-reveal, slippage limits, private order flow where needed.

### Testing — Foundry

- **Foundry is the 2026 standard for serious contract work** — Rust-based, fast, with **built-in fuzz + invariant testing** (Hardhat needs external tools). Hardhat still has wider share for full-stack/deployment + better JS/frontend integration; the two coexist in one repo (Foundry for tests, Hardhat for deploy/integration).
- Write **invariant tests** ("total supply always equals sum of balances"), **fuzz tests** (random inputs), and **fork tests** (against mainnet state).
- Aim for high coverage on value-moving paths. Coverage ≠ safety, but gaps on money paths are unacceptable.

### Gas optimization (only after correctness)

- Minimize **storage writes** (`SSTORE` is the dominant cost); pack structs into 32-byte slots; use `immutable`/`constant`.
- Use events instead of storage for data you only need to read off-chain.
- Batch operations; prefer `calldata` over `memory` for external fn args.
- Don't sacrifice readability/safety for micro gas savings on L2s where gas is already cheap.

### Indexing

- You **cannot** query a chain like a DB. Use an indexer to turn on-chain events into queryable data.
- **The Graph** — established, declarative subgraphs, decentralized; great for standard cases, weaker on real-time/high-frequency.
- **Ponder** — TypeScript, fast, full customization, good DX for app-specific indexing.
- **Envio / Alchemy Subgraphs** — performance-focused alternatives.
- Choose: The Graph for decentralization/standard, Ponder/Envio for speed + custom logic.

### Wallet / key management

- Treat private keys like nuclear launch codes. **Never** in code, env files committed to git, or logs.
- Admin keys → **multisig (Safe)** + timelock. Deployer keys → hardware wallet / KMS.
- For institutional custody → **MPC** (Fireblocks) or qualified custodian.
- Rotate, segregate by environment, and assume any single key will eventually leak. (Private-key compromise = ~88% of stolen funds in Q1 2025.)

### Audits

- **Mandatory** before mainnet for anything holding value. One audit is a floor, not a guarantee — most 2025 exploits hit *audited* contracts.
- Layer defenses: internal review → ≥1 reputable audit → public bug bounty (Immunefi) → monitoring + pausability → gradual TVL ramp.
- Budget audits in *months* and real money. If the project can't afford an audit, it can't afford to hold funds.

### Oracles — Chainlink

- Default to **Chainlink** for price feeds, VRF (randomness), Automation (keepers), and **CCIP** (cross-chain messaging).
- Never derive critical prices from a single manipulable source. Validate freshness (staleness checks) and bounds.

---

## 4. Tools Landscape (2026)

### Chains / L2s
- **Ethereum L1** — settlement, RWA, high-value DeFi
- **Base / Arbitrum / Optimism** — the surviving L2 majority; default for new EVM apps
- **Polygon, BNB Chain, Avalanche** — EVM alternatives with their own ecosystems
- **Solana** — high-throughput consumer/payments, non-EVM (Rust/Anchor)
- **Aptos / Sui** — Move-based, parallel execution

### Smart-contract dev
- **Foundry** — Rust, fast, fuzz + invariant testing built in (test/dev standard)
- **Hardhat** — JS/TS, deployment + frontend integration, wider full-stack share
- **OpenZeppelin Contracts** — audited standard library (ERC-20/721/1155, proxies, AccessControl) — don't reimplement these
- **Solidity** (EVM), **Vyper** (security-minimalist alt), **Rust/Anchor** (Solana), **Move** (Aptos/Sui)

### Frontend / client
- **viem** — modern low-level TypeScript Ethereum interface (replaces ethers/web3.js for new builds)
- **wagmi** — React hooks over viem (multi-chain, connectors, account mgmt)
- **WalletConnect / RainbowKit / ConnectKit** — wallet connection UX

### Infra / RPC
- **Alchemy, Infura, QuickNode** — managed RPC + enhanced APIs (don't run your own node early)
- **Self-hosted node** — only when decentralization/cost/control demands it

### Indexing
- **The Graph** (decentralized subgraphs), **Ponder** (TS, custom), **Envio** (speed)

### Account abstraction (ERC-4337 / EIP-7702)
- **ERC-4337** — smart accounts via alt-mempool UserOperations; gas sponsorship (paymasters), batching, session keys, social recovery. ~30-50% gas overhead vs an EOA.
- **EIP-7702** (live since Pectra, May 2025) — lets a normal EOA *temporarily* execute contract code; **complements, not replaces** 4337 and is compatible with its infra. The two together are the AA stack.
- **Bundler/paymaster providers** — Pimlico, Alchemy, Biconomy, ZeroDev.

### Stablecoins / RWA
- **Stablecoins** = the settlement layer (~$300B+ mcap, tens of trillions in annual transfer volume; GENIUS Act gave US a federal framework in 2025). USDC/USDT for payments + on/off-ramps.
- **RWA tokenization** — fast-growing ($30B+ on-chain excl. stablecoins by 2026); tokenized Treasuries the largest category (BlackRock BUIDL, Franklin Templeton). Standards trending toward ERC-3643 (permissioned/compliant tokens) for regulated assets.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Blockchain for a problem a DB solves | Slow, costly, hard to change — no trust benefit gained | Honest decision tree; default to a database |
| Storing large data on-chain | Pay forever to store bytes that don't need consensus | Store hash on-chain, blob on IPFS/Arweave/S3 |
| Unaudited contracts holding value | Irreversible loss, you become a rekt.news headline | Audit + bounty + monitoring + gradual ramp |
| Rolling your own crypto / proxy / token | Subtle bugs you can't see; auditors can't either | OpenZeppelin, audited standards, established libs |
| No upgrade path (when you'll need fixes) | Can't patch a critical bug post-deploy | Proxy pattern *or* deliberate immutable + migration plan |
| Upgradeable everything | Every upgrade key is an attack + centralization vector | Upgrade only what must change; timelock + multisig |
| Ignoring gas at design time | Unusable on L1, surprise costs | Model gas early; pick L2; minimize storage writes |
| Single oracle / spot-price trust | Flash-loan price manipulation drains the protocol | Chainlink/TWAP, multi-source, staleness checks |
| Private keys in code / env / logs | ~88% of stolen funds trace to key compromise | KMS/HSM, multisig admin, hardware wallets |
| "Decentralized" but one sequencer/admin/RPC | Centralized reality, false marketing, real SPOF | Be honest; reduce SPOFs where it matters |
| Trusting the mempool (no MEV defense) | Front-running, sandwich attacks | Commit-reveal, slippage limits, private order flow |
| Naive cross-chain bridge | Bridges = ~40% of all web3 value hacked | Minimize bridging; use CCIP/audited canonical bridges |
| No event emission | Off-chain world can't observe state | Emit events on every state change |

---

## 6. Advanced / Expert Topics

### L2s / Rollups — optimistic vs ZK

- **Optimistic (Arbitrum, Base, OP)** — assume valid, allow fraud proofs in a challenge window. Mature, cheap, EVM-equivalent. Cost: ~7-day withdrawal delay to L1 (mitigated by liquidity bridges).
- **ZK rollups** — every batch carries a validity proof (SNARK/STARK); **instant finality**, no challenge window, the gold standard for financial apps. 2026 prover-hardware advances cut proof cost sharply; the trend is toward ZK. zkEVMs (zkSync, Polygon zkEVM, Scroll, Linea) are maturing.
- **Pick**: optimistic for cheapest + most mature EVM today; ZK where fast finality / withdrawal speed / cryptographic guarantees matter.

### Account abstraction (deep)
Smart accounts unlock: **gas sponsorship** (onboard users with zero ETH), **session keys** (gaming/agents act without per-tx signing), **social recovery** (no seed-phrase loss), **batched txs** (approve+swap in one click), **passkey/biometric signing**. ERC-4337 + EIP-7702 (Pectra) are the converged stack — design consumer UX around this in 2026.

### Modular blockchains (DA layers)
Separate **execution / settlement / consensus / data availability** into specialized layers. DA is the current battleground:
- **Celestia** — pioneered modular DA, Data Availability Sampling, ~$0.001/MB, ~50% DA market share.
- **EigenDA** — restaking-secured (EigenLayer), high throughput, Ethereum-native security.
- **Avail** — multichain coordination focus.
Choose DA on cost vs security-source vs throughput. Posting to Ethereum blobs (EIP-4844) remains the most-secure default; alt-DA trades security for cost.

### Cross-chain / bridges (+ risks)
Bridges are the **single most-exploited primitive in web3** (~40% of all value hacked: Ronin $625M, Wormhole $325M, Nomad $190M; 2026 bridge exploits continue). Risk sources: smart-contract bugs, validator/multisig compromise, forged cross-chain messages (e.g. spoofed LayerZero instructions), social-engineered admin keys.
- **Minimize bridging** architecturally. If unavoidable, use **canonical / audited** bridges or message layers (Chainlink CCIP, LayerZero, Wormhole) and treat the bridge as your weakest link in threat modeling.

### ZK proofs — use cases beyond rollups
- **Privacy** — prove a statement without revealing data (private payments, private balances)
- **Identity** — prove "over 18" / "KYC'd" / "unique human" without exposing the underlying data (on-chain identity, proof of personhood)
- **Verifiable compute** — prove an off-chain computation ran correctly (the bridge to verifiable AI/data, below)
- **Scaling** — validity proofs (rollups)

### RWA tokenization
Bringing off-chain assets (Treasuries, credit, equities, commodities, real estate) on-chain as tokens. The fastest-growing institutional use case (BlackRock, JPMorgan, Franklin Templeton). Architect concerns: **compliance-aware token standards (ERC-3643 / permissioned transfers)**, identity/whitelist gating, oracle-fed NAV, and the legal-wrapper ↔ on-chain-token binding (hand the legal side to blockchain-consultant + governance).

### On-chain identity
Soulbound tokens, verifiable credentials, ENS, proof-of-personhood. Foundation for under-collateralized lending, reputation, compliant RWA, sybil resistance. Pair with ZK for privacy-preserving credentials.

### MEV (Maximal Extractable Value)
Validators/searchers reorder/insert/censor txs for profit. Affects every public-mempool app. Defenses: private order flow (Flashbots), commit-reveal, batch auctions (CoW), MEV-aware AMM design. Architect every value-moving tx assuming an adversary sees it first.

### Scaling patterns
- **State channels / app-specific rollups** for high-frequency interactions
- **Optimistic off-chain compute + on-chain settlement**
- **Account abstraction batching** to amortize gas
- Push everything possible off-chain; settle on-chain.

### Blockchain × AI / Data
- **Provenance** — immutable hash-on-chain of datasets/model versions for tamper-evident audit trails (strong fit for data-platform work)
- **Verifiable compute (zkML)** — prove an AI inference ran a specific model on specific inputs without revealing them
- **Agent payments** — smart accounts + session keys + stablecoins let autonomous agents transact under bounded authority
- **Data marketplaces** — tokenized access, on-chain settlement for off-chain data/compute
Be skeptical of "AI + blockchain" pitches: usually only the *provenance/settlement* slice genuinely needs a chain — the rest is off-chain.

---

## 7. References

### Core docs
- **Ethereum docs** — https://ethereum.org/en/developers/docs/
- **Solidity docs** — https://docs.soliditylang.org/
- **OpenZeppelin Contracts** — https://docs.openzeppelin.com/contracts/
- **Foundry Book** — https://book.getfoundry.sh/
- **viem** — https://viem.sh/ · **wagmi** — https://wagmi.sh/
- **ERC-4337** — https://eips.ethereum.org/EIPS/eip-4337 · **EIP-7702** — https://eips.ethereum.org/EIPS/eip-7702

### Security / post-mortems (read these religiously)
- **rekt.news** — exploit post-mortems (learn from others' losses) — https://rekt.news/
- **Chainlink security/oracle education** — https://chain.link/education-hub
- **Immunefi** — bug bounty platform + writeups — https://immunefi.com/

### Ecosystem / data
- **L2Beat** — L2 risk + activity dashboard (read before picking an L2) — https://l2beat.com/
- **RWA.xyz** — tokenized RWA analytics — https://app.rwa.xyz/
- **a16z crypto** — trends, research, builder playbooks — https://a16zcrypto.com/
- **The Graph docs** — https://thegraph.com/docs/ · **Ponder** — https://ponder.sh/

---

## 8. Working With Other Roles

| Role | Handoff / common discussion |
|---|---|
| **Blockchain Consultant** | "Is there a real business + regulatory case, and what's the tokenomics?" — *they* validate fit; you take it from "should we" to "how". |
| **Security Engineer / Auditor** | "Here's the contract architecture, trust model, and admin-key design — threat-model and audit it." You design for auditability; they verify. |
| **Solution Architect** | "Here's the on-chain ↔ off-chain contract: events to index, RPC dependency, oracle inputs, custody boundary." They own the off-chain system. |
| **Software / Frontend Engineer** | "Build the dApp on viem/wagmi against these contracts + indexer; here's the AA/wallet UX." |
| **Data Architect** | "On-chain events feed the indexer/warehouse; here's the provenance/hash-anchoring design." |
| **Governance / Compliance Consultant** | "Here's how permissioned token standards, identity gating, and admin controls map to compliance requirements." |
| **Product Manager** | "Translate the UX (gasless onboarding, recovery, custody) into the AA + chain choices." |

---

*Reference selectively. The architect's first and highest-value job is often to say "you don't need a blockchain for this." When you do need one: minimize what goes on-chain, treat every key and bug as catastrophic, and never trust a single oracle, bridge, or admin.*
