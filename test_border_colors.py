#!/usr/bin/env python3
"""
Playwright test to check watercolor border colors across all pages
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_border_colors():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        # Test pages and their expected borders
        pages_to_test = [
            {
                'name': 'Home',
                'url': 'http://localhost:8000/',
                'borders': [
                    '.bg-mist-blue.section-border-top.section-border-secondary',
                    '.bg-gradient-about.section-border-top.section-border-primary', 
                    '.bg-pale-blush.section-border-top.section-border-accent',
                    '.bg-gradient-hero.section-border-top.section-border-muted',
                    '.bg-deep-ash.section-border-top.section-border-secondary'
                ]
            },
            {
                'name': 'Gallery',
                'url': 'http://localhost:8000/gallery/',
                'borders': [
                    '.bg-surface.section-border-top.section-border-primary',
                    '.bg-mist-blue.section-border-top.section-border-secondary'
                ]
            },
            {
                'name': 'Shop',
                'url': 'http://localhost:8000/shop/',
                'borders': [
                    '.bg-surface.section-border-top.section-border-primary',
                    '.bg-gradient-about.section-border-top.section-border-secondary',
                    '.bg-gradient-hero.section-border-top.section-border-accent'
                ]
            },
            {
                'name': 'About',
                'url': 'http://localhost:8000/about/',
                'borders': [
                    '.bg-pale-blush.section-border-top.section-border-primary',
                    '.bg-gradient-hero.section-border-top.section-border-secondary',
                    '.bg-vintage-rosewood.section-border-top.section-border-muted',
                    '.bg-gradient-contact.section-border-top.section-border-accent'
                ]
            },
            {
                'name': 'Contact',
                'url': 'http://localhost:8000/contact/',
                'borders': [
                    '.bg-surface.section-border-top.section-border-primary',
                    '.bg-gradient-hero.section-border-top.section-border-secondary',
                    '.bg-black.section-border-top.section-border-accent'
                ]
            }
        ]
        
        results = []
        
        for page_info in pages_to_test:
            print(f"\n=== Testing {page_info['name']} Page ===")
            
            try:
                # Navigate to page
                await page.goto(page_info['url'], wait_until='networkidle')
                await page.wait_for_timeout(2000)  # Wait for CSS to load
                
                page_results = {
                    'page': page_info['name'],
                    'url': page_info['url'],
                    'borders': []
                }
                
                # Check each border
                for border_selector in page_info['borders']:
                    print(f"  Checking border: {border_selector}")
                    
                    # Check if element exists
                    element = page.locator(border_selector)
                    count = await element.count()
                    
                    if count == 0:
                        print(f"    ❌ Element not found")
                        page_results['borders'].append({
                            'selector': border_selector,
                            'found': False,
                            'error': 'Element not found'
                        })
                        continue
                    
                    # Check ::before pseudo-element color
                    try:
                        color = await page.evaluate(f"""
                            () => {{
                                const element = document.querySelector('{border_selector}');
                                if (!element) return 'Element not found';
                                
                                const beforeStyles = window.getComputedStyle(element, '::before');
                                return {{
                                    color: beforeStyles.color,
                                    backgroundImage: beforeStyles.backgroundImage,
                                    display: beforeStyles.display,
                                    content: beforeStyles.content
                                }};
                            }}
                        """)
                        
                        print(f"    ✅ Found - Color: {color['color']}")
                        print(f"    Background: {color['backgroundImage'][:50]}...")
                        print(f"    Display: {color['display']}, Content: {color['content']}")
                        
                        page_results['borders'].append({
                            'selector': border_selector,
                            'found': True,
                            'styles': color
                        })
                        
                    except Exception as e:
                        print(f"    ❌ Error getting styles: {e}")
                        page_results['borders'].append({
                            'selector': border_selector,
                            'found': True,
                            'error': f'Style error: {e}'
                        })
                
                results.append(page_results)
                
            except Exception as e:
                print(f"❌ Error loading {page_info['name']}: {e}")
                results.append({
                    'page': page_info['name'],
                    'url': page_info['url'],
                    'error': str(e)
                })
        
        # Save results to file
        with open('/mnt/c/Users/ayoon/projects/AizasFineArt/border_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== Test Complete ===")
        print(f"Results saved to border_test_results.json")
        
        # Keep browser open for manual inspection
        print("Browser will stay open for 30 seconds for manual inspection...")
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_border_colors())