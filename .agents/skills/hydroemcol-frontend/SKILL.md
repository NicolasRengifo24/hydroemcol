---
name: hidroemcol-frontend
description: Use when designing or implementing the Hidroemcol frontend, including pages, components, navigation, service presentation, catalog interfaces, contact flows, responsive layouts, UX and visual design decisions.
---

# Hidroemcol Frontend

## Purpose

This skill defines frontend design and UX rules specific to the Hidroemcol project.

It complements the project's general design skills and the instructions defined in AGENTS.md.

The project context is documented in:

`CONTEXTO_MAESTRO.md`

Before making important frontend decisions, consult the project context.

---

## Business context

Hidroemcol is an industrial company focused on hydraulic and electrohydraulic solutions.

Its services include:

- Supply of hydraulic and electrohydraulic spare parts.
- Importation of components on request.
- Electrical services for hydraulic control systems.
- Proportional control systems.
- Motion and speed control.
- Custom electrohydraulic system design and implementation.
- Hydraulic technical services.
- Hydraulic component testing.
- Testing through a hydraulic test bench.
- Diagnosis and testing of cylinders.
- Pumps.
- Hydraulic motors.
- Orbitrols.
- Controls.
- Valves.
- Other hydraulic and electrohydraulic components.

The website must communicate technical capability and trust rather than behave like a generic technology startup website.

---

## Primary website objectives

The website should allow a visitor to:

1. Understand what Hidroemcol does quickly.
2. Discover its services.
3. Explore available spare parts and components.
4. Understand the company's technical capabilities.
5. Request information or a quotation.
6. Contact the company easily.
7. Understand the technical service process.
8. Navigate comfortably from mobile devices.

---

## Target users

The interface should consider users such as:

- Industrial companies.
- Maintenance personnel.
- Mechanical technicians.
- Hydraulic technicians.
- Electrical technicians.
- Engineers.
- Purchasing personnel.
- Workshop personnel.
- Companies looking for hydraulic components.
- Companies requiring technical hydraulic or electrohydraulic services.

Users may have different levels of technical knowledge.

The interface must therefore remain technically credible without becoming unnecessarily difficult to understand.

---

## UX principles

Prioritize:

- Clear navigation.
- Strong visual hierarchy.
- Short and understandable content blocks.
- Clear calls to action.
- Easy access to contact options.
- Easy service discovery.
- Clear separation between products and services.
- Consistent terminology.
- Predictable interactions.
- Useful feedback after user actions.

Do not make users search unnecessarily for:

- What Hidroemcol does.
- What services are available.
- How to request information.
- How to contact the company.

---

## Responsive design

All frontend interfaces must work correctly on:

- Mobile.
- Tablet.
- Laptop.
- Desktop.

Use a mobile-first approach.

Do not design exclusively for desktop and then attempt to fix the layout afterward.

Avoid:

- Horizontal overflow.
- Fixed widths that break small screens.
- Text becoming unreadably small.
- Buttons too small for touch interaction.
- Navigation elements that become unusable on mobile.
- Images that distort or overflow their containers.

---

## Visual direction

The visual language should communicate:

- Industrial expertise.
- Technical precision.
- Reliability.
- Professionalism.
- Engineering.
- Hydraulic technology.
- Electrohydraulic technology.

Avoid making the website look like:

- A generic SaaS application.
- A cryptocurrency website.
- A gaming website.
- A generic AI startup.
- An unrelated ecommerce template.

The visual design should be modern without losing its industrial identity.

---

## Components

Prefer reusable React components.

Examples include:

- Navbar.
- Footer.
- Hero sections.
- Service cards.
- Product cards.
- Category cards.
- Contact sections.
- Quote/request forms.
- Buttons.
- Inputs.
- Modals.
- Status indicators.
- Loading states.
- Empty states.
- Error states.

Do not duplicate large blocks of JSX when a reusable component would improve maintainability.

---

## Content hierarchy

Important information should be immediately visible.

For service pages, prioritize:

1. Service name.
2. What the service solves.
3. Short explanation.
4. Main technical capabilities.
5. Relevant components or systems.
6. Call to action.
7. Contact/request mechanism.

Do not overwhelm the first screen with technical specifications.

Technical details can be progressively disclosed.

---

## Calls to action

Calls to action should have a clear purpose.

Examples:

- Solicitar cotización.
- Consultar disponibilidad.
- Solicitar diagnóstico.
- Agendar servicio.
- Consultar un repuesto.
- Hablar con un asesor.

Avoid excessive competing primary buttons.

---

## Accessibility

Use:

- Semantic HTML.
- Proper heading hierarchy.
- Labels for form controls.
- Keyboard-accessible interactions.
- Sufficient contrast.
- Descriptive button text.
- Meaningful alternative text for relevant images.
- Visible focus states.

Do not use visual styling as the only way to communicate important information.

---

## Loading, empty and error states

Interfaces that communicate with the backend must account for:

- Loading.
- Successful response.
- Empty result.
- Error.
- Retry where appropriate.

Do not leave users staring at a blank screen while data is loading.

---

## React principles

Use the existing React architecture defined by the project.

Prefer:

- TypeScript.
- Reusable components.
- Clear component responsibilities.
- Existing services/API clients.
- Existing state-management patterns.
- Existing routing patterns.

Do not introduce a new state-management library or replace an existing architectural pattern without discussing it first.

---

## Design verification

After implementing a significant frontend change, inspect the result for:

- Responsive behavior.
- Alignment.
- Spacing.
- Typography.
- Visual hierarchy.
- Interactive states.
- Accessibility.
- Overflow.
- Consistency with the rest of the application.

Fix problems discovered during review instead of assuming that successful compilation means the UI is finished.

---

## Important restriction

This skill does not authorize changes to:

- Database architecture.
- Backend architecture.
- API contracts.
- Authentication architecture.
- Core business rules.

If frontend implementation reveals that one of these needs to change, explain the issue and ask the user before making the architectural change.
