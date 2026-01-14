'use client';

interface CropOverlayProps {
  widthInches: number;
  heightInches: number;
  sourceRatio?: number; // defaults to 3:2 (1.5)
}

/**
 * Displays a semi-transparent overlay showing what areas will be cropped
 * when printing at the selected size.
 *
 * Darkens the areas that will be cut off, leaving the printable area clear.
 * When ratios match (no crop needed), shows a subtle border to indicate selection.
 */
export default function CropOverlay({
  widthInches,
  heightInches,
  sourceRatio = 1.5 // 3:2 default
}: CropOverlayProps) {
  // For vertical images (sourceRatio < 1), flip the print dimensions
  // so that a "30x20" print becomes "20x30" for vertical orientation
  const isVertical = sourceRatio < 1;
  const printRatio = isVertical
    ? heightInches / widthInches
    : widthInches / heightInches;

  // If ratios match (within tolerance), no crop needed - show full frame border
  const tolerance = 0.02;
  if (Math.abs(printRatio - sourceRatio) < tolerance) {
    return (
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-2 border-2 border-white/70 rounded" />
      </div>
    );
  }

  // Calculate crop percentages
  // If print is wider than source: crop top/bottom
  // If print is narrower than source: crop left/right

  let cropX = 0; // percentage to crop from each side (left and right)
  let cropY = 0; // percentage to crop from each side (top and bottom)

  if (printRatio > sourceRatio) {
    // Print is wider - crop top and bottom
    // Calculate what percentage of height to keep
    const keepHeight = sourceRatio / printRatio;
    cropY = ((1 - keepHeight) / 2) * 100;
  } else {
    // Print is narrower - crop left and right
    // Calculate what percentage of width to keep
    const keepWidth = printRatio / sourceRatio;
    cropX = ((1 - keepWidth) / 2) * 100;
  }

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Top crop overlay */}
      {cropY > 0 && (
        <div
          className="absolute left-0 right-0 top-0 bg-black/50"
          style={{ height: `${cropY}%` }}
        />
      )}

      {/* Bottom crop overlay */}
      {cropY > 0 && (
        <div
          className="absolute left-0 right-0 bottom-0 bg-black/50"
          style={{ height: `${cropY}%` }}
        />
      )}

      {/* Left crop overlay */}
      {cropX > 0 && (
        <div
          className="absolute left-0 top-0 bottom-0 bg-black/50"
          style={{
            width: `${cropX}%`,
            top: cropY > 0 ? `${cropY}%` : 0,
            bottom: cropY > 0 ? `${cropY}%` : 0
          }}
        />
      )}

      {/* Right crop overlay */}
      {cropX > 0 && (
        <div
          className="absolute right-0 top-0 bottom-0 bg-black/50"
          style={{
            width: `${cropX}%`,
            top: cropY > 0 ? `${cropY}%` : 0,
            bottom: cropY > 0 ? `${cropY}%` : 0
          }}
        />
      )}

      {/* Border around the crop area */}
      {(cropX > 0 || cropY > 0) && (
        <div
          className="absolute border-2 border-white/70"
          style={{
            left: `${cropX}%`,
            right: `${cropX}%`,
            top: `${cropY}%`,
            bottom: `${cropY}%`
          }}
        />
      )}
    </div>
  );
}
