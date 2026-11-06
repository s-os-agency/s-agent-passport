# Passport server component

The Passport product now references its private server project at `packages/passport-server` as a pinned Git submodule. This provides one product checkout while retaining the server repository’s access controls, independent lockfile and history.

## Source provenance

| Item | Value |
| --- | --- |
| Product repository | `s-os-agency/s-agent-passport` |
| Product baseline | `f9dc8fa9aee2fbce176a6672d24d029a967c2c30` |
| Server repository | `s-os-agency/s-agent-passport-server` (private) |
| Server source branch at selection | `chore/initial-server-project` |
| Pinned server commit | `0524a8668e205722c65ac9623a69324ed1f7ecfe` |
| Package path | `packages/passport-server` |

The recorded Git link is the authoritative version. No tracking branch is configured: a normal submodule update checks out that exact commit instead of silently following a moving branch. The source branch was the server repository’s default at selection time.

## Checkout

With an existing Git credential helper or SSH configuration that can read the private server repository:

```bash
git clone --recurse-submodules https://github.com/s-os-agency/s-agent-passport.git
```

For an existing checkout, after fetching and checking out the consolidation commit:

```bash
git submodule sync -- packages/passport-server
git submodule update --init --recursive -- packages/passport-server
git submodule status -- packages/passport-server
```

Do not put access tokens into `.gitmodules`, remote URLs, scripts or commits. A public clone without private-repository access still contains the main product; it cannot initialize the server component. Public source ZIP downloads do not include private submodule files. CI jobs that need this component must use an existing appropriately scoped credential; the default public-repository token does not automatically gain access to the private repository.

## Build and run independently

The existing root application already contains `server/`, `client/`, `shared/` and its own package and lockfile. The server component is a separate full-stack application, not a folder to overlay onto that existing `server/`. It retains its own `client/`, `server/`, `shared/`, package manifest, lockfile, TypeScript paths and Vite configuration.

From the product root, initialize the submodule, then:

```bash
cd packages/passport-server
corepack pnpm install --frozen-lockfile
corepack pnpm check
corepack pnpm build
```

The pinned package declares pnpm 10.4.1. Supply its required environment through local or deployment-managed configuration; inspect its current environment and database configuration before running `corepack pnpm dev` or `corepack pnpm start`. Do not run its database migration command as part of initialization. Run the two applications on separate ports when developing them together.

No workspace linking, root dependency hoisting, lockfile merging, shared database, issuer unification or automatic runtime wiring is introduced by this package reference. Existing root install/build commands retain their current scope. Root TypeScript includes only `client/src`, `shared` and `server`; the added package stays outside that compilation. The root formatter ignores the private package so product-wide formatting does not rewrite its independent source.

## Updating the pin

Fetch and review the intended server commit in the component checkout, check out that commit, and commit the resulting Git link change in the product repository. Update this provenance record with the new commit and reason. Keep component changes in its own repository before updating the parent pin; do not treat an uncommitted component working tree as a product release.

## Outstanding work preserved

The existing server normalization pull request and the product’s signing, dependency and passkey pull requests remain separate open changes. They are not absorbed by this packaging commit. This change does not claim a deployed service, shared authentication or a completed backend integration.

## Execution record

Added a pinned private server component under the Passport product, checkout instructions and source provenance. Inspected the Git link, file diff and parent compilation scope; no software test suites were added or run.

Implemented by **Codex / passport_consolidation** on 6 November 2026.
