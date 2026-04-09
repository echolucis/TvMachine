'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Play, Info } from 'lucide-react'
import Navbar from '../components/Navbar'
import ContentRow from '../components/ContentRow'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export default function Home() {
  const [trending, setTrending] = useState<any[]>([])
  const [popularMovies, setPopularMovies] = useState<any[]>([])
  const [popularTV, setPopularTV] = useState<any[]>([])
  const [topRated, setTopRated] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [heroContent, setHeroContent] = useState<any>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch trending content for hero
        const trendingRes = await fetch(`${API_URL}/content/trending?time_window=week`)
        const trendingData = await trendingRes.json()
        setTrending(trendingData.results || [])
        
        if (trendingData.results && trendingData.results.length > 0) {
          setHeroContent(trendingData.results[0])
        }

        // Fetch popular movies
        const moviesRes = await fetch(`${API_URL}/content/movies?page=1`)
        const moviesData = await moviesRes.json()
        setPopularMovies(moviesData.results || [])

        // Fetch popular TV shows
        const tvRes = await fetch(`${API_URL}/content/tv?page=1`)
        const tvData = await tvRes.json()
        setPopularTV(tvData.results || [])

        // Fetch top rated
        const topRatedRes = await fetch(`${API_URL}/content/movies?page=2`)
        const topRatedData = await topRatedRes.json()
        setTopRated(topRatedData.results || [])

        setLoading(false)
      } catch (error) {
        console.error('Error fetching data:', error)
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      {heroContent && (
        <section className="relative h-[80vh] w-full">
          <div className="absolute inset-0">
            <Image
              src={`https://image.tmdb.org/t/p/original${heroContent.backdrop_path}`}
              alt={heroContent.title || heroContent.name}
              fill
              className="object-cover"
              priority
            />
            <div className="hero-overlay absolute inset-0" />
          </div>

          <div className="relative z-10 h-full flex items-center max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl">
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
                {heroContent.title || heroContent.name}
              </h1>
              
              <p className="text-lg text-gray-200 mb-6 line-clamp-3">
                {heroContent.overview}
              </p>

              <div className="flex space-x-4">
                <Link
                  href={`/${heroContent.media_type === 'tv' ? 'tv' : 'movies'}/${heroContent.id}`}
                  className="bg-primary hover:bg-primary-light text-white px-8 py-3 rounded-md font-semibold flex items-center space-x-2 transition-colors"
                >
                  <Play className="w-5 h-5" fill="currentColor" />
                  <span>Play Now</span>
                </Link>
                
                <button className="bg-surface-light/80 hover:bg-surface-light text-white px-8 py-3 rounded-md font-semibold flex items-center space-x-2 transition-colors backdrop-blur-sm">
                  <Info className="w-5 h-5" />
                  <span>More Info</span>
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Content Rows */}
      <div className="-mt-32 relative z-20 space-y-8 pb-16">
        {trending.length > 0 && (
          <ContentRow 
            title="🔥 Trending This Week" 
            movies={trending.slice(0, 12)} 
          />
        )}

        {popularMovies.length > 0 && (
          <ContentRow 
            title="🎬 Popular Movies" 
            movies={popularMovies} 
          />
        )}

        {popularTV.length > 0 && (
          <ContentRow 
            title="📺 Popular TV Shows" 
            movies={popularTV} 
          />
        )}

        {topRated.length > 0 && (
          <ContentRow 
            title="⭐ Top Rated" 
            movies={topRated} 
          />
        )}
      </div>
    </main>
  )
}
