import React from 'react'

export default function AudioContent({ audioBase64 }) {
  if (!audioBase64) return null

  const src = `data:audio/mpeg;base64,${audioBase64}`

  return (
    <div className="card animate-fade-in">
      <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        🔊 Voice Narration
      </h2>
      <p className="text-sm text-slate-500 mb-4">
        Listen to an AI-narrated summary of this module.
      </p>
      <audio
        controls
        className="w-full"
        preload="metadata"
      >
        <source src={src} type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>

      {/* Download link */}
      <a
        href={src}
        download="narration.mp3"
        className="inline-flex items-center gap-1.5 mt-3 text-sm text-indigo-600 hover:underline"
      >
        ⬇ Download MP3
      </a>
    </div>
  )
}
