---
name: web-design
description: Use when designing, structuring or improving web interfaces, especially when UX, responsive behavior, accessibility, navigation, information architecture or interaction design are important.
---

---

# Web Design

## Purpose

Provide general principles for designing usable, responsive, accessible and understandable web interfaces.

This skill focuses primarily on UX and interaction design rather than visual decoration.

For Hidroemcol-specific decisions, follow `hidroemcol-frontend` and `AGENTS.md`.

---

## 1. User first

Design around the user's objective rather than around the technology.

Before implementing a page, identify:

- Who is using it.
- What the user wants to accomplish.
- What information the user needs.
- What action the user should take next.
- What could confuse or block the user.

Avoid adding UI elements that do not contribute to the user's goal.

---

## 2. Information architecture

Information should be organized according to how users understand the business.

Use:

- Clear page hierarchy.
- Logical navigation.
- Descriptive section names.
- Consistent terminology.
- Grouping of related information.

Users should be able to understand the purpose of a page without exploring the entire interface.

For service-oriented pages, prioritize:

1. What the service is.
2. What problem it solves.
3. What Hidroemcol can do.
4. Relevant technical information.
5. What the user can do next.

---

## 3. Navigation

Navigation should be predictable.

Avoid:

- Hidden important actions.
- Excessively deep navigation.
- Ambiguous labels.
- Different navigation patterns between pages without justification.

Important actions such as contacting Hidroemcol or requesting information should remain easy to find.

---

## 4. Responsive design

Use a mobile-first approach.

Design progressively for:

- Mobile.
- Tablet.
- Desktop.

Prefer fluid layouts using:

- Flexbox.
- CSS Grid.
- Flexible widths.
- `minmax()`.
- `clamp()`.
- Relative spacing.

Avoid unnecessary fixed widths.

Do not solve responsive problems by simply adding many media-query overrides.

---

## 5. Mobile usability

On small screens:

- Buttons must be easy to tap.
- Text must remain readable.
- Navigation must remain usable.
- Important actions should remain visible.
- Cards should not become excessively narrow.
- Content should not require horizontal scrolling.

Do not simply shrink the desktop interface.

Reconsider the layout when necessary.

---

## 6. Accessibility

Use semantic HTML whenever possible.

Examples:

- `header`
- `nav`
- `main`
- `section`
- `article`
- `footer`
- `button`
- `form`
- `label`

Forms must have associated labels.

Interactive elements must be keyboard accessible.

Do not communicate important information exclusively through color.

Maintain sufficient contrast.

Images that convey meaning should have appropriate alternative text.

---

## 7. Forms

Forms should minimize unnecessary effort.

For each field:

- Use a clear label.
- Explain unusual requirements.
- Use appropriate input types.
- Provide useful validation.
- Display understandable errors.
- Preserve user input when possible.

Do not request information that the system does not actually need.

---

## 8. Feedback

Users should understand what happened after an interaction.

Provide appropriate feedback for:

- Successful actions.
- Errors.
- Loading.
- Empty results.
- Disabled states.
- Validation.

Avoid silent failures.

---

## 9. Loading and empty states

Never assume that data is always immediately available.

Interfaces that depend on APIs should account for:

- Loading.
- Success.
- Empty results.
- Errors.
- Retry.

Loading states should preserve the layout when possible to avoid unnecessary visual shifts.

---

## 10. Calls to action

Primary actions should be visually distinguishable from secondary actions.

Examples relevant to Hidroemcol:

- Solicitar cotización.
- Consultar repuesto.
- Solicitar diagnóstico.
- Agendar servicio.
- Contactar asesor.

Avoid giving every button the same visual importance.

---

## 11. Content hierarchy

Users should be able to scan the page quickly.

Use:

- Clear headings.
- Short paragraphs.
- Lists when appropriate.
- Visual grouping.
- Consistent spacing.

Do not create large walls of technical text.

Technical information should be progressively disclosed when appropriate.

---

## 12. Error prevention

Prefer preventing errors over explaining them afterward.

Examples:

- Disable submission when required information is missing.
- Validate input before sending.
- Clearly indicate required fields.
- Confirm potentially destructive actions.

---

## 13. Consistency

Reuse established:

- Components.
- Spacing.
- Typography.
- Buttons.
- Form patterns.
- Feedback patterns.
- Navigation patterns.

Do not create a new visual or interaction pattern for every page.

---

## 14. Performance-aware UX

Avoid unnecessary interface complexity.

Prefer:

- Lazy loading where appropriate.
- Optimized images.
- Minimal unnecessary animations.
- Efficient rendering.
- Existing project data-fetching patterns.

Do not introduce performance-heavy libraries without justification.

---

## 15. Before considering a page complete

Check:

- Can a new user understand the page?
- Is the primary action obvious?
- Does it work on mobile?
- Does it work on desktop?
- Are loading and error states handled?
- Are forms understandable?
- Is the interface keyboard accessible?
- Is there unnecessary visual complexity?
- Is the terminology consistent with Hidroemcol?

If important answers are negative, improve the design before considering the task complete.
