import MovieCard from './MovieCard'

interface ContentRowProps {
  title: string
  movies: Array<{
    id: number
    title: string
    poster_path: string
    backdrop_path?: string
    overview?: string
    vote_average?: number
    release_date?: string
    first_air_date?: string
    media_type?: 'movie' | 'tv'
  }>
}

export default function ContentRow({ title, movies }: ContentRowProps) {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-white mb-4 px-4 sm:px-6 lg:px-8">{title}</h2>
      
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 px-4 sm:px-6 lg:px-8">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            id={movie.id}
            title={movie.title || movie.name || ''}
            posterPath={movie.poster_path || ''}
            backdropPath={movie.backdrop_path}
            overview={movie.overview}
            rating={movie.vote_average}
            releaseDate={movie.release_date || movie.first_air_date}
            mediaType={movie.media_type || 'movie'}
          />
        ))}
      </div>
    </div>
  )
}
