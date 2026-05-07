# Chapter 9: Forms & Inputs — The Settings Page

[← Chapter 8: Animations](chapter-08-animations.md) | [Chapter 10: Dynamic Classes →](chapter-10-dynamic-classes.md)

---

## The Task

Sora: "The settings page has text inputs, textareas, selects, checkboxes, radio buttons, toggles, and file uploads. They all need to look consistent, show validation states, and be accessible. Here's the Figma."

---

## Base Input Style

Every text input in Pixelflow follows the same pattern:

```tsx
function Input({ label, id, error, ...props }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
      </label>
      <input
        id={id}
        className={`
          w-full px-3 py-2 rounded-lg border text-sm
          bg-white dark:bg-gray-800
          text-gray-900 dark:text-white
          placeholder-gray-400 dark:placeholder-gray-500
          transition-colors
          focus:outline-none focus:ring-2 focus:ring-offset-0
          ${error
            ? 'border-red-500 focus:ring-red-500/20'
            : 'border-gray-300 dark:border-gray-700 focus:border-brand-500 focus:ring-brand-500/20'
          }
        `}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}
```

The anatomy:
- `w-full` → full width of container
- `px-3 py-2` → comfortable click target
- `rounded-lg border` → visible boundary
- `focus:ring-2 focus:ring-brand-500/20` → colored glow on focus
- `focus:border-brand-500` → border color changes on focus
- Error state swaps brand colors for red

---

## Textarea

