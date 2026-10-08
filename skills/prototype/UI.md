# UI Prototype

Make **several radically different UI variations** on a single route. The user selects a variation from a floating bottom bar. The user moves between variants in the browser and selects one (or takes parts from each). Then the user throws the others away.

If the question is about logic or state and not about how something looks, this is the wrong branch. Use [LOGIC.md](LOGIC.md).

## When this is the right shape

- "What should this page look like?"
- "I want to see a few options for this dashboard before committing."
- "Try a different layout for the settings screen."
- Any time when the user would otherwise use a day to select between three vague mockups in their head.

## Two sub-shapes: strongly prefer sub-shape A

A UI prototype is much easier to judge when it is **directly next to the rest of the app**. The app gives a real header, a real sidebar, real data and real density. A throwaway route by itself is a vacuum. Each variant looks fine in isolation. Use sub-shape A by default when a possible existing page can hold the variants. Use sub-shape B only if the prototype really has no near location.

### Sub-shape A: adjustment to an existing page (preferred)

The route already exists. The variants render **on the same route**, and a `?variant=` URL search param selects them. The existing data fetching, params and auth all stay. Only the rendering changes. This is the default. Select it unless you have a specific reason not to.

The prototype can be for something that does not have a page yet but *would naturally be inside one*. Examples are a new section of the dashboard, a new card on the settings screen, or a new step in an existing flow. That is still sub-shape A. Mount the variants inside the host page.

### Sub-shape B: a new page (last resort)

Use this only when the prototype really has no existing page to be inside (e.g. an entirely new top-level surface, or a flow that you cannot embed in a sensible place).

Create a **throwaway route** with the routing convention that the project already uses. Do not invent a new top-level structure. Give it a name that clearly shows a prototype (e.g. include the word `prototype` in the path or filename). Use the same `?variant=` pattern.

Before you select sub-shape B, do a quick test: is there really no existing page where you could embed it? An empty route hides design problems that a populated route would show.

In both sub-shapes, the floating bottom bar is the same.

## Process

### 1. State the question and pick N

Use **3 variants** by default. More than 5 are no longer radically different and become noise. Thus do not use more than that.

Write the plan in one line, at the location of the prototype or in a comment at the top of the file:

> "Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route."

This works when the user is available to disagree, and also when the user is not available.

### 2. Generate radically different variants

Write a draft of each variant. Each variant must obey these limits:

- The purpose of the page and the data that it has access to.
- The component library or styling system of the project (TailwindCSS, shadcn, MUI, plain CSS, or other).
- A clear exported component name, e.g. `VariantA`, `VariantB`, `VariantC`.

Variants must be **structurally different**: a different layout, a different information hierarchy, a different primary affordance. Different colors only are not sufficient. Three card grids with small changes are not a UI prototype. They are wallpaper. If two drafts are too similar, make one again with the explicit instruction "do not use a card grid".

### 3. Wire them together

Create a single switcher component on the route:

```tsx
// pseudo-code, adapt to the project's framework
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A','B','C']} current={variant} />
  </>
);
```

For sub-shape A (existing page): keep all the existing data fetching above the switcher. Only the rendered subtree changes for each variant.

For sub-shape B (new page): the throwaway route under `/prototype/<name>` mounts the same switcher.

### 4. Build the floating switcher

Make a small fixed-position bar at the bottom center of the screen. It has three parts:

- **Left arrow**: goes to the previous variant (after the first variant, it goes to the last).
- **Variant label**: shows the current variant key. If the variant exports a name, it also shows that name, e.g. `B (Sidebar layout)`.
- **Right arrow**: goes to the next variant (after the last variant, it goes to the first).

Behavior:

- A click on an arrow updates the URL search param. Use the router of the framework, e.g. `router.replace` on Next, `navigate` on React Router, etc. Then the user can share the variant, and it stays after a reload.
- Keyboard: the `←` and `→` arrow keys also change the variant. Do not catch arrow keys when an `<input>`, `<textarea>`, or `[contenteditable]` has focus.
- Make it look different from the page (e.g. a high-contrast pill, a subtle shadow), so that it is clearly not part of the design under evaluation.
- Hide it in production builds. Use `process.env.NODE_ENV !== 'production'` or an equivalent check as a gate, so that an accidental prototype merge cannot send the bar to users.

Put the switcher in a single shared component, so that both sub-shapes can use it again. Put it where the shared UI of the project is.

### 5. Hand it over

Give the URL (and the `?variant=` keys). The user will look through the variants when they have time. The interesting feedback is usually **"I want the header from B with the sidebar from C"**. That is the actual design that they want.

### 6. Capture the answer and clean up

When a variant wins, record the answer (which variant and why). Then keep the prototype as the [SKILL](SKILL.md) describes. Put the winner into the real code. Move the others to the throwaway branch, not into main:

- **Sub-shape A**: put the winner into the existing page. Remove the losing variants and the switcher from main.
- **Sub-shape B**: change the winning variant into a real route. Remove the throwaway route and the switcher from main.

The full set of variants is the primary source. Thus it goes to the throwaway branch, not to the bin. Variant components and a switcher in the main branch decay fast and confuse the next reader.

## Anti-patterns

- **Variants that differ only in colour or copy.** That is a small change, not a prototype. Real variants disagree about structure.
- **Sharing too much code between variants.** A shared `<Header>` is fine. A shared `<Layout>` defeats the purpose. Each variant should be free to throw out the layout.
- **Wiring variants to real mutations.** Read-only prototypes are fine. If a variant must change data, point it at a stub. The question is "what should this look like", not "does the backend work".
- **Promoting the prototype directly to production.** Someone wrote the variant code under prototype constraints (no tests, minimal error handling). Write it again correctly when you put it into the real code.
