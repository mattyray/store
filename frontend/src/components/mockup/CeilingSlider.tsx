'use client';

interface CeilingSliderProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export default function CeilingSlider({ value, onChange, disabled }: CeilingSliderProps) {
  return (
    <div className={`${disabled ? 'opacity-50' : ''}`}>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Ceiling Height
        </label>
        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
          {value} ft
        </span>
      </div>

      <input
        type="range"
        min={7}
        max={12}
        step={0.5}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        disabled={disabled}
        className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />

      <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1">
        <span>7 ft</span>
        <span>12 ft</span>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Adjust to match your room&apos;s ceiling height for accurate print sizing
      </p>
    </div>
  );
}
