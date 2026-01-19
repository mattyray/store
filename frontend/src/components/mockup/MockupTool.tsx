'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import type { Photo, ProductVariant, WallAnalysis } from '@/types';
import {
  uploadWallImage,
  pollWallAnalysis,
  updateWallAnalysis,
  saveMockup,
  getPhotos,
} from '@/lib/api';
import WallUploader from './WallUploader';
import WallCanvas from './WallCanvas';
import CeilingSlider from './CeilingSlider';
import PrintSelector from './PrintSelector';

interface MockupPrint {
  id: string;
  photo: Photo;
  variant: ProductVariant;
  position: { x: number; y: number };
}

interface MockupToolProps {
  initialPhoto?: Photo;
  initialVariant?: ProductVariant;
  onClose: () => void;
}

type Step = 'upload' | 'processing' | 'editor';

export default function MockupTool({ initialPhoto, initialVariant, onClose }: MockupToolProps) {
  // State
  const [step, setStep] = useState<Step>('upload');
  const [isUploading, setIsUploading] = useState(false);
  const [analysis, setAnalysis] = useState<WallAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Editor state
  const [ceilingHeight, setCeilingHeight] = useState(8);
  const [prints, setPrints] = useState<MockupPrint[]>([]);
  const [availablePhotos, setAvailablePhotos] = useState<Photo[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(initialPhoto || null);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(initialVariant || null);

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  // Canvas ref for export
  const canvasRef = useRef<{ toDataURL: () => string } | null>(null);

  // Load available photos
  useEffect(() => {
    getPhotos()
      .then((data) => {
        setAvailablePhotos(data.results || []);
        // If we have an initial photo, make sure it has variants
        if (initialPhoto && initialPhoto.variants) {
          setSelectedPhoto(initialPhoto);
        }
      })
      .catch(console.error);
  }, [initialPhoto]);

  // Handle wall image upload
  const handleUpload = useCallback(async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadWallImage(file);
      setAnalysis(result);

      if (result.status === 'pending' || result.status === 'processing') {
        setStep('processing');
        // Poll for completion
        const completed = await pollWallAnalysis(result.id, (status) => {
          setAnalysis((prev) => (prev ? { ...prev, status } : null));
        });
        setAnalysis(completed);
        setStep('editor');
      } else {
        // Already completed or manual
        setStep('editor');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  }, []);

  // Handle sample wall selection
  const handleSampleWallSelect = useCallback(async (wallUrl: string) => {
    setIsUploading(true);
    setError(null);

    try {
      // Fetch the sample wall image and convert to File
      const response = await fetch(wallUrl);
      const blob = await response.blob();
      const filename = wallUrl.split('/').pop() || 'sample-wall.jpg';
      const file = new File([blob], filename, { type: blob.type });

      // Upload through the normal flow
      const result = await uploadWallImage(file);
      setAnalysis(result);

      if (result.status === 'pending' || result.status === 'processing') {
        setStep('processing');
        // Poll for completion
        const completed = await pollWallAnalysis(result.id, (status) => {
          setAnalysis((prev) => (prev ? { ...prev, status } : null));
        });
        setAnalysis(completed);
        setStep('editor');
      } else {
        setStep('editor');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sample wall');
    } finally {
      setIsUploading(false);
    }
  }, []);

  // Handle ceiling height change
  const handleCeilingHeightChange = useCallback(
    async (height: number) => {
      setCeilingHeight(height);

      if (analysis) {
        try {
          const updated = await updateWallAnalysis(analysis.id, {
            wall_height_feet: height,
          });
          setAnalysis(updated);
        } catch (err) {
          console.error('Failed to update analysis:', err);
        }
      }
    },
    [analysis]
  );

  // Add print to wall
  const handleAddPrint = useCallback(() => {
    if (!selectedPhoto || !selectedVariant) return;

    const newPrint: MockupPrint = {
      id: `print-${Date.now()}`,
      photo: selectedPhoto,
      variant: selectedVariant,
      position: { x: 0, y: 0 }, // Will be centered by canvas
    };

    setPrints((prev) => [...prev, newPrint]);
  }, [selectedPhoto, selectedVariant]);

  // Update print position
  const handlePrintMove = useCallback((printId: string, position: { x: number; y: number }) => {
    setPrints((prev) =>
      prev.map((p) => (p.id === printId ? { ...p, position } : p))
    );
  }, []);

  // Remove print
  const handlePrintRemove = useCallback((printId: string) => {
    setPrints((prev) => prev.filter((p) => p.id !== printId));
  }, []);

  // Download mockup
  const handleDownload = useCallback(() => {
    if (!canvasRef.current) return;

    const dataUrl = canvasRef.current.toDataURL();
    const link = document.createElement('a');
    link.download = 'wall-mockup.jpg';
    link.href = dataUrl;
    link.click();
  }, []);

  // Save and get share link
  const handleSave = useCallback(async () => {
    if (!canvasRef.current || !analysis) return;

    setIsSaving(true);
    try {
      const mockupImage = canvasRef.current.toDataURL();
      const result = await saveMockup({
        analysis_id: analysis.id,
        mockup_image: mockupImage,
        config: {
          prints: prints.map((p) => ({
            photo_id: p.photo.id,
            variant_id: p.variant.id,
            position: p.position,
          })),
          wall_height_feet: ceilingHeight,
        },
      });
      setShareUrl(result.share_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setIsSaving(false);
    }
  }, [analysis, prints, ceilingHeight]);

  // Copy share link
  const handleCopyLink = useCallback(() => {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl);
    }
  }, [shareUrl]);

  // Calculate pixels per inch
  const pixelsPerInch = analysis?.pixels_per_inch || (analysis?.wall_bounds
    ? (analysis.wall_bounds.bottom - analysis.wall_bounds.top) / (ceilingHeight * 12)
    : 10);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100">
            See In Your Room
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded">
              {error}
            </div>
          )}

          {/* Upload Step */}
          {step === 'upload' && (
            <div className="max-w-lg mx-auto">
              <WallUploader
                onUpload={handleUpload}
                onSelectSampleWall={handleSampleWallSelect}
                isUploading={isUploading}
              />
            </div>
          )}

          {/* Processing Step */}
          {step === 'processing' && (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Analyzing your wall...
              </p>
              {analysis?.status && (
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                  Status: {analysis.status}
                </p>
              )}
            </div>
          )}

          {/* Editor Step */}
          {step === 'editor' && analysis && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Canvas */}
              <div className="lg:col-span-2">
                <WallCanvas
                  wallImage={analysis.original_image}
                  wallBounds={analysis.wall_bounds}
                  pixelsPerInch={pixelsPerInch}
                  prints={prints}
                  onPrintMove={handlePrintMove}
                  onPrintRemove={handlePrintRemove}
                  canvasRef={canvasRef}
                />

                {/* Confidence indicator */}
                {analysis.confidence !== null && (
                  <div className="mt-2 text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Wall detection: </span>
                    <span
                      className={`font-medium ${
                        analysis.confidence >= 0.5
                          ? 'text-green-600 dark:text-green-400'
                          : analysis.confidence >= 0.3
                          ? 'text-yellow-600 dark:text-yellow-400'
                          : 'text-red-600 dark:text-red-400'
                      }`}
                    >
                      {Math.round(analysis.confidence * 100)}%
                    </span>
                    {analysis.status === 'manual' && (
                      <span className="text-gray-400 dark:text-gray-500 ml-2">
                        (manual selection)
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="space-y-6">
                {/* Ceiling Height */}
                <CeilingSlider
                  value={ceilingHeight}
                  onChange={handleCeilingHeightChange}
                />

                {/* Print Selector */}
                <PrintSelector
                  photos={availablePhotos}
                  selectedPhoto={selectedPhoto}
                  selectedVariant={selectedVariant}
                  onSelectPhoto={(photo) => {
                    setSelectedPhoto(photo);
                    setSelectedVariant(null);
                  }}
                  onSelectVariant={setSelectedVariant}
                  onAddPrint={handleAddPrint}
                />

                {/* Actions */}
                <div className="space-y-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handleDownload}
                    disabled={prints.length === 0}
                    className="w-full py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:bg-gray-800 dark:hover:bg-gray-200 transition disabled:opacity-50"
                  >
                    Download Image
                  </button>

                  <button
                    onClick={handleSave}
                    disabled={prints.length === 0 || isSaving}
                    className="w-full py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition disabled:opacity-50"
                  >
                    {isSaving ? 'Saving...' : 'Get Shareable Link'}
                  </button>

                  {shareUrl && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                      <p className="text-sm text-green-700 dark:text-green-300 mb-2">
                        Mockup saved!
                      </p>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={shareUrl}
                          readOnly
                          className="flex-1 px-2 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded"
                        />
                        <button
                          onClick={handleCopyLink}
                          className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
