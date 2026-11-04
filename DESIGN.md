---
name: Texas, County by County
description: How all 254 Texas counties voted, 2008 to 2024, as a quiet pastel map.
colors:
  lilac-mist: "#f6f4fb"
  surface-white: "#ffffff"
  hairline: "#e9e5f2"
  lavender: "#ece6fb"
  lavender-2: "#d9cff6"
  lavender-ink: "#4b3f8a"
  focus-violet: "#6a55cc"
  track-violet: "#8473d6"
  plum-ink: "#2a2533"
  plum-ink-2: "#5d5770"
  plum-ink-3: "#6e6882"
  state-outline: "#c9c2dc"
  rep-rose-1: "#f2a0a6"
  rep-rose-2: "#dc4a55"
  rep-rose-3: "#b01e2c"
  dem-blue-1: "#97b8ee"
  dem-blue-2: "#3f75d4"
  dem-blue-3: "#1a4aa3"
  other-sand-1: "#ece6d3"
  other-sand-2: "#ddd2b0"
  other-sand-3: "#c9b98a"
  unreported: "#e8e6ee"
  lib-butter: "#ecd08a"
  grn-mint: "#9fd6b6"
  wri-haze: "#d6d2e0"
  ind-lilac: "#c9b8ec"
typography:
  display:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "2.5rem"
    fontWeight: 300
    lineHeight: 1.05
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 450
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  figure:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 300
    lineHeight: 1.1
    letterSpacing: "-0.02em"
    fontFeature: "\"tnum\" 1"
  title:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"tnum\" 1"
  name:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 500
    lineHeight: 1.3
  label:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
  caption:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
rounded:
  chip: "4px"
  focus: "8px"
  md: "12px"
  lg: "14px"
  card: "16px"
  sheet: "18px"
  float: "20px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "28px"
  3xl: "32px"
  4xl: "36px"
components:
  segmented-track:
    backgroundColor: "{colors.lavender}"
    rounded: "{rounded.pill}"
    padding: "3px"
  segmented-option:
    backgroundColor: "transparent"
    textColor: "{colors.plum-ink-2}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "7px 16px"
  segmented-option-on:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink}"
    rounded: "{rounded.pill}"
  button-pill:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink-2}"
    rounded: "{rounded.pill}"
    padding: "7px 14px"
  icon-button:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink-2}"
    rounded: "{rounded.pill}"
    size: "36px"
  crumb-link:
    textColor: "{colors.lavender-ink}"
    padding: "0"
  won-chip:
    backgroundColor: "{colors.lavender}"
    textColor: "{colors.lavender-ink}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  timeline:
    backgroundColor: "{colors.surface-white}"
    rounded: "{rounded.float}"
    padding: "16px 22px 12px"
  legend:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink-2}"
    rounded: "{rounded.lg}"
    padding: "12px 14px"
  map-tooltip:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink}"
    rounded: "{rounded.md}"
    padding: "10px 14px"
  results-panel:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.plum-ink}"
    padding: "36px 32px 28px"
  peek:
    backgroundColor: "{colors.surface-white}"
    rounded: "{rounded.sheet}"
    padding: "12px 12px 12px 16px"
---

# Design System: Texas, County by County

## Overview

**Creative North Star: "The Quiet Pastel Map"**

Texas in soft rose and powder blue on a pale lilac field, with nothing on screen but the map, the result, and one slim timeline. The map owns the left of the screen; a white results panel holds the answer on the right; a floating pill slider sits along the bottom edge of the map. Everything that is not data is lilac, lavender, white or plum ink, so the party pastels are the only saturated colour you see.

It is calm and sleek rather than a busy election-night dashboard: light weights for big words and numbers, hairline borders, soft wide shadows, generous rounded corners. Density stays low. One answer at a time, written as a plain sentence ("Beto O'Rourke won Travis County by 49.7 points."), with exact counts underneath.

Motion is a single gesture. When the election changes, counties recolour in a soft west-to-east wave; candidate rows re-rank in place; the panel crossfades. All of it honours reduced motion.

