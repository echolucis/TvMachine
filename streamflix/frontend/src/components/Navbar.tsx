'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Play, Tv, Film, Search, Menu, X, User, Home } from 'lucide-react'

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      isScrolled ? 'bg-background/95 backdrop-blur-sm shadow-lg' : 'bg-gradient-to-b from-black/80 to-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <Play className="w-8 h-8 text-primary" fill="currentColor" />
            <span className="text-2xl font-bold text-primary">StreamFlix</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-1 text-white hover:text-primary transition-colors">
              <Home className="w-5 h-5" />
              <span>Home</span>
            </Link>
            <Link href="/movies" className="flex items-center space-x-1 text-gray-300 hover:text-primary transition-colors">
              <Film className="w-5 h-5" />
              <span>Movies</span>
            </Link>
            <Link href="/tv" className="flex items-center space-x-1 text-gray-300 hover:text-primary transition-colors">
              <Tv className="w-5 h-5" />
              <span>TV Shows</span>
            </Link>
            <Link href="/live-tv" className="flex items-center space-x-1 text-gray-300 hover:text-primary transition-colors">
              <Tv className="w-5 h-5" />
              <span>Live TV</span>
            </Link>
            <Link href="/my-list" className="flex items-center space-x-1 text-gray-300 hover:text-primary transition-colors">
              <User className="w-5 h-5" />
              <span>My List</span>
            </Link>
          </div>

          {/* Search and Mobile Menu */}
          <div className="flex items-center space-x-4">
            <button className="text-gray-300 hover:text-white transition-colors">
              <Search className="w-6 h-6" />
            </button>
            
            <button 
              className="md:hidden text-gray-300 hover:text-white"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-surface border-t border-surface-light">
          <div className="px-4 py-4 space-y-4">
            <Link href="/" className="flex items-center space-x-2 text-white hover:text-primary transition-colors">
              <Home className="w-5 h-5" />
              <span>Home</span>
            </Link>
            <Link href="/movies" className="flex items-center space-x-2 text-gray-300 hover:text-primary transition-colors">
              <Film className="w-5 h-5" />
              <span>Movies</span>
            </Link>
            <Link href="/tv" className="flex items-center space-x-2 text-gray-300 hover:text-primary transition-colors">
              <Tv className="w-5 h-5" />
              <span>TV Shows</span>
            </Link>
            <Link href="/live-tv" className="flex items-center space-x-2 text-gray-300 hover:text-primary transition-colors">
              <Tv className="w-5 h-5" />
              <span>Live TV</span>
            </Link>
            <Link href="/my-list" className="flex items-center space-x-2 text-gray-300 hover:text-primary transition-colors">
              <User className="w-5 h-5" />
              <span>My List</span>
            </Link>
          </div>
        </div>
      )}
    </nav>
  )
}
