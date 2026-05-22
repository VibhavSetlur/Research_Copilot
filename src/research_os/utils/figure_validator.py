#!/usr/bin/env python3
"""
Research OS Figure Quality Validator
Performs quality and publication compliance checks on generated PNG figures.
Checks DPI, margin truncation, colorblind safety, and axis labels.
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image

# Canonical Okabe-Ito color palette in RGB
OKABE_ITO_RGB = [
    (0, 0, 0),        # Black
    (230, 159, 0),    # Orange
    (86, 180, 233),   # Sky Blue
    (0, 158, 115),    # Bluish Green
    (240, 228, 66),   # Yellow
    (0, 114, 178),    # Blue
    (213, 94, 0),     # Vermilion
    (204, 121, 167)   # Reddish Purple
]

def check_file_size(path: Path, max_mb: float = 5.0) -> Tuple[bool, str]:
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File size too large: {size_mb:.2f} MB (max {max_mb} MB)"
    return True, f"File size is reasonable: {size_mb:.2f} MB"

def check_dpi(img: Image.Image, minimum: int = 300) -> Tuple[bool, str]:
    dpi = img.info.get("dpi")
    if dpi:
        # dpi can be a tuple (x_dpi, y_dpi)
        avg_dpi = sum(dpi) / len(dpi)
        if avg_dpi < (minimum - 1.0):
            return False, f"DPI {avg_dpi:.1f} is below minimum requirement of {minimum}"
        return True, f"DPI {avg_dpi:.1f} meets requirement"
    
    # Heuristic based on pixel dimensions (e.g. > 1200px width is likely high-res)
    width, height = img.size
    if width >= 1200:
        return True, f"DPI metadata missing, but resolution {width}x{height} is sufficient (assumed >= 300 DPI)"
    return False, f"DPI metadata missing and resolution {width}x{height} is too low for publication"

def check_axis_origin_truncation(img: Image.Image) -> Tuple[bool, str]:
    """Check if non-background pixels touch the absolute edges of the image (indicating clipping)."""
    width, height = img.size
    # Convert image to RGB to handle background color checks
    rgb_img = img.convert("RGB")
    
    # Get background color (typically the color of the top-left pixel)
    bg_color = rgb_img.getpixel((0, 0))
    
    # Check if there are non-bg pixels on the outer 2-pixel border
    border_pixels = []
    
    # Top and bottom borders
    for x in range(width):
        border_pixels.append(rgb_img.getpixel((x, 0)))
        border_pixels.append(rgb_img.getpixel((x, height - 1)))
        
    # Left and right borders
    for y in range(height):
        border_pixels.append(rgb_img.getpixel((0, y)))
        border_pixels.append(rgb_img.getpixel((width - 1, y)))
        
    # Count non-background pixels on the border
    threshold = 15  # RGB tolerance
    clipped = 0
    for p in border_pixels:
        diff = sum(abs(p[i] - bg_color[i]) for i in range(3))
        if diff > threshold:
            clipped += 1
            
    # If more than 0.5% of the border pixels are non-background, warn of potential truncation
    total_border = len(border_pixels)
    if (clipped / total_border) > 0.005:
        return False, f"Potential truncation detected: {clipped} pixels touch the outer image borders"
    
    return True, "No border clipping/truncation detected"

def check_axis_labels_heuristic(img: Image.Image) -> Tuple[bool, str]:
    """Heuristic check: verify presence of text/variation in bottom and left margins where labels reside."""
    width, height = img.size
    rgb_img = img.convert("RGB")
    bg_color = rgb_img.getpixel((0, 0))
    
    # Left margin (0% to 15% width) and Bottom margin (85% to 100% height)
    left_margin_w = int(width * 0.15)
    bottom_margin_h = int(height * 0.15)
    
    # Count color changes (variance) in left margin
    left_variance = 0
    for y in range(int(height * 0.2), int(height * 0.8), 5):
        row_colors = [rgb_img.getpixel((x, y)) for x in range(5, left_margin_w, 2)]
        # Check if any pixel differs from background
        non_bg = sum(1 for p in row_colors if sum(abs(p[i] - bg_color[i]) for i in range(3)) > 30)
        if non_bg > 0:
            left_variance += 1
            
    # Count color changes in bottom margin
    bottom_variance = 0
    for x in range(int(width * 0.2), int(width * 0.8), 5):
        col_colors = [rgb_img.getpixel((x, y)) for y in range(height - bottom_margin_h, height - 5, 2)]
        non_bg = sum(1 for p in col_colors if sum(abs(p[i] - bg_color[i]) for i in range(3)) > 30)
        if non_bg > 0:
            bottom_variance += 1
            
    # Require at least some variation indicating tick marks and labels
    if left_variance < 3:
        return False, "Failed: Left margin lacks pixel variation. Y-axis label or ticks may be missing."
    if bottom_variance < 3:
        return False, "Failed: Bottom margin lacks pixel variation. X-axis label or ticks may be missing."
        
    return True, "Left and bottom margin variance check passed (labels/ticks likely present)"

def check_colorblind_palette(img: Image.Image) -> Tuple[bool, str]:
    """Inspect top colors and check if they include dangerous red-green overlap without colorblind support."""
    # Resize to speed up color extraction
    small_img = img.convert("RGB").resize((100, 100))
    colors = small_img.getcolors(10000)
    
    if not colors:
        return True, "Unable to extract colors"
        
    # Sort colors by frequency
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
    
    # Filter out near-white and near-black background/foreground colors
    plot_colors = []
    for count, rgb in sorted_colors:
        # Ignore highly white or highly black/gray colors (background/text)
        is_gray = abs(rgb[0] - rgb[1]) < 15 and abs(rgb[1] - rgb[2]) < 15
        if not is_gray and (sum(rgb) < 700 and sum(rgb) > 100):
            plot_colors.append(rgb)
            if len(plot_colors) >= 5:
                break
                
    # Detect red vs green conflicts
    has_red = False
    has_green = False
    for r, g, b in plot_colors:
        if r > 150 and g < 100 and b < 100:
            has_red = True
        if g > 150 and r < 100 and b < 100:
            has_green = True
            
    if has_red and has_green:
        return False, "Warning: Image contains both saturated Red and Green, which is problematic for deuteranopia/protanopia. Use Okabe-Ito colors."
        
    return True, "Color palette check passed (no high-contrast red-green pairings detected)"


def validate_figure_file(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        return {
            "file_exists": False,
            "verdict": "FAIL",
            "errors": [f"File {path_str} does not exist"]
        }
        
    results = {}
    errors = []
    warnings = []
    
    try:
        # File Size Check
        size_ok, size_msg = check_file_size(path)
        results["file_size"] = {"status": "PASS" if size_ok else "FAIL", "message": size_msg}
        if not size_ok:
            errors.append(size_msg)
            
        # Open Image
        with Image.open(path) as img:
            # DPI Check
            dpi_ok, dpi_msg = check_dpi(img)
            results["dpi"] = {"status": "PASS" if dpi_ok else "FAIL", "message": dpi_msg}
            if not dpi_ok:
                errors.append(dpi_msg)
                
            # Origin / Truncation Check
            trunc_ok, trunc_msg = check_axis_origin_truncation(img)
            results["truncation"] = {"status": "PASS" if trunc_ok else "WARN", "message": trunc_msg}
            if not trunc_ok:
                warnings.append(trunc_msg)
                
            # Axis Labels Check
            labels_ok, labels_msg = check_axis_labels_heuristic(img)
            results["axis_labels"] = {"status": "PASS" if labels_ok else "FAIL", "message": labels_msg}
            if not labels_ok:
                errors.append(labels_msg)
                
            # Colorblind Safe Check
            cb_ok, cb_msg = check_colorblind_palette(img)
            results["colorblind_safe"] = {"status": "PASS" if cb_ok else "WARN", "message": cb_msg}
            if not cb_ok:
                warnings.append(cb_msg)
                
    except Exception as e:
        return {
            "file_exists": True,
            "verdict": "FAIL",
            "errors": [f"Image parsing failed: {e}"]
        }
        
    verdict = "FAIL" if errors else "PASS"
    
    return {
        "file_exists": True,
        "verdict": verdict,
        "results": results,
        "errors": errors,
        "warnings": warnings
    }

def main():
    parser = argparse.ArgumentParser(description="Verify figure quality and layout compliance")
    parser.add_argument("file", help="Path to the PNG figure file to validate")
    args = parser.parse_args()
    
    report = validate_figure_file(args.file)
    
    print("=" * 60)
    print(f"FIGURE QUALITY REPORT: {args.file}")
    print("=" * 60)
    print(f"Verdict: {report['verdict']}")
    print()
    
    if report.get("results"):
        for check, res in report["results"].items():
            print(f"  [{res['status']}] {check.ljust(15)}: {res['message']}")
            
    print()
    if report.get("errors"):
        print("ERRORS:")
        for err in report["errors"]:
            print(f"  - {err}")
            
    if report.get("warnings"):
        print("WARNINGS:")
        for warn in report["warnings"]:
            print(f"  - {warn}")
            
    print("=" * 60)
    
    # Exit with code 1 if validation fails
    if report["verdict"] == "FAIL":
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
