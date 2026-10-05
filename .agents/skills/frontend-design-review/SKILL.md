---
name: frontend-design
description: Use when creating or significantly modifying React frontend interfaces, components, layouts, visual systems, typography, spacing, colors, animations or other visual design decisions.
---

---

# Frontend Design

## Purpose

Create polished, coherent and production-quality frontend interfaces.

This skill focuses on visual design and frontend implementation.

For UX principles use `web-design`.

For Hidroemcol-specific visual and business decisions use `hidroemcol-frontend`.

---

## 1. Establish visual direction

Before implementing a significant page, establish a coherent visual direction.

Consider:

- Industry.
- Audience.
- Brand personality.
- Content.
- Function of the page.
- Visual hierarchy.

For Hidroemcol, the visual language should communicate:

- Technical expertise.
- Industrial capability.
- Precision.
- Reliability.
- Professionalism.
- Engineering.
- Hydraulic and electrohydraulic technology.

Avoid generic visual styles unrelated to the industrial context.

---

## 2. Visual hierarchy

The most important information should receive the strongest visual emphasis.

Use differences in:

- Size.
- Weight.
- Position.
- Spacing.
- Contrast.
- Container structure.

Do not make every element visually dominant.

A page should have an obvious reading path.

---

## 3. Typography

Use a consistent typographic system.

Define clear relationships between:

- Display headings.
- Page headings.
- Section headings.
- Body text.
- Supporting text.
- Labels.
- Buttons.

Avoid using too many font families.

Prioritize readability over decorative typography.

Typography should remain readable on mobile.

---

## 4. Spacing

Use a consistent spacing system.

Related elements should be visually closer together.

Unrelated sections should have greater separation.

Avoid arbitrary spacing values throughout the application.

Prefer reusable spacing conventions.

---

## 5. Color

Use color intentionally.

A color should have a purpose such as:

- Brand identity.
- Primary action.
- Secondary action.
- Status.
- Warning.
- Error.
- Success.
- Background hierarchy.

Do not use many competing accent colors.

Important information must not depend solely on color.

---

## 6. Components

Prefer reusable React components.

Examples:

- Button.
- Card.
- Input.
- Select.
- Modal.
- Badge.
- Navigation.
- Hero.
- Service card.
- Product card.
- Section.
- Form.

Components should have a clear responsibility.

Avoid creating components so generic that their behavior becomes difficult to understand.

---

## 7. Layout

Use modern CSS layout systems.

Prefer:

- CSS Grid.
- Flexbox.
- Fluid sizing.
- Responsive containers.

Avoid layouts based primarily on:

- Absolute positioning.
- Hardcoded pixel coordinates.
- Fixed widths that prevent adaptation.

Absolute positioning is acceptable when it serves a deliberate visual purpose.

---

## 8. Cards

Cards should communicate meaningful groups of information.

Do not turn every piece of content into a card simply because cards are visually attractive.

A card should have:

- Clear purpose.
- Clear hierarchy.
- Appropriate spacing.
- Appropriate interaction if clickable.

---

## 9. Images

Images should support the message of the page.

For Hidroemcol, prioritize imagery related to:

- Hydraulic systems.
- Hydraulic components.
- Industrial machinery.
- Technical workshops.
- Test benches.
- Electrohydraulic control systems.
- Engineering work.

Avoid irrelevant generic stock imagery.

Do not distort images.

Use appropriate aspect ratios and responsive sizing.

---

## 10. Icons

Icons should reinforce meaning.

Use a consistent icon family.

Do not use icons merely as decoration when they add no information.

Interactive icons should have accessible labels when necessary.

---

## 11. Microinteractions

Use animation to communicate:

- State changes.
- Navigation.
- Loading.
- Feedback.
- Relationships between elements.

Animations should be subtle and purposeful.

Avoid excessive:

- Parallax.
- Floating elements.
- Continuous movement.
- Decorative animations.

Respect reduced-motion preferences.

---

## 12. Hover and interaction states

Interactive elements should communicate their state.

Consider:

- Default.
- Hover.
- Focus.
- Active.
- Disabled.
- Loading.
- Error.

Do not rely exclusively on hover because touch devices do not have hover in the same way.

---

## 13. Responsive visual design

Do not merely scale desktop designs down.

Adapt:

- Typography.
- Grid columns.
- Navigation.
- Spacing.
- Images.
- Component density.
- Section composition.

Mobile layouts may require a different visual hierarchy.

---

## 14. Empty states

Empty interfaces should still communicate what the user can do.

Examples:

- No products found.
- No search results.
- No available appointments.
- No previous requests.

Explain the situation and provide an appropriate next action.

---

## 15. Error states

Errors should be visible and understandable.

Avoid technical messages such as:

`500 Internal Server Error`

as the only message shown to users.

Where appropriate, provide:

- Explanation.
- Recovery action.
- Retry.

---

## 16. React implementation

Use the existing React and TypeScript architecture.

Before creating a new component:

1. Check whether an existing component can be reused.
2. Check whether a similar pattern already exists.
3. Follow the established project structure.
4. Avoid unnecessary dependencies.

Do not introduce a UI framework or design system without discussing it first.

---

## 17. Design quality

Before considering a visual implementation complete, inspect:

- Alignment.
- Spacing.
- Typography.
- Contrast.
- Consistency.
- Responsive behavior.
- Component reuse.
- Interactive states.
- Visual hierarchy.

The interface should look intentionally designed rather than assembled from unrelated components.
