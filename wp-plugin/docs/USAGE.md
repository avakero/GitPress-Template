# Usage Guide

This document covers how to use GitPress Editor day-to-day on desktop and mobile.

## Quick start

1. Visit any page on your site while logged in as Administrator or Editor.
2. Tap the yellow pencil button in the bottom-right corner.
3. Tap elements on the page to add them to the selection queue.
4. Type what you want changed into the instruction box.
5. Tap **Send to AI**.
6. Review the suggestion, tap **Preview**, then **Apply to WordPress**.

## The launcher button

The yellow circular button in the bottom-right is the editor launcher. It appears on every frontend page when you are logged in with editing permissions.

- **Tap**: Opens the editor panel and enables element selection.
- On iPhone with a notch or home indicator, the button automatically avoids the safe area.

If you don't want to see the button on certain pages, you can turn it off entirely in **Settings → GitPress Editor → Floating Button**.

## The editor panel

### Desktop (≥ 1024px)

A right-side drawer slides in from the edge of the screen. It is 380px wide and pushes the page content aside visually via a semi-transparent backdrop.

### Tablet (768–1023px)

Same drawer, slightly narrower (340px).

### Mobile (< 768px)

A bottom sheet slides up from the bottom, covering ~90% of the viewport. Key gestures:

- **Swipe the handle bar down** to close the sheet. If you drag more than a quarter of the sheet's height (or 120px, whichever is smaller), the sheet closes. Otherwise it snaps back.
- **Tap the backdrop** above the sheet to close.
- **Soft keyboard**: When you focus the instruction text area, the sheet automatically shrinks so the footer stays above the keyboard.

## Selecting elements

With the panel open, the editor is in "selection mode":

- **Hover** over any text, image, icon, or link to highlight it with a teal outline.
- **Tap/click** to select — the outline turns orange and the element is added to the queue in the panel.
- **Tap again** to deselect.

### What can be selected?

- Headings (`h1`–`h6`)
- Paragraphs, list items, buttons, links
- Images, Font Awesome icons
- Captions, time stamps

### What cannot be selected?

- Empty decorative containers
- Background-image-only elements
- Content managed by some page builders (see Installation FAQ)

### The queue

The panel shows every selected element with:

- A short preview of its text content
- The HTML tag name
- An `×` button to remove it from the queue

You can select multiple elements and edit them all in one AI request (up to 30 per request).

## The instruction box

Describe what you want changed in plain language. Examples:

- "Change the title to 'About Our Team'"
- "Make this paragraph more friendly and welcoming"
- "Shorten the description to one sentence"
- "Translate this section to English"
- "Rephrase in a more professional tone"

The AI sees the elements you selected plus your instruction, so be specific. If you selected three items but only want one changed, remove the others first.

## AI response

After you tap **Send to AI**, the panel shows a loading spinner (~2–5 seconds), then displays one card per suggested edit:

- **Path** — identifies which element the change applies to
- **×** — removes this single edit and reverts the element's preview
- **After** — the proposed text (green)
- **Reason** — a short rationale from the AI (optional)

The suggestions are **automatically applied to the page** as a live preview (auto-preview). Each changed element shows a green left-border and a small "Preview" label. This does NOT save anything — it is purely visual.

If the AI returned content that doesn't match the expected JSON shape, the raw response is shown instead and you can retry.

## Reviewing edits

- **Remove a single edit**: Tap the **×** button on its card. The element reverts to its original state while other edits remain.
- **Revert all**: Tap **Revert** to undo all previewed changes.
- **Re-preview**: After reverting, tap **Preview** to re-apply the suggestions.
- The preview disappears if you close the panel or tap **Clear**.

## Applying to WordPress

When you are happy with the preview, tap **Apply to WordPress** (orange). You will be asked to confirm — this step writes the change to the database.

- The plugin resolves your current page URL to the WordPress post/page ID automatically.
- It opens the post, finds the `current_content` text, replaces it with `new_content`, and saves.
- WordPress creates a revision, so you can roll back from **Posts → All Posts → (your post) → Revisions** if needed.

### What if the apply fails?

Common causes and fixes:

