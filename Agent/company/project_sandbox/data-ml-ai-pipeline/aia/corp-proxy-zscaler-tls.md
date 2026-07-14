# Corporate Proxy (Zscaler) + TLS — unblocking az / databricks / pip / git

> **Status: UNRESOLVED / IN PROGRESS at AIA (2026-07-13).** Login flow now opens, ARM call still fails.
> **The missing piece is almost certainly the INTERMEDIATE certs** (root alone is not enough — §4).
> Generic ops note — no AIA internals. Reusable at any enterprise behind a TLS-inspecting proxy
> (Zscaler, Netskope, Blue Coat, Palo Alto...).

---

## 1. The symptom

```
$ az login
... unable to get local issuer certificate (_ssl.c:1032)
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed'))
```
Hits `login.microsoftonline.com` and/or `management.azure.com`. Same class of failure shows up in
`databricks` CLI, `pip install`, `git clone`, `curl`, npm — anything that ships its own CA store.

## 2. Root cause

**Zscaler is a MITM by design.** It terminates the TLS connection, inspects it, and **re-signs the
certificate with the Zscaler CA**. Your OS trusts that CA (IT pushed it). But:

- **Python / requests / azure-cli / databricks-cli use `certifi`'s bundled `cacert.pem`, not the OS store.**
- **Node uses its own bundle. Git may use its own. curl may use its own.**

None of them know about Zscaler → every TLS handshake fails. This is **not** a bug and **not** a
misconfiguration on your side. It is the price of TLS inspection, and the fix is always the same:
**give each toolchain a CA bundle that contains the proxy's CA chain.**

## 3. The trap: an exported Zscaler cert can be malformed

```
Error: Basic Constraints of CA cert not marked critical
```

RFC 5280 says a CA certificate's `basicConstraints` extension **must be marked critical**. Older
tooling tolerated it; **modern OpenSSL 3.x / Python 3.11+ enforce it** and reject the cert outright.
You will see this when the cert was exported wrong (or you grabbed an intermediate from the wrong store).

**Inspect before you trust:**
```bash
openssl x509 -in zscaler-root-ca.cer -text -noout | head -30
# Look for:
#   X509v3 Basic Constraints: critical      <-- the word "critical" MUST be there
#       CA:TRUE
```
If `critical` is missing → **re-export** (Base-64 X.509 / PEM, from **Trusted Root Certification
Authorities**), or better: **pull the chain off the wire** (§4), which always gives you well-formed DER.

## 4. ⭐ The fix that actually works: a master CA bundle (certifi + root **AND** intermediates)

The classic failure is doing this with the **root only**. Azure CLI login is **two phases against two
endpoints**, and they can present **different intermediates**:

```
Phase 1  login.microsoftonline.com   → browser flow opens ✅   (root was enough)
Phase 2  management.azure.com (ARM)  → "unable to get local issuer certificate" ❌  (needs the INTERMEDIATE)
```
If your login page opens and *then* it dies "retrieving subscriptions" — **that is this exact bug.**
You are one intermediate cert away from done.

**Get the full chain from the live connection** (this is the reliable way — no cert-store archaeology):
```bash
openssl s_client -showcerts -connect management.azure.com:443    </dev/null 2>/dev/null > chain-arm.pem
openssl s_client -showcerts -connect login.microsoftonline.com:443 </dev/null 2>/dev/null > chain-login.pem
# Behind Zscaler, every cert in these files is Zscaler-signed — that is the proof of interception.
grep -c "BEGIN CERTIFICATE" chain-arm.pem chain-login.pem
```