**Key Characteristics:**
- Pale lilac-mist ground, white surfaces, plum ink for every text tone (AA on both).
- Party pastels carry data and nothing else; lavender carries selection and state.
- Geist Variable throughout: light for big words and numbers, medium for names, tabular figures for counts.
- Hairline borders plus soft, wide, plum-tinted shadows on floating pieces only.
- Pill and generously rounded shapes; no hard corners on interactive pieces.

## Colors

A pastel field on lilac with one quiet violet accent; colour that means something belongs to the data.

### Primary
- **Focus Violet** (`focus-violet`): the single interactive accent. Focus rings (2px, 3px offset), slider thumb border, text caret. Passes non-text contrast on white and on the ground.
- **Track Violet** (`track-violet`): the filled part of the timeline track only. At 3:1 or better for non-text contrast (3.9:1 on white, 3.2:1 against the unfilled lavender track).

### Secondary
- **Lavender** (`lavender`): selection and state surfaces: the segmented-control track, the unfilled slider track, the "Won" chip.
- **Lavender 2** (`lavender-2`): text selection highlight and scrollbar thumbs.
- **Lavender Ink** (`lavender-ink`): text that belongs to the selection layer: the "All of Texas" crumb, the "Won" chip label, the race-switch notice, "See full results" in the peek.

### Data (party fabric)
- **Republican Rose** (`rep-rose-1` / `-2` / `-3`) and **Democrat Powder Blue** (`dem-blue-1` / `-2` / `-3`): three margin steps each, for <10, 10–30 and 30+ points. Step 3 also fills candidate bars, swatches and the counties-won bar.
- **Other Sand** (`other-sand-1` / `-2` / `-3`): any county carried by a minor party, same three steps.
- **Unreported** (`unreported`): counties with no votes.
- **Minor-party swatches**: Libertarian butter (`lib-butter`), Green mint (`grn-mint`), Write-in haze (`wri-haze`), Independent lilac (`ind-lilac`), used for candidate bars and dots only.

### Neutral
- **Lilac Mist** (`lilac-mist`): page ground, map stage, empty bar track, icon-button hover.
- **Surface White** (`surface-white`): results panel, every floating card (legend, timeline, tooltip, peek, map controls), and the white seams between counties on the map.
- **Hairline** (`hairline`): every 1px border and divider.
- **State Outline** (`state-outline`): the Texas outline around the map.
- **Plum Ink** (`plum-ink`), **Plum Ink 2** (`plum-ink-2`), **Plum Ink 3** (`plum-ink-3`): primary, secondary and tertiary text. Every tone passes AA on the ground and on white: 13.6:1, 6.3:1 and 4.85:1 on the ground. Plum Ink also draws the map's hover and selection outlines.

### Named Rules
**The Data-Only Pastel Rule.** Rose, powder blue, sand, butter, mint and haze mean a party and nothing else. Never use them for buttons, states, headings or decoration. Interface state is lavender and violet.

**The Text-Carries-Precision Rule.** Neighbouring margin steps are about 1.7–2.2:1 apart (darkened on owner request), so shade reads the margin band, but only roughly; the exact margin and vote counts are always available as text (panel, tooltip, peek). Any new surface that uses the shade steps must also give the exact number in text.

**The Plum-Only Text Rule.** All text uses the three plum ink tones or lavender ink. No grey, no pure black, no coloured text drawn from the party pastels.

## Typography

**Display Font:** Geist Variable (with Geist, system-ui, sans-serif)
**Body Font:** Geist Variable (same family)

**Character:** One modern grotesque, with weight doing the work: big words and percentages are set thin (300), names medium (500), the header title semibold (600). Tabular figures are on by default (`"tnum" 1` on body) so counts line up, and switched off in the header, subtitles and year ticks where the numbers are read, not compared.

