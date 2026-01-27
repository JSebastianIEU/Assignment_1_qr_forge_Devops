import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import { COLOR_PALETTE } from '../../utils/constants'
import type { QRFormValues } from '../../utils/validation'
import { qrSchema } from '../../utils/validation'
import { Button } from '../common/Button'
import { Input } from '../common/Input'

interface QRFormProps {
  onPreview: (values: QRFormValues) => void
  onSubmit: (values: QRFormValues) => void
  isSubmitting?: boolean
  isPreviewing?: boolean
}

export const QRForm = ({ onPreview, onSubmit, isSubmitting, isPreviewing }: QRFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
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

  return (
    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
      <div className="grid gap-4 sm:grid-cols-2">
        <Input label="Title" error={errors.title?.message} {...register('title')} placeholder="Campaign Black Friday" />
        <Input
          label="URL / destination"
          error={errors.url?.message}
          {...register('url')}
          placeholder="https://your-site.com"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="Primary color"
          type="color"
          error={errors.foreground_color?.message}
          {...register('foreground_color')}
        />
        <Input
          label="Background color"
          type="color"
          error={errors.background_color?.message}
          {...register('background_color')}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Input
          label="Size (px)"
          type="number"
          inputMode="numeric"
          error={errors.size?.message}
          {...register('size', { valueAsNumber: true })}
        />
        <Input
          label="Padding"
          type="number"
          inputMode="numeric"
          error={errors.padding?.message}
          {...register('padding', { valueAsNumber: true })}
        />
        <Input
          label="Border radius"
          type="number"
          inputMode="numeric"
          error={errors.border_radius?.message}
          {...register('border_radius', { valueAsNumber: true })}
        />
      </div>

      <Input
        label="Overlay (optional)"
        error={errors.overlay_text?.message}
        {...register('overlay_text')}
        placeholder="TXT"
        helperText="Max 4 characters"
      />

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-700">Quick palette</p>
        <div className="flex flex-wrap gap-2">
          {COLOR_PALETTE.map((color) => (
            <button
              key={color}
              type="button"
              aria-label={`Use color ${color}`}
              className="h-8 w-8 rounded-full border border-slate-200"
              style={{ backgroundColor: color }}
              onClick={() => setValue('foreground_color', color)}
            />
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button type="submit" loading={isSubmitting}>
          Save QR
        </Button>
        <Button
          type="button"
          variant="secondary"
          loading={isPreviewing}
          onClick={handleSubmit((values) => onPreview(values))}
        >
          View preview
        </Button>
      </div>
    </form>
  )
}
