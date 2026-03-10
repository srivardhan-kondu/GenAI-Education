import React from 'react'

export default function VideoContent({ videos }) {
    const available = videos?.filter((v) => v.base64_data) ?? []

    if (available.length === 0) {
        return (
            <div className="card text-center py-12 text-slate-400">
                <p className="text-4xl mb-2">🎬</p>
                <p className="font-medium">No videos generated for this module.</p>
                <p className="text-sm mt-1">
                    Enable video generation when creating a module to see concept animations here.
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-semibold text-slate-800">
                🎬 Concept Videos
            </h3>
            <div className="grid grid-cols-1 gap-6">
                {available.map((video, idx) => (
                    <div key={idx} className="card overflow-hidden !p-0">
                        <video
                            controls
                            className="w-full rounded-t-2xl bg-black"
                            style={{ maxHeight: '500px' }}
                        >
                            <source
                                src={`data:video/mp4;base64,${video.base64_data}`}
                                type="video/mp4"
                            />
                            Your browser does not support the video tag.
                        </video>
                        <div className="px-5 py-3 flex items-center justify-between">
                            <p className="text-sm font-medium text-slate-700">
                                🏷 {video.concept}
                            </p>
                            <a
                                href={`data:video/mp4;base64,${video.base64_data}`}
                                download={`${video.concept}.mp4`}
                                className="text-xs text-indigo-600 hover:underline"
                            >
                                ⬇ Download
                            </a>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