### Hierarchy
- **Display** (300, 2.5rem, 1.05, -0.035em; 1.875rem at 960px and below): the place name heading the results panel ("Texas", "Travis County").
- **Headline** (450, 1.5rem, 1.3, -0.02em, `text-wrap: pretty`): the one-sentence answer under the heading.
- **Figure** (300, 1.5rem, 1.1, -0.02em, tabular): candidate percentages.
- **Title** (600, 1.125rem, -0.02em): the site title in the header.
- **Body** (400, 15px, 1.5, tabular): base text.
- **Name** (500, 0.9375rem, 1.3): candidate names; tooltip county names (600, 0.875rem).
- **Label** (500, 0.875rem): segmented-control options; 0.8125rem for map buttons, crumb, notice.
- **Caption** (400, 0.75rem down to 0.6875rem, plum ink 3): vote counts, legend, year ticks, source note.

### Named Rules
**The Light-Numbers Rule.** Big numbers are set light (300) and large, never bold. Weight goes up only as size goes down.

**The Subtitle-Below Rule.** Context for a heading sits under it, never above it. The race and year ("U.S. Senate · 2018") follow the h2 as a subtitle; the only thing that may sit above the heading is the "All of Texas" back link, which is navigation, not a label. No eyebrows or kickers.

## Layout

A two-column app shell that fills the viewport: a thin header (title and subtitle on the left, race switch on the right, 20px 28px padding, hairline below), then a grid of the map stage (`minmax(0, 1fr)`) and a fixed 400px white results panel with a hairline on its left. The panel scrolls on its own; its contents stack with a 32px gap, the answer block with 20px, candidate rows with 18px. The source note is pushed to the panel's bottom.

The map floats its tools: the legend top-left (20px inset), zoom controls top-right, a "Show all of Texas" pill when the view has moved, and the timeline centred 24px from the bottom, `min(620px, 100% - 48px)` wide.

At 960px and below the shell becomes one column: header (race switch goes full width, options share it evenly), the map at 62svh (at least 420px), then the results. Floating pieces tighten to 12px insets. When a county is selected and the panel is off-screen, a fixed peek bar sits 12px above the bottom safe area.

Spacing follows a loose 4px grid; the steps actually used are 4, 8, 12, 16, 20, 28, 32 and 36px.

## Elevation & Depth

A hybrid: the page itself is flat (ground, panel and header are separated by hairlines and tone, not shadow), and only things that float over the map get a soft, wide, plum-tinted shadow. Shadows are ambient, never hard or offset.

### Shadow Vocabulary
- **Soft** (`box-shadow: 0 1px 2px rgba(42,37,51,.04), 0 8px 24px rgba(42,37,51,.06)`): resting floating pieces: legend, map controls, the reset pill, the error card.
- **Lift** (`box-shadow: 0 2px 6px rgba(42,37,51,.06), 0 16px 40px rgba(42,37,51,.1)`): pieces that carry the answer or the main control: timeline, tooltip, mobile peek.
- **Toggle** (`box-shadow: 0 1px 3px rgba(42,37,51,.1)`): the selected option in the segmented control.

### Named Rules
**The Float-Only Shadow Rule.** A shadow means "this sits on top of the map." Panels and the header in the layout stay flat with hairlines.

## Shapes

Rounded and soft. Interactive controls are pills (999px): segmented control, reset button, icon button, chip, bars and the slider track. Floating cards get large radii that grow with their size: 12px for the tooltip and zoom controls, 14px for the legend, 16px for the error card, 18px for the peek, 20px for the timeline. Legend swatches are 4px; party dots are 8px circles. Borders are always a single 1px hairline.

On the map, counties are separated by white seams that thicken with zoom (0.6px to 1.4px), and Texas is outlined in state-outline lilac (1px to 2px, round joins).

## Components

### Segmented race switch
Quiet and tactile.
- **Shape:** lavender pill track with 3px padding and 2px between options.
- **Option:** plum ink 2 label on transparent; hover goes to plum ink.
- **On:** a white pill with plum ink text and the toggle shadow; colour and shadow ease over 0.25s.
- **Unavailable:** plum ink 3 at 55% opacity, not clickable; tapping it shows a lavender-ink notice under the switch ("No Governor race in 2008.") through a live region.