**Build the master bundle:**
```bash
CERTIFI=$(python -c "import certifi; print(certifi.where())")
# azure-cli ships its OWN python+certifi; if the above misses, use its bundle instead:
#   .../Microsoft SDKs/Azure/CLI2/Lib/site-packages/certifi/cacert.pem

cat "$CERTIFI"        >  ~/master-ca-bundle.crt   # public roots (keep these! don't replace, EXTEND)
cat zscaler-root*.cer >> ~/master-ca-bundle.crt   # Zscaler ROOT
cat zscaler-int*.cer  >> ~/master-ca-bundle.crt   # Zscaler INTERMEDIATE(s)  <<< the usual missing piece
cat chain-arm.pem chain-login.pem >> ~/master-ca-bundle.crt   # belt-and-braces: the on-the-wire chain

grep -c "BEGIN CERTIFICATE" ~/master-ca-bundle.crt            # sanity: should jump by the certs you added
```

**Point every toolchain at it — one bundle unblocks az + databricks + pip + git + curl + node together:**
```bash
export MASTER_CA="$HOME/master-ca-bundle.crt"
export REQUESTS_CA_BUNDLE="$MASTER_CA"   # python-requests → azure-cli, databricks-cli
export SSL_CERT_FILE="$MASTER_CA"        # python ssl / openssl
export CURL_CA_BUNDLE="$MASTER_CA"       # curl
export PIP_CERT="$MASTER_CA"             # pip
export NODE_EXTRA_CA_CERTS="$MASTER_CA"  # node / npm
git config --global http.sslCAInfo "$MASTER_CA"

az login --tenant <tenant-id>
databricks auth login --host https://adb-<id>.<n>.azuredatabricks.net
```
Put the exports in `~/.bashrc` / `~/.zshrc` (Git Bash on Windows: `~/.bash_profile`) so they survive.

## 5. Gotchas

| Gotcha | Detail |
|---|---|
| **Root alone is not enough** | Different Azure endpoints present different intermediates. **Add root + ALL intermediates.** This is the #1 cause of "login works, subscriptions fail". |
| **Path mangling in Git Bash** | `export REQUESTS_CA_BUNDLE="/c/Users/x/c/Users/x/cert.cer"` → the doubled prefix means you concatenated a Windows path onto a POSIX one. Windows `C:\Users\x\f.cer` = Git Bash `/c/Users/x/f.cer`. Always `ls -la "$REQUESTS_CA_BUNDLE"` before blaming the cert. |
| **Wrong CA entirely** | A cert named `<company>-corporate-ca` is often *not* the interceptor. **Zscaler is the one doing the MITM** — `openssl s_client` tells you the truth about who signed what. |
| **EXTEND, never REPLACE** | If the bundle contains only the Zscaler certs, every *public* CA breaks. Always start from `certifi`'s `cacert.pem`. |
| **azure-cli has its own certifi** | It bundles its own Python. Patch/point at *that* `cacert.pem` if `REQUESTS_CA_BUNDLE` alone doesn't take. |
| **Never `--insecure` / `verify=False`** | Disables verification wholesale. Fails audit at a regulated employer, and hides real MITM. Not an option. |
| **Cert rotation** | Zscaler CAs get rotated. When "it broke overnight and nobody changed anything" → rebuild the bundle. |

## 6. Debug ladder (in order)

1. `openssl s_client -showcerts -connect <host>:443` → **who actually signed this?** (Zscaler ⇒ interception confirmed)
2. `openssl x509 -in <cert> -text -noout | grep -A1 "Basic Constraints"` → is it **critical**? is it **CA:TRUE**?
3. `ls -la "$REQUESTS_CA_BUNDLE"` → does the file even exist at that path?
4. `grep -c "BEGIN CERTIFICATE" "$REQUESTS_CA_BUNDLE"` → did the concat actually work?
5. `curl -v --cacert "$MASTER_CA" https://management.azure.com/` → test the bundle **without** the CLI in the way.
6. Only then re-run `az login`.

## 7. If it still fails — ask IT for the right artifact

Ask for **"the full Zscaler CA chain (root + intermediates) in PEM/Base-64"**, not "the cert". Many
enterprises publish an official bundle; using theirs beats hand-assembling from the Windows cert store,
and it survives rotation because they update it.

---
*Provenance: chat hist 2026-07-13 session 02, Turns 18-22. Verdict at time of writing: root cert got the
browser flow open; the ARM call still failed → **intermediates were the missing piece**. Carry this forward.*
