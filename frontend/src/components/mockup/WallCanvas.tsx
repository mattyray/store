'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import type { Photo, ProductVariant, WallAnalysis } from '@/types';

// Fabric.js types (will be imported dynamically)
type FabricCanvas = {
  dispose: () => void;
  setBackgroundImage: (img: FabricImage, callback: () => void, options?: object) => void;
  renderAll: () => void;
  add: (obj: FabricObject) => void;
  remove: (obj: FabricObject) => void;
  setActiveObject: (obj: FabricObject) => void;
  toDataURL: (options?: { format?: string; quality?: number; multiplier?: number }) => string;
  getObjects: () => FabricObject[];
  getActiveObject: () => FabricObject | null;
  on: (event: string, handler: () => void) => void;
  setWidth: (width: number) => void;
  setHeight: (height: number) => void;
};

type FabricImage = FabricObject & {
  scaleToWidth: (width: number) => void;
  width?: number;
  height?: number;
};

type FabricObject = {
  set: (options: object) => void;
  data?: { printId?: string };
};

type FabricShadow = object;

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
  const fabricRef = useRef<FabricCanvas | null>(null);
  const printObjectsRef = useRef<Map<string, FabricImage>>(new Map());
  const [fabricLoaded, setFabricLoaded] = useState(false);
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
  const [scale, setScale] = useState(1);

  // Load Fabric.js dynamically
  useEffect(() => {
    import('fabric').then((fabricModule) => {
      (window as unknown as { fabric: typeof fabricModule.fabric }).fabric = fabricModule.fabric;
      setFabricLoaded(true);
    });
  }, []);

  // Calculate canvas size based on container
  useEffect(() => {
    if (!containerRef.current) return;

    const updateSize = () => {
      const container = containerRef.current;
      if (!container) return;

      const containerWidth = container.clientWidth;
      const maxHeight = window.innerHeight * 0.6;

      // Load the wall image to get its dimensions
      const img = new Image();
      img.onload = () => {
        const imageAspect = img.width / img.height;
        let width = containerWidth;
        let height = width / imageAspect;

        if (height > maxHeight) {
          height = maxHeight;
          width = height * imageAspect;
        }

        setCanvasSize({ width, height });
        setScale(width / img.width);
      };
      img.src = wallImage;
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, [wallImage]);

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (!fabricLoaded || !canvasElementRef.current) return;

    const fabric = (window as unknown as { fabric: { Canvas: new (el: HTMLCanvasElement, options?: object) => FabricCanvas; Image: { fromURL: (url: string, callback: (img: FabricImage) => void, options?: object) => void }; Shadow: new (options: object) => FabricShadow } }).fabric;

    // Dispose existing canvas
    if (fabricRef.current) {
      fabricRef.current.dispose();
    }

    // Create new canvas
    const canvas = new fabric.Canvas(canvasElementRef.current, {
      selection: true,
      preserveObjectStacking: true,
    });
    fabricRef.current = canvas;

    // Set canvas size
    canvas.setWidth(canvasSize.width);
    canvas.setHeight(canvasSize.height);

    // Load wall image as background
    fabric.Image.fromURL(
      wallImage,
      (img: FabricImage) => {
        canvas.setBackgroundImage(img, () => canvas.renderAll(), {
          scaleX: canvasSize.width / (img.width || 1),
          scaleY: canvasSize.height / (img.height || 1),
        });
      },
      { crossOrigin: 'anonymous' }
    );

    // Handle object movement
    canvas.on('object:moved', () => {
      const activeObj = canvas.getActiveObject();
      if (activeObj && activeObj.data?.printId && onPrintMove) {
        const obj = activeObj as unknown as { left: number; top: number };
        onPrintMove(activeObj.data.printId, {
          x: obj.left / scale,
          y: obj.top / scale,
        });
      }
    });

    return () => {
      canvas.dispose();
    };
  }, [fabricLoaded, canvasSize, wallImage, scale, onPrintMove]);

  // Add/update prints on canvas
  useEffect(() => {
    if (!fabricRef.current || !fabricLoaded) return;

    const fabric = (window as unknown as { fabric: { Canvas: new (el: HTMLCanvasElement, options?: object) => FabricCanvas; Image: { fromURL: (url: string, callback: (img: FabricImage) => void, options?: object) => void }; Shadow: new (options: object) => FabricShadow } }).fabric;
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

      fabric.Image.fromURL(
        print.photo.image,
        (img: FabricImage) => {
          img.scaleToWidth(printWidthPx);
          img.set({
            left: posX,
            top: posY,
            hasControls: true,
            hasBorders: true,
            lockRotation: true,
            lockScalingFlip: true,
            cornerColor: '#3b82f6',
            cornerStyle: 'circle',
            borderColor: '#3b82f6',
            data: { printId: print.id },
            shadow: new fabric.Shadow({
              color: 'rgba(0,0,0,0.4)',
              blur: 20,
              offsetX: 8,
              offsetY: 8,
            }),
          });

          canvas.add(img);
          canvas.setActiveObject(img);
          canvas.renderAll();
          printObjectsRef.current.set(print.id, img);
        },
        { crossOrigin: 'anonymous' }
      );
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
    if (canvasRef) {
      (canvasRef as React.MutableRefObject<{ toDataURL: () => string } | null>).current = {
        toDataURL: getDataURL,
      };
    }
  }, [canvasRef, getDataURL]);

  // Remove selected print
  const handleRemoveSelected = useCallback(() => {
    if (!fabricRef.current) return;
    const activeObj = fabricRef.current.getActiveObject();
    if (activeObj && activeObj.data?.printId) {
      onPrintRemove?.(activeObj.data.printId);
    }
  }, [onPrintRemove]);

  return (
    <div ref={containerRef} className="relative w-full">
      <canvas ref={canvasElementRef} className="border border-gray-200 dark:border-gray-700 rounded" />

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
      <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
        Drag prints to reposition. Use corners to resize.
      </p>
    </div>
  );
}
