import Image from 'next/image'
import Link from 'next/link'
import { Play, Info } from 'lucide-react'

interface MovieCardProps {
  id: number
  title: string
  posterPath: string
  backdropPath?: string
  overview?: string
  rating?: number
  releaseDate?: string
  mediaType?: 'movie' | 'tv'
}

export default function MovieCard({
  id,
  title,
  posterPath,
  backdropPath,
  overview,
  rating,
  releaseDate,
  mediaType = 'movie',
}: MovieCardProps) {
  const imageUrl = posterPath 
    ? `https://image.tmdb.org/t/p/w500${posterPath}`
    : '/placeholder-poster.jpg'

  return (
    <Link href={`/${mediaType}/${id}`} className="movie-card relative group">
      <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-surface">
        <Image
          src={imageUrl}
          alt={title}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 50vw, (max-width: 1200px) 25vw, 15vw"
        />
        
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
          <h3 className="text-white font-semibold text-sm mb-2 line-clamp-2">
            {title}
          </h3>
          
          {rating && (
            <div className="flex items-center space-x-2 text-xs text-gray-300 mb-3">
              <span className="text-green-500">{(rating * 10).toFixed(0)}% Match</span>
              {releaseDate && (
                <span>{new Date(releaseDate).getFullYear()}</span>
              )}
            </div>
          )}
          
          <div className="flex space-x-2">
            <button className="flex-1 bg-primary hover:bg-primary-light text-white px-4 py-2 rounded-md text-xs font-semibold flex items-center justify-center space-x-1 transition-colors">
              <Play className="w-4 h-4" fill="currentColor" />
              <span>Play</span>
            </button>
            <button className="bg-surface-light hover:bg-surface text-white px-3 py-2 rounded-md text-xs font-semibold transition-colors">
              <Info className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </Link>
  )
}