| Error | Cause | Fix |
|---|---|---|
| No matching text was found | The original text isn't in the post's `post_content` | Re-select and retry; content may be in a page-builder structure we can't reach |
| Permission denied | Your role changed, or nonce expired | Reload the page |
| Too many requests | Hit the per-user rate limit | Wait a minute and retry |
| Post not found | The URL resolution failed | Check that the page has a slug matching the URL |

## Changing text styles (colors, fonts, effects)

As of v0.2.0, the AI can modify element colors, font weight, size, and visual
effects in addition to text content. Examples of instructions that work:

- **Color**: "Make this title red" → `{ style: { color: "#ff0000" } }`
- **Bold**: "Make this bold" → `{ style: { "font-weight": "bold" } }`
- **Size**: "Make this bigger" → `{ style: { "font-size": "3rem" } }`
- **Multiple**: "Make this title red and bold" → `{ style: { color: "#ff0000", "font-weight": "bold" } }`

### Preset effects

For complex visual effects, the AI uses pre-defined CSS classes shipped with
the plugin. These are guaranteed to render correctly across browsers:

| Instruction | Class applied |
|---|---|
| "Make this rainbow" | `gp-text-rainbow` |
| "Use the brand gradient" | `gp-text-gradient-brand` |
| "Add a warm gradient" | `gp-text-gradient-warm` |
| "Highlight with yellow marker" | `gp-text-marker-yellow` |
| "Make this glow" | `gp-text-glow` |
| "Add an outline" | `gp-text-outline` |
| "Make this italic" | `gp-text-italic` |
| "Center align" | `gp-text-center` |
| "Larger size" | `gp-text-lg` / `gp-text-xl` / `gp-text-2xl` / ... |

The edit card in the panel shows which classes will be added or removed.
If the preview looks wrong, tap **Revert**, adjust your instruction, and
retry.

### What CAN'T be changed by the AI

- The element's tag (e.g. `<p>` → `<h2>`)
- Nesting structure or adding new child elements
- Images other than swapping `src`
- Any element without a `data-edit` attribute

## Tips for better AI results

1. **Select specific elements**, not whole sections. The AI works better with focused context.
2. **Be explicit about tone**: "more formal", "friendlier", "shorter", "add emojis", etc.
3. **For translations**, say both the source and target language: "Translate from Japanese to English in a professional tone".
4. **For rewrites**, give the AI constraints: "Keep it under 30 words", "Preserve the call-to-action".
5. **Iterate**: If the first suggestion isn't great, tweak your instruction and send again. The queue stays intact.

## Keyboard shortcuts (desktop)

- **Esc**: Close the panel (same as tapping the × button)
- **Tab**: Move focus between controls
- **Enter** in the instruction box: starts a new line (send button remains click-only to prevent accidents)

## Mobile tips

- **iOS Safari**: The editor handles the dynamic toolbar correctly. Pull down on the handle bar to close, not the top of the sheet.
- **Android Chrome**: The soft keyboard expands the sheet properly. If the footer hides behind the keyboard, tap the backdrop to close and reopen.
- **Landscape mode**: The bottom sheet still works but uses less of the screen. Consider rotating to portrait for longer editing sessions.

## Limitations

- **One post per apply action**: You cannot apply edits from multiple pages in a single request. The editor targets the page you are currently viewing.
- **Text-based replacement**: The engine finds your `current_content` by text matching. If two paragraphs contain identical text, only the first is replaced.
- **Page builder content**: Content managed outside `post_content` (Elementor JSON, ACF fields) is not editable.
- **Rate limits**: 30 AI requests and 20 apply requests per minute per user. This prevents runaway costs on the trial key.

## Where are my changes stored?

All edits are written directly to the target post's `post_content` field via `wp_update_post()`. WordPress automatically creates a revision, so you always have a rollback path.

No separate "edit history" is kept by the plugin — use WordPress revisions for audit trail.

## Getting help

- File an issue at the [GitHub Issues page](https://github.com/avakero/GitPress/issues)
- Check [INSTALL.md](./INSTALL.md) for setup troubleshooting
- Check the [Changelog](../CHANGELOG.md) for version history
