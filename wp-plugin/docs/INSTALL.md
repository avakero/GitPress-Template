# Installation Guide

This document walks through installing GitPress Editor on a WordPress site.

## Prerequisites

- WordPress **5.6** or later
- PHP **7.4** or later with the `DOM` extension enabled (bundled with virtually all PHP builds)
- `https://` recommended (required for `visualViewport` mobile keyboard handling)
- A WordPress user account with the **Administrator** or **Editor** role
- **Pages must contain `data-edit` attributes on the elements you want to edit.**
  Sites built with the `website-builder` skill from the GitPress repository already
  have these attributes automatically. Existing third-party WordPress sites are
  NOT supported out of the box — they would need to be re-built or manually
  annotated with `data-edit` attributes. The plugin ships with a baseline manifest
  for the reference `pixelcraft` site, and sites with a different structure can
  drop their own manifests into `wp-content/uploads/gitpress-manifests/` to get
  curated editing rules (see "Site-specific manifests" below).

## Step 1: Download the plugin

Go to the [GitHub Releases page](https://github.com/avakero/GitPress/releases) and download the latest `gitpress-editor-<version>.zip` file.

## Step 2: Upload to WordPress

1. Log in to your WordPress admin dashboard.
2. Navigate to **Plugins → Add New**.
3. Click **Upload Plugin** at the top of the page.
4. Click **Choose File** and select the downloaded zip.
5. Click **Install Now**.
6. After installation completes, click **Activate Plugin**.

## Step 3: Configure settings

Go to **Settings → GitPress Editor**.

### 3-1. Gemini API key (optional)

The plugin ships with a low-quota trial key for evaluation. For production use, we strongly recommend entering your own key:

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and sign in with a Google account.
2. Click **Create API Key** and copy the generated key.
3. In WordPress, paste the key into the **Your Gemini API Key** field.
4. Click **Save Changes**.

The key is stored encrypted with AES-256-GCM using a per-site secret derived from WordPress salts. It is never sent to the browser.

### 3-2. Enabled roles

By default, **Administrator** and **Editor** roles see the floating editor button. You can enable **Author** and **Contributor** as well from the checkboxes in the settings page.

> Note: Users still need the `edit_pages` or `edit_posts` capability (which is implicit in Editor and above).

### 3-3. Floating button

You can toggle the launcher button on/off site-wide. Turning it off effectively disables the frontend editor without deactivating the plugin.

### 3-4. Model selection

Choose between:

- **gemini-2.0-flash** — fastest, lowest cost, default
- **gemini-2.5-flash** — better quality, slightly slower
- **gemini-2.5-pro** — highest quality, significantly slower and more expensive

## Step 4: Verify

1. Log out of WordPress admin and log back in.
2. Visit any page on the frontend of your site (not wp-admin).
3. You should see a yellow pencil button in the bottom-right corner.
4. Tap it — the editor panel should slide in.

If you don't see the button:

- Confirm you are logged in as Administrator or Editor
- Check Settings → GitPress Editor → Floating Button is enabled
- Check browser console for any JavaScript errors

## Step 5: Test the editing flow

1. Open a post or page where you have some text content (e.g. "About Us").
2. Tap the editor button to open the panel.
3. Tap a paragraph on the page — it should gain a teal outline and appear in the selection queue.
4. Type a change instruction like "Make this friendlier" into the text area.
5. Tap **Send to AI** (yellow button).
6. After a few seconds, an edit card appears showing before → after.
7. Tap **Preview** to see the change on the page.
8. Tap **Apply to WordPress** (orange button) and confirm.
9. Reload the page — your change should be live.

## Uninstall

**Plugins → Installed Plugins → GitPress Editor → Deactivate → Delete**

Deleting the plugin removes the stored options, including the encrypted API key.

## Troubleshooting

### "Permission denied"

Your user role is not in the enabled roles list, or you lack the `edit_pages` capability. Ask an administrator to enable your role in Settings → GitPress Editor.

### "Session expired. Please reload the page."

Your WordPress nonce has expired (typically after 24 hours). Reload the page and try again.

### "Too many requests"

You've hit the per-user rate limit (30 AI calls or 20 apply calls per minute). Wait a minute and retry.

### "Gemini rejected the API key"

Your API key is invalid, expired, or from a disabled Google Cloud project. Re-generate one at AI Studio and paste it into the settings.

### "No matching text was found"

The AI returned content that doesn't match the original text on the page, usually because:
- The original text has since been edited elsewhere
- The AI truncated or paraphrased the `current_content` field

Try sending fewer elements per request, or re-select and retry.

### The button doesn't appear on mobile Safari

Make sure your site uses HTTPS. Some browser security policies require it for `visualViewport` and safe-area-inset features.

### Changes don't show after applying

Your site is likely using a caching plugin. Clear the cache, or try again after the TTL expires.

## Site-specific manifests

The plugin resolves editing rules (allowed CSS properties, allowed classes, element type)
by looking up each `data-edit` path in a manifest. Two manifest layers are merged at
runtime, with later layers overriding earlier ones on key collision:

1. **Bundled baseline** — `manifests/*.json` inside the plugin zip, built from
   `config/editables/*.yaml`. Tuned for the reference `pixelcraft` site.
2. **Site-specific overrides** — JSON files you drop into
   `wp-content/uploads/gitpress-manifests/` on your WordPress host.

If your site was generated by the `website-builder` skill (or any tool that produces
`data-edit`-annotated HTML with a matching set of YAML manifests), you can register
those manifests with a two-step process:

### Generate the manifest (once per site)

From the repo root:

```bash
python scripts/generate_manifest.py --html-dir path/to/your-site
```

This scans every HTML file for `data-edit` attributes and writes one YAML file per
page into `path/to/your-site/editables/`. The YAML format matches `config/editables/*.yaml`.

Verify integrity:

```bash
python scripts/validate_editables.py --html-dir path/to/your-site --yaml-dir path/to/your-site/editables
```

### Deploy to WordPress

Convert each YAML to JSON (use any YAML→JSON tool, e.g. `python -c "import yaml,json,sys; print(json.dumps(yaml.safe_load(open(sys.argv[1])), ensure_ascii=False, indent=2))" page.yaml > page.json`)
and upload the resulting `*.json` files to:

```
wp-content/uploads/gitpress-manifests/
```

The plugin picks them up automatically on the next page load (or within 15 minutes if a
previous manifest was cached). To force a refresh, save the GitPress Editor settings
page once — this flushes the manifest cache.

To relocate the directory, add a PHP filter in your theme's `functions.php`:

```php
add_filter( 'gitpress_editor_site_manifests_dir', function () {
    return ABSPATH . 'wp-content/my-custom-manifests';
} );
```

Return an empty string to disable site-specific loading entirely.

## Next steps

See [USAGE.md](./USAGE.md) for the full user guide including mobile gestures and AI prompting tips.
