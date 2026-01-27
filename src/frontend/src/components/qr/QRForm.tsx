import { zodResolver } from '@hookform/resolvers/zod'
import { useRef } from 'react'
import { useForm } from 'react-hook-form'

import { COLOR_PALETTE } from '../../utils/constants'
import type { QRFormValues } from '../../utils/validation'
import { qrSchema } from '../../utils/validation'
import { Input } from '../common/Input'

interface QRFormProps {
  onPreview: (values: QRFormValues) => void
  onSubmit: (values: QRFormValues) => void
  isSubmitting?: boolean
  isPreviewing?: boolean
}

const Section = ({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) => (
  <div className="space-y-3">
    <div className="border-b border-slate-200/60 pb-2">
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
    </div>
    <div className="space-y-4">{children}</div>
  </div>
)

const SliderField = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  error,
}: {
  label: string
  value: number
  onChange: (val: number) => void
  min: number
  max: number
  step?: number
  error?: string
}) => (
  <div className="space-y-1.5">
    <label className="text-xs font-medium text-slate-700">{label}</label>
    <div className="flex items-center gap-3">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="flex-1 h-1.5 bg-slate-200 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-600 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition [&::-webkit-slider-thumb]:hover:bg-blue-700 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-blue-600 [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:cursor-pointer"
      />
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-16 px-2 py-1 text-xs text-center border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all duration-150"
      />
    </div>
    {error && <p className="text-xs text-red-500">{error}</p>}
  </div>
)

const ColorField = ({
  label,
  value,
  onChange,
  error,
  palette,
}: {
  label: string
  value: string
  onChange: (val: string) => void
  error?: string
  palette?: string[]
}) => (
  <div className="space-y-2">
    <label className="text-xs font-medium text-slate-700">{label}</label>
    <div className="flex items-center gap-2">
      <div
        className="w-10 h-10 rounded-lg border-2 border-slate-200 shadow-sm cursor-pointer transition-transform hover:scale-105"
        style={{ backgroundColor: value }}
        onClick={() => document.getElementById(`color-${label}`)?.click()}
      />
      <input
        id={`color-${label}`}
        type="color"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="sr-only"
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="#000000"
        className="flex-1 px-3 py-2 text-xs font-mono border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all duration-150"
      />
    </div>
    {palette && (
      <div className="flex flex-wrap gap-1.5">
        {palette.map((color) => (
          <button
            key={color}
            type="button"
            onClick={() => onChange(color)}
            className="w-7 h-7 rounded-md border border-slate-200 shadow-sm transition-all duration-150 hover:scale-110 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            style={{ backgroundColor: color }}
            aria-label={`Use color ${color}`}
          />
        ))}
      </div>
    )}
    {error && <p className="text-xs text-red-500">{error}</p>}
  </div>
)

export const QRForm = ({ onPreview, onSubmit: onSubmitProp, isSubmitting: ___, isPreviewing: ____ }: QRFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    getValues,
  } = useForm<QRFormValues>({
    resolver: zodResolver(qrSchema),
    defaultValues: {
      title: 'New campaign',
      url: 'https://example.com',
      foreground_color: '#1d4ed8',
      background_color: '#ffffff',
      size: 320,
      padding: 12,
      border_radius: 8,
      overlay_text: '',
    },
  })

  const watchedValues = watch()
  const overlayLength = watchedValues.overlay_text?.length || 0
  const overlayMaxLength = 4

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)

  const debouncedPreview = () => {
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current)
    debounceTimerRef.current = setTimeout(() => {
      // Always get the latest values from the form
      const currentValues = getValues()
      onPreview(currentValues)
    }, 300)
  }

  const handleFieldChange = (callback: () => void) => {
    callback()
    // Trigger preview immediately with current values
    debouncedPreview()
  }

  return (
    <form className="flex flex-col h-full" onSubmit={handleSubmit(onSubmitProp)}>
      <div className="flex-1 overflow-y-auto scrollbar-hide space-y-6 pb-4">
        <Section title="Basics" description="Campaign details and destination">
          <Input
            label="Title"
            error={errors.title?.message}
            {...register('title')}
            placeholder="Campaign Black Friday"
          />
          <Input
            label="URL / Destination"
            error={errors.url?.message}
            {...register('url')}
            placeholder="https://your-site.com"
          />
        </Section>

        <Section title="Colors" description="Customize foreground and background">
          <ColorField
            label="Primary"
            value={watchedValues.foreground_color}
            onChange={(val) => handleFieldChange(() => setValue('foreground_color', val))}
            error={errors.foreground_color?.message}
            palette={COLOR_PALETTE}
          />
          <ColorField
            label="Background"
            value={watchedValues.background_color}
            onChange={(val) => handleFieldChange(() => setValue('background_color', val))}
            error={errors.background_color?.message}
          />
        </Section>

        <Section title="Shape & Size" description="Configure dimensions and style">
          <SliderField
            label="Size (px)"
            value={watchedValues.size}
            onChange={(val) => handleFieldChange(() => setValue('size', val))}
            min={128}
            max={512}
            step={8}
            error={errors.size?.message}
          />
          <SliderField
            label="Padding"
            value={watchedValues.padding}
            onChange={(val) => handleFieldChange(() => setValue('padding', val))}
            min={0}
            max={32}
            step={2}
            error={errors.padding?.message}
          />
          <SliderField
            label="Border Radius"
            value={watchedValues.border_radius}
            onChange={(val) => handleFieldChange(() => setValue('border_radius', val))}
            min={0}
            max={24}
            step={2}
            error={errors.border_radius?.message}
          />
        </Section>

        <Section title="Overlay" description="Optional text label (max 4 chars)">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-700">Text</label>
              <span
                className={`text-xs font-medium transition-colors duration-150 ${
                  overlayLength > overlayMaxLength ? 'text-red-500' : 'text-slate-400'
                }`}
              >
                {overlayLength} / {overlayMaxLength}
              </span>
            </div>
            <Input
              {...register('overlay_text')}
              placeholder="TXT"
              error={errors.overlay_text?.message}
              maxLength={overlayMaxLength}
            />
          </div>
        </Section>
      </div>
    </form>
  )
}