```tsx
function Textarea({ label, id, error, rows = 4, ...props }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
      </label>
      <textarea
        id={id}
        rows={rows}
        className={`
          w-full px-3 py-2 rounded-lg border text-sm resize-y
          bg-white dark:bg-gray-800
          text-gray-900 dark:text-white
          placeholder-gray-400 dark:placeholder-gray-500
          transition-colors
          focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500
          ${error ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-300 dark:border-gray-700'}
        `}
        {...props}
      />
      {error && <p className="mt-1.5 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
```

`resize-y` allows vertical resizing only. Use `resize-none` to disable resizing entirely.

---

## Select

```tsx
function Select({ label, id, options, error, ...props }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
      </label>
      <select
        id={id}
        className={`
          w-full px-3 py-2 rounded-lg border text-sm appearance-none
          bg-white dark:bg-gray-800
          text-gray-900 dark:text-white
          transition-colors cursor-pointer
          focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500
          ${error ? 'border-red-500' : 'border-gray-300 dark:border-gray-700'}
          bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2020%2020%22%20fill%3D%22%236b7280%22%3E%3Cpath%20fill-rule%3D%22evenodd%22%20d%3D%22M5.23%207.21a.75.75%200%20011.06.02L10%2011.168l3.71-3.938a.75.75%200%20111.08%201.04l-4.25%204.5a.75.75%200%2001-1.08%200l-4.25-4.5a.75.75%200%2001.02-1.06z%22%2F%3E%3C%2Fsvg%3E')]
          bg-[length:20px] bg-[position:right_8px_center] bg-no-repeat pr-10
        `}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}
```

`appearance-none` removes the browser's default dropdown arrow so we can add our own with a background SVG.

---

## Checkbox & Radio

```tsx
function Checkbox({ label, id, ...props }) {
  return (
    <label htmlFor={id} className="flex items-center gap-3 cursor-pointer group">
      <input
        type="checkbox"
        id={id}
        className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-brand-600 focus:ring-brand-500 focus:ring-offset-0 dark:bg-gray-800 cursor-pointer"
        {...props}
      />
      <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
        {label}
      </span>
    </label>
  );
}

function Radio({ label, id, name, ...props }) {
  return (
    <label htmlFor={id} className="flex items-center gap-3 cursor-pointer group">
      <input
        type="radio"
        id={id}
        name={name}
        className="w-4 h-4 border-gray-300 dark:border-gray-600 text-brand-600 focus:ring-brand-500 focus:ring-offset-0 dark:bg-gray-800 cursor-pointer"
        {...props}
      />
      <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
        {label}
      </span>
    </label>
  );
}
```

Tailwind styles native checkboxes and radios with `text-brand-600` (the checked color) and `focus:ring-brand-500`.

---

## Toggle Switch

A custom toggle built with Tailwind:

```tsx
function Toggle({ label, id, checked, onChange }) {
  return (
    <label htmlFor={id} className="flex items-center gap-3 cursor-pointer">
      <button
        id={id}
        role="switch"
        aria-checked={checked}
        onClick={onChange}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2
          ${checked ? 'bg-brand-600' : 'bg-gray-200 dark:bg-gray-700'}
        `}
      >
        <span
          className={`
            inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
    </label>
  );
}
```

The trick: a rounded-full container with a circle inside that slides via `translate-x`.

---

## Form Layout

```tsx
function SettingsForm() {
  return (
    <form className="max-w-2xl space-y-6">
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Profile Settings
        </h2>

        <div className="space-y-4">
          {/* Two columns on desktop */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="First name" id="firstName" placeholder="Jane" />
            <Input label="Last name" id="lastName" placeholder="Doe" />
          </div>

          <Input label="Email" id="email" type="email" placeholder="jane@pixelflow.io" />
          <Textarea label="Bio" id="bio" placeholder="Tell us about yourself..." rows={3} />

          <Select
            label="Timezone"
            id="timezone"
            options={[
              { value: "utc", label: "UTC" },
              { value: "est", label: "Eastern Time" },
              { value: "pst", label: "Pacific Time" },
            ]}
          />
        </div>
      </div>

      {/* Notification preferences */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Notifications
        </h2>

        <div className="space-y-4">
          <Toggle label="Email notifications" id="emailNotifs" checked={true} />
          <Toggle label="Push notifications" id="pushNotifs" checked={false} />
          <Toggle label="Weekly digest" id="digest" checked={true} />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <button type="button" className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
          Cancel
        </button>
        <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors">
          Save Changes
        </button>
      </div>
    </form>
  );
}
```

---

## Validation States

```html
<!-- Default -->
<input class="border-gray-300 focus:border-brand-500 focus:ring-brand-500/20" />

<!-- Error -->
<input class="border-red-500 focus:border-red-500 focus:ring-red-500/20" />

<!-- Success -->
<input class="border-green-500 focus:border-green-500 focus:ring-green-500/20" />

<!-- Disabled -->
<input class="border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed" disabled />
```

With helper text:

```tsx
function InputWithValidation({ label, id, error, success, hint, ...props }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
      </label>
      <input id={id} className="..." {...props} />
      {hint && !error && !success && (
        <p className="mt-1.5 text-sm text-gray-500">{hint}</p>
      )}
      {error && (
        <p className="mt-1.5 text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
          <span>⚠</span> {error}
        </p>
      )}
      {success && (
        <p className="mt-1.5 text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
          <span>✓</span> {success}
        </p>
      )}
    </div>
  );
}
```

---

## File Upload

```tsx
function FileUpload({ label, accept }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
      </label>
      <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg cursor-pointer hover:border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/20 transition-colors">
        <div className="flex flex-col items-center">
          <span className="text-2xl mb-1">📁</span>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Click to upload or drag and drop
          </span>
          <span className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            PNG, JPG up to 10MB
          </span>
        </div>
        <input type="file" className="hidden" accept={accept} />
      </label>
    </div>
  );
}
```

`border-dashed` + hover color change creates the standard upload zone pattern.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Text input base                 │ w-full px-3 py-2 rounded-lg border text-sm
Focus state                     │ focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500
Error state                     │ border-red-500 focus:ring-red-500/20
Disabled                        │ bg-gray-50 text-gray-400 cursor-not-allowed
Remove native appearance        │ appearance-none
Toggle track                    │ h-6 w-11 rounded-full
Toggle knob                     │ h-4 w-4 rounded-full translate-x-{n}
Checkbox/radio color            │ text-brand-600 focus:ring-brand-500
Form spacing                    │ space-y-4 (between fields)
Two-column fields               │ grid grid-cols-1 sm:grid-cols-2 gap-4
Upload zone                     │ border-2 border-dashed hover:border-brand-500
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The forms look great. But I'm seeing a lot of repeated class strings. The button styles are copy-pasted in 12 places. If I change the border radius, you have to update all of them. We need a system for managing this."

Dynamic classes, class variance authority (CVA), and conditional styling.

---

[← Chapter 8: Animations](chapter-08-animations.md) | [Chapter 10: Dynamic Classes →](chapter-10-dynamic-classes.md)
