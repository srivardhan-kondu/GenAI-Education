import React, { useState } from 'react'

export default function ImageContent({ images }) {
  const [selected, setSelected] = useState(null)

  if (!images || images.length === 0) return null

  const validImages = images.filter((img) => img.base64_data)
  if (validImages.length === 0) {
    return (
      <div className="card text-center py-12 text-slate-400">
        <p className="text-4xl mb-2">🖼</p>
        <p className="font-medium">Image generation failed.</p>
        <p className="text-sm mt-1">
          The AI image service may be temporarily unavailable. Please try generating the module again.
        </p>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="card">
        <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          🖼 Visual Diagrams
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {validImages.map((img, i) => (
            <button
              key={i}
              onClick={() => setSelected(img)}
              className="group rounded-xl overflow-hidden border-2 border-slate-200 hover:border-indigo-400 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <img
                src={`data:image/jpeg;base64,${img.base64_data}`}
                alt={img.concept}
                className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
              <div className="p-2 bg-slate-50 text-center">
                <p className="text-xs font-medium text-slate-600 capitalize truncate">
                  {img.concept}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Lightbox */}
      {selected && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="relative max-w-3xl w-full bg-white rounded-2xl overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={`data:image/jpeg;base64,${selected.base64_data}`}
              alt={selected.concept}
              className="w-full max-h-[75vh] object-contain"
            />
            <div className="p-4 flex items-center justify-between">
              <p className="font-semibold text-slate-800 capitalize">{selected.concept}</p>
              <button
                onClick={() => setSelected(null)}
                className="btn-secondary text-sm py-1.5 px-3"
              >
                Close ✕
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
