'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getCart } from '@/lib/api';

export default function Header() {
  const [cartCount, setCartCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    getCart()
      .then((cart) => setCartCount(cart.item_count))
      .catch(() => setCartCount(0));
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="text-xl font-light tracking-wide text-gray-900">
            Matthew Raynor
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/collections" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Collections
            </Link>
            <Link href="/photos" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Shop All
            </Link>
            <Link href="/about" className="text-sm text-gray-600 hover:text-gray-900 transition">
              About
            </Link>
            <Link href="/contact" className="text-sm text-gray-600 hover:text-gray-900 transition">
              Contact
            </Link>
            <Link href="/cart" className="relative text-sm text-gray-600 hover:text-gray-900 transition">
              Cart
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-4 bg-blue-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <div className="flex flex-col space-y-4">
              <Link href="/collections" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Collections
              </Link>
              <Link href="/photos" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Shop All
              </Link>
              <Link href="/about" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                About
              </Link>
              <Link href="/contact" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Contact
              </Link>
              <Link href="/cart" className="text-gray-600 hover:text-gray-900" onClick={() => setMobileMenuOpen(false)}>
                Cart {cartCount > 0 && `(${cartCount})`}
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
