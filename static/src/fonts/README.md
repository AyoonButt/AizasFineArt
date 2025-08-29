# Custom Fonts for Aiza's Fine Art

This directory contains the custom fonts for the website redesign.

## Required Font Files

### Nadeko (Logo Font)
- **Source**: https://www.fontspace.com/nadeko-font-f121998
- **Usage**: Brand name "Aiza's Fine Art"
- **Files needed**:
  - Nadeko-Regular.woff2
  - Nadeko-Regular.woff
  - Nadeko-Regular.ttf

### Colton (Header Font)  
- **Source**: https://www.fontspace.com/colton-font-f5832
- **Usage**: Page titles, section headings, artwork titles
- **Files needed**:
  - Colton-Regular.woff2
  - Colton-Regular.woff
  - Colton-Regular.ttf

### Baar Sophia (Decorative Font)
- **Source**: https://www.fontspace.com/baar-sophia-font-f2019
- **Usage**: Special accents, quotes, decorative text
- **Files needed**:
  - BaarSophia-Regular.woff2
  - BaarSophia-Regular.woff
  - BaarSophia-Regular.ttf

## Installation Instructions

1. Download the fonts from their respective sources
2. Convert to web formats (woff2, woff) if needed
3. Place font files in this directory
4. The CSS @font-face declarations are already set up in `/static/src/css/design-system.css`

## Fallbacks

The design system includes fallback fonts:
- Nadeko → serif
- Colton → serif  
- Baar Sophia → serif
- Karla (Google Fonts) → sans-serif