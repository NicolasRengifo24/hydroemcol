---
name: frontend-design-review
description: Use when reviewing, auditing or validating a React frontend implementation for UX, responsive behavior, accessibility, visual consistency, usability and frontend quality.
---

---

# Frontend Design Review

## Purpose

Review an existing frontend implementation and identify concrete problems before considering the work complete.

This skill is for evaluation and improvement.

Do not rewrite the application simply to apply personal preferences.

Prioritize problems that affect:

1. Usability.
2. Accessibility.
3. Responsive behavior.
4. Visual hierarchy.
5. Consistency.
6. Maintainability.

---

## 1. Review the actual implementation

Before making recommendations:

- Read the relevant React components.
- Understand their relationships.
- Inspect existing styles.
- Inspect reusable components.
- Inspect routing when relevant.
- Inspect API/data dependencies when relevant.

Do not make recommendations based only on filenames.

---

## 2. UX review

Check:

- Can users understand the purpose of the page?
- Is the main action obvious?
- Is navigation predictable?
- Are labels understandable?
- Are important actions easy to find?
- Are forms understandable?
- Are error messages useful?
- Are loading states present?
- Are empty states present?

Identify the specific component or section causing the problem.

---

## 3. Responsive review

Check the interface at least conceptually for:

### Mobile

- Small phone.
- Larger phone.

### Tablet

- Portrait.
- Landscape.

### Desktop

- Standard laptop.
- Large desktop.

Look for:

- Horizontal overflow.
- Overlapping elements.
- Excessive whitespace.
- Text truncation.
- Broken grids.
- Navigation problems.
- Buttons that become difficult to tap.
- Images that overflow.
- Cards becoming too narrow.

Do not assume that a desktop screenshot proves responsive correctness.

---

## 4. Accessibility review

Check:

- Semantic HTML.
- Heading hierarchy.
- Labels.
- Keyboard navigation.
- Focus states.
- Button semantics.
- Link semantics.
- Alternative text.
- Contrast.
- Form errors.
- Motion behavior.

Do not recommend accessibility changes that have no practical relevance without explaining the reason.

---

## 5. Visual hierarchy

Check whether the page clearly communicates:

- What the page is about.
- What is most important.
- What the user should do next.

Look for:

- Too many competing headings.
- Excessive visual emphasis.
- Weak primary CTA.
- Inconsistent spacing.
- Poor alignment.
- Inconsistent component sizes.

---

## 6. Consistency

Compare the reviewed page with existing pages.

Look for consistency in:

- Navigation.
- Buttons.
- Typography.
- Spacing.
- Cards.
- Forms.
- Icons.
- Colors.
- Feedback.
- Responsive behavior.

Do not create a new visual language when the project already has one.

---

## 7. Interaction states

Check interactive components for:

- Default.
- Hover.
- Focus.
- Active.
- Disabled.
- Loading.
- Error.
- Success.

Not every component needs every state, but important interactive elements should communicate their current state.

---

## 8. Content review

Check whether:

- Headings describe the content accurately.
- Technical terms are understandable in context.
- Paragraphs are unnecessarily long.
- Calls to action are specific.
- Important information is visible.
- Users are not forced to interpret technical implementation details.

Do not rewrite business information without checking the project context.

---

## 9. Mobile-first problems

Pay particular attention to interfaces that were clearly designed for desktop first.

Common warning signs:

- Desktop navigation compressed into mobile.
- Three or four-column grids remaining too dense.
- Tiny text.
- Excessive horizontal padding.
- Buttons side-by-side when they should stack.
- Large decorative elements consuming most of the mobile viewport.

---

## 10. Performance-related UI problems

Look for obvious issues such as:

- Oversized images.
- Unnecessary animations.
- Excessive client-side rendering.
- Repeated expensive operations.
- Components rendering unnecessarily.

Do not recommend architectural performance changes without understanding the current implementation.

---

## 11. Review severity

Classify findings as:

### Critical

Prevents users from completing an important task or creates a severe accessibility/responsive problem.

### High

Significantly harms usability or creates a major visual/interaction problem.

### Medium

Noticeable problem that should be addressed but does not block the user.

### Low

Polish or minor consistency improvement.

Do not invent problems simply to produce a longer review.

---

## 12. Review output

When reporting findings, use:

- Problem.
- Location.
- Why it matters.
- Recommended improvement.
- Severity.

Example:

```text
[High] Mobile navigation

Problem:
The navigation links overflow horizontally on small screens.

Location:
Navbar component.

Why:
Users cannot reliably access all navigation options.

Recommendation:
Use a responsive navigation pattern that changes composition on small screens.
```

---

## 13. Fixing findings

If the user asks to fix the findings:

1. Confirm the relevant files.
2. Make the smallest appropriate change.
3. Preserve existing architecture.
4. Recheck responsive behavior.
5. Recheck accessibility.
6. Verify that the change did not break other components.

Do not redesign unrelated parts of the application.

---

## 14. Final review

Before declaring the frontend complete, verify:

- UX.
- Responsive behavior.
- Accessibility.
- Visual hierarchy.
- Consistency.
- Interaction states.
- Loading/error/empty states.
- Mobile usability.

A successful build does not automatically mean a successful user interface.