### Buttons
- **Pill button** ("Show all of Texas"): white, hairline border, soft shadow, plum ink 2, 0.8125rem/500, 7px 14px.
- **Icon button** (close the peek): 36px white circle with a hairline, plum ink 2; hover goes to plum ink on the lilac ground. Icons are Lucide SVG strokes.
- **Text link** (crumb, "show write-ins"): no chrome. The crumb is lavender ink with a back arrow and underlines on hover; the write-in toggle is plum ink 3 with a chevron that rotates 180 degrees.
- **Focus:** every control gets a 2px focus-violet outline, 3px offset, 8px radius. The map canvas uses an inset outline.

### Timeline slider
The signature control: a floating white card (20px radius, lift shadow) holding a native range input that snaps to election years.
- **Track:** 4px pill; filled in track violet up to the thumb, lavender after it.
- **Thumb:** 18px white circle with a 2px focus-violet border and a small shadow; it scales to 1.12 while dragged; keyboard focus adds a white-then-violet double ring.
- **Ticks:** year labels in caption size, plum ink 3, clickable; the current year is plum ink at 600.

### Results panel
- **Heading block:** optional lavender-ink crumb, display-size place name, plum ink 3 subtitle under it.
- **Answer:** headline-size sentence naming the winner and margin.
- **Candidate row:** name (500) with party dot and party name below; light percentage and vote count right-aligned; a 4px party-colour bar spanning the row on the lilac track. The winner gets a lavender "Won" chip (0.6875rem/600).
- **Counties-won bar:** an 8px split pill in rose step 3 and blue step 3 with a 3px gap, counts in plum ink at 600 beneath.

### Legend
A white card (14px radius, soft shadow) with a 3×2 grid of 36px swatches, Rep. and Dem. by the three margin steps, step labels in caption size, and the caption "Margin of victory, points".

### Map selection and tooltip
- **Hover:** a 1.4px plum-ink outline on the county.
- **Selection:** a 2.2px plum-ink outline over a 5px white backing, so it reads on every pastel.
- **Tooltip:** white card, 12px radius, lift shadow, county name at 600 with winner, party dot and margin.
- **Keyboard:** arrow keys step through counties alphabetically, Escape returns to all of Texas.

### Mobile peek
Fixed white sheet (18px radius, lift shadow) that slides up when a county is tapped and the panel is off-screen: county name at 600, winner and margin with a party dot, "See full results" in lavender ink, and a close icon button. It hides once the panel scrolls into view.

### Motion
- **Recolour wave:** counties recolour west to east by longitude over 700ms with an ease-out cubic; with reduced motion they recolour at once.
- **Rows:** candidate rows keep identity by party and re-rank in place (layout animation, 0.35s); bars scale over 0.6s.
- **Panel:** content crossfades with a 6px rise (0.28s).
- **Shared easing:** `cubic-bezier(0.22, 1, 0.36, 1)`.
- **Reduced motion:** Motion runs with `reducedMotion="user"`, CSS transitions collapse to 0.01ms, and the wave, map fly-to and scroll-into-view all skip their animation.

## Do's and Don'ts

### Do:
- **Do** keep every text tone to plum ink, plum ink 2, plum ink 3 or lavender ink, so all text passes AA on the lilac ground and on white.
- **Do** use focus violet for focus rings and the slider thumb, and track violet only for the filled track, kept at 3:1 or better for non-text contrast.
- **Do** pair every margin shade with the exact margin in text somewhere on the same path (panel, tooltip or peek).
- **Do** set large numbers light (300) with tabular figures, and keep names at 500.
- **Do** put a heading's context under it as a subtitle.
- **Do** keep shadows on floating pieces only, using the soft and lift values.
- **Do** make sure every new animation respects reduced motion, through Motion's `reducedMotion="user"` or the CSS override.

### Don't:
- **Don't** use party pastels for anything but party data: no rose or blue buttons, states, headings or decorative fills.
- **Don't** put eyebrows or kickers above headings.
- **Don't** add dashboard chrome (stat tiles, dense tables, extra toolbars) around the map; one answer at a time.
- **Don't** use hard or offset shadows, or heavy borders; 1px hairlines only.
- **Don't** add a second accent hue; interface state is lavender and violet.
- **Don't** add motion beyond the wave, the in-place re-rank, the panel crossfade and the small state transitions.
