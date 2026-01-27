const chips = Array.from({ length: 16 }).map((_, i) => {
  const column = i % 6
  const row = Math.floor(i / 6)
  const baseLeft = 6 + column * 15
  const duration = 42 + (i % 4) * 4
  return {
    left: `${baseLeft}%`,
    delay: `${i * 1.8}s`,
    duration: `${duration}s`,
    opacity: 0.14 + (i % 3) * 0.03,
    size: 56 + (i % 3) * 5,
    top: `${-260 - row * 60}px`,
  }
})

export const BackgroundLayer = () => (
  <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden bg-transparent">
    <div className="qr-rain">
      {chips.map((chip, idx) => (
        <span
          key={idx}
          className="qr-chip"
          style={{
            left: chip.left,
            animationDelay: chip.delay,
            animationDuration: chip.duration,
            opacity: chip.opacity,
            width: chip.size,
            height: chip.size,
            top: chip.top,
          }}
        />
      ))}
    </div>
  </div>
)
