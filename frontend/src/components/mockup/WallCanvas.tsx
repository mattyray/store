'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import type { Photo, ProductVariant, WallAnalysis } from '@/types';

interface MockupPrintData {
  id: string;
  photo: Photo;
  variant: ProductVariant;
  position: { x: number; y: number };
}

interface WallCanvasProps {
  wallImage: string;
  wallBounds: WallAnalysis['wall_bounds'];
  pixelsPerInch: number;
  prints: MockupPrintData[];
  onPrintMove?: (printId: string, position: { x: number; y: number }) => void;
  onPrintRemove?: (printId: string) => void;
  canvasRef?: React.RefObject<{ toDataURL: () => string } | null>;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type FabricType = any;

export default function WallCanvas({
  wallImage,
  wallBounds,
  pixelsPerInch,
  prints,
  onPrintMove,
  onPrintRemove,
  canvasRef,
}: WallCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasElementRef = useRef<HTMLCanvasElement>(null);
  const fabricRef = useRef<FabricType>(null);
  const fabricModuleRef = useRef<FabricType>(null);
  const printObjectsRef = useRef<Map<string, FabricType>>(new Map());
  const [fabricLoaded, setFabricLoaded] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const [scale, setScale] = useState(1);
  const imageDimensionsRef = useRef({ width: 0, height: 0 });

  // Load Fabric.js dynamically
  useEffect(() => {
    import('fabric').then((mod) => {
      fabricModuleRef.current = mod;
      setFabricLoaded(true);
    });
  }, []);

  // Load wall image dimensions first
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      imageDimensionsRef.current = { width: img.width, height: img.height };
      setImageLoaded(true);
    };
    img.src = wallImage;
  }, [wallImage]);

  // Calculate canvas size based on container and image
  useEffect(() => {
    if (!containerRef.current || !imageLoaded) return;

    const updateSize = () => {
      const container = containerRef.current;
      if (!container) return;

      const { width: imgWidth, height: imgHeight } = imageDimensionsRef.current;
      if (!imgWidth || !imgHeight) return;

      const containerWidth = container.clientWidth;
      const maxHeight = window.innerHeight * 0.6;
      const imageAspect = imgWidth / imgHeight;

      let width: number;
      let height: number;

      // For portrait images (taller than wide), fit to height first
      if (imageAspect < 1) {
        height = Math.min(maxHeight, 500);
        width = height * imageAspect;
        // Ensure width doesn't exceed container
        if (width > containerWidth) {
          width = containerWidth;
          height = width / imageAspect;
        }
      } else {
        // Landscape images - fit to width first
        width = Math.min(containerWidth, 600);
        height = width / imageAspect;
        if (height > maxHeight) {
          height = maxHeight;
          width = height * imageAspect;
        }
      }

      setCanvasSize({ width: Math.round(width), height: Math.round(height) });
      setScale(width / imgWidth);
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, [wallImage, imageLoaded]);

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (!fabricLoaded || !canvasElementRef.current || !fabricModuleRef.current || !canvasSize.width || !canvasSize.height) return;

    const fabric = fabricModuleRef.current;

    // Dispose existing canvas
    if (fabricRef.current) {
      fabricRef.current.dispose();
    }

    // Create new canvas
    const canvas = new fabric.Canvas(canvasElementRef.current, {
      selection: true,
      preserveObjectStacking: true,
      width: canvasSize.width,
      height: canvasSize.height,
    });
    fabricRef.current = canvas;

    // Load wall image as background
    fabric.FabricImage.fromURL(wallImage, { crossOrigin: 'anonymous' }).then((img: FabricType) => {
      // Scale image to fit canvas
      const scaleX = canvasSize.width / img.width;
      const scaleY = canvasSize.height / img.height;
      img.set({
        scaleX: scaleX,
        scaleY: scaleY,
        originX: 'left',
        originY: 'top',
        left: 0,
        top: 0,
      });
      canvas.backgroundImage = img;
      canvas.renderAll();
    }).catch((err: Error) => {
      console.error('Failed to load wall image:', err);
    });

    // Handle object movement
    canvas.on('object:modified', () => {
      const activeObj = canvas.getActiveObject();
      if (activeObj && activeObj.printId && onPrintMove) {
        onPrintMove(activeObj.printId, {
          x: activeObj.left / scale,
          y: activeObj.top / scale,
        });
      }
    });

    return () => {
      canvas.dispose();
    };
  }, [fabricLoaded, canvasSize, wallImage, scale, onPrintMove]);

  // Add/update prints on canvas
  useEffect(() => {
    if (!fabricRef.current || !fabricLoaded || !fabricModuleRef.current) return;

    const fabric = fabricModuleRef.current;
    const canvas = fabricRef.current;

    // Track which prints we've seen
    const currentPrintIds = new Set(prints.map((p) => p.id));

    // Remove prints that are no longer in the list
    printObjectsRef.current.forEach((obj, printId) => {
      if (!currentPrintIds.has(printId)) {
        canvas.remove(obj);
        printObjectsRef.current.delete(printId);
      }
    });

    // Add new prints
    prints.forEach((print) => {
      if (printObjectsRef.current.has(print.id)) return;

      // Calculate print size in canvas pixels
      const printWidthInches = print.variant.width_inches;
      const printHeightInches = print.variant.height_inches;
      const printWidthPx = printWidthInches * pixelsPerInch * scale;
      const printHeightPx = printHeightInches * pixelsPerInch * scale;

      // Default position: center of wall bounds
      let defaultX = canvasSize.width / 2 - printWidthPx / 2;
      let defaultY = canvasSize.height / 2 - printHeightPx / 2;

      if (wallBounds) {
        const scaledBounds = {
          left: wallBounds.left * scale,
          right: wallBounds.right * scale,
          top: wallBounds.top * scale,
          bottom: wallBounds.bottom * scale,
        };
        defaultX = (scaledBounds.left + scaledBounds.right) / 2 - printWidthPx / 2;
        defaultY = (scaledBounds.top + scaledBounds.bottom) / 2 - printHeightPx / 2;
      }

      const posX = print.position.x ? print.position.x * scale : defaultX;
      const posY = print.position.y ? print.position.y * scale : defaultY;

      fabric.FabricImage.fromURL(print.photo.image, { crossOrigin: 'anonymous' }).then((img: FabricType) => {
        const scaleToFit = printWidthPx / img.width;
        img.scaleX = scaleToFit;
        img.scaleY = scaleToFit * (printHeightPx / (img.height * scaleToFit));
        img.set({
          left: posX,
          top: posY,
          hasControls: true,
          hasBorders: true,
          lockRotation: true,
          cornerColor: '#3b82f6',
          cornerStyle: 'circle',
          borderColor: '#3b82f6',
          shadow: new fabric.Shadow({
            color: 'rgba(0,0,0,0.4)',
            blur: 20,
            offsetX: 8,
            offsetY: 8,
          }),
        });

        // Store custom data on the object
        img.printId = print.id;

        canvas.add(img);
        canvas.setActiveObject(img);
        canvas.renderAll();
        printObjectsRef.current.set(print.id, img);
      });
    });
  }, [prints, fabricLoaded, pixelsPerInch, scale, canvasSize, wallBounds]);

  // Expose toDataURL method
  const getDataURL = useCallback(() => {
    if (!fabricRef.current) return '';
    return fabricRef.current.toDataURL({
      format: 'jpeg',
      quality: 0.9,
      multiplier: 2,
    });
  }, []);

  // Set ref for parent access
  useEffect(() => {
    if (canvasRef && 'current' in canvasRef) {
      (canvasRef as { current: { toDataURL: () => string } | null }).current = {
        toDataURL: getDataURL,
      };
    }
  }, [canvasRef, getDataURL]);

  // Remove selected print
  const handleRemoveSelected = useCallback(() => {
    if (!fabricRef.current) return;
    const activeObj = fabricRef.current.getActiveObject();
    if (activeObj && activeObj.printId) {
      onPrintRemove?.(activeObj.printId);
    }
  }, [onPrintRemove]);

  return (
    <div ref={containerRef} className="relative w-full flex justify-center">
      {canvasSize.width > 0 && canvasSize.height > 0 ? (
        <canvas ref={canvasElementRef} className="border border-gray-200 dark:border-gray-700 rounded" />
      ) : (
        <div className="w-full h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded">
          <span className="text-gray-500">Loading wall image...</span>
        </div>
      )}

      {/* Remove button */}
      <button
        onClick={handleRemoveSelected}
        className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition opacity-80 hover:opacity-100"
        title="Remove selected print"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      {/* Instructions */}
      {canvasSize.width > 0 && (
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
          Drag prints to reposition. Use corners to resize.
        </p>
      )}
    </div>
  );
}
