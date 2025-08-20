import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = ({ 
  currentPage = '',
  user = null,
  cartCount = 0,
  wishlistCount = 0 
}) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Animation variants
  const navVariants = {
    hidden: { y: -100, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: -20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  const mobileMenuVariants = {
    hidden: {
      opacity: 0,
      y: -20,
      scale: 0.95,
      transition: { duration: 0.2 }
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        staggerChildren: 0.1
      }
    }
  };

  const userMenuVariants = {
    hidden: {
      opacity: 0,
      scale: 0.95,
      y: -10,
      transition: { duration: 0.15 }
    },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25
      }
    }
  };

  const navigation = [
    { name: 'Home', href: '/', key: 'home' },
    { name: 'Portfolio', href: '/portfolio/', key: 'portfolio' },
    { name: 'Shop', href: '/shop/', key: 'shop' },
    { name: 'About', href: '/about/', key: 'about' },
    { name: 'Contact', href: '/contact/', key: 'contact' }
  ];

  const NavLink = ({ href, children, isActive, className = '', onClick }) => (
    <motion.a
      href={href}
      className={`nav-link ${isActive ? 'nav-link-active' : ''} ${className}`}
      variants={itemVariants}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
    >
      {children}
    </motion.a>
  );

  const IconButton = ({ children, onClick, className = '', count = null }) => (
    <motion.button
      className={`p-2 text-neutral-700 hover:text-primary-600 transition-colors relative ${className}`}
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      {children}
      {count > 0 && (
        <motion.span
          className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          {count}
        </motion.span>
      )}
    </motion.button>
  );

  return (
    <motion.nav
      className={`navbar fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-neutral-200' 
          : 'bg-white/90 backdrop-blur-sm border-b border-neutral-100'
      }`}
      variants={navVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div className="flex-shrink-0" variants={itemVariants}>
            <a href="/" className="flex items-center space-x-2">
              <motion.div 
                className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
              >
                <span className="text-white font-playfair font-bold text-lg">A</span>
              </motion.div>
              <div className="hidden sm:block">
                <h1 className="font-playfair font-semibold text-xl text-neutral-800">
                  Aiza's Fine Art
                </h1>
                <p className="text-xs text-neutral-600 -mt-1">Fort Worth, Texas</p>
              </div>
            </a>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <NavLink
                key={item.key}
                href={item.href}
                isActive={currentPage === item.key}
              >
                {item.name}
              </NavLink>
            ))}
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            {/* Search (hidden on small screens) */}
            <motion.div className="hidden lg:block" variants={itemVariants}>
              <form action="/search/" method="get" className="relative">
                <motion.input
                  type="search"
                  name="q"
                  placeholder="Search artworks..."
                  className="w-48 pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                  whileFocus={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300, damping: 24 }}
                />
                <svg className="absolute left-3 top-2.5 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </form>
            </motion.div>

            {/* User Menu or Auth Links */}
            {user ? (
              <motion.div className="relative" variants={itemVariants}>
                <motion.button
                  className="flex items-center space-x-2 text-neutral-700 hover:text-primary-500 transition-colors"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 text-sm font-medium">
                      {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <span className="hidden sm:block">
                    {user.first_name || user.username}
                  </span>
                  <motion.svg 
                    className="w-4 h-4"
                    animate={{ rotate: isUserMenuOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                  </motion.svg>
                </motion.button>
                
                {/* User Dropdown */}
                <AnimatePresence>
                  {isUserMenuOpen && (
                    <motion.div
                      className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-50"
                      variants={userMenuVariants}
                      initial="hidden"
                      animate="visible"
                      exit="hidden"
                      onMouseLeave={() => setIsUserMenuOpen(false)}
                    >
                      <div className="py-1">
                        <a href="/dashboard/" className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">Dashboard</a>
                        <a href="/profile/" className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">Profile</a>
                        <a href="/orders/" className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">Orders</a>
                        <a href="/wishlist/" className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">Wishlist</a>
                        <div className="border-t border-neutral-100 mt-1 pt-1">
                          <form method="post" action="/logout/">
                            <input type="hidden" name="csrfmiddlewaretoken" value={document.querySelector('[name=csrfmiddlewaretoken]')?.value} />
                            <button type="submit" className="block w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50">
                              Logout
                            </button>
                          </form>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ) : (
              <motion.div className="flex items-center space-x-4" variants={itemVariants}>
                <NavLink href="/login/">Login</NavLink>
                <NavLink href="/signup/" className="btn-primary">Sign Up</NavLink>
              </motion.div>
            )}

            {/* Cart/Wishlist Icons */}
            <motion.div className="flex items-center space-x-2" variants={itemVariants}>
              <IconButton count={wishlistCount}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                </svg>
              </IconButton>
              <IconButton count={cartCount}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.293 2.293A1 1 0 004 16v0a1 1 0 001 1h.01M6 20v.01M20 20v.01"></path>
                </svg>
              </IconButton>
            </motion.div>

            {/* Mobile Menu Button */}
            <motion.button
              className="md:hidden p-2 text-neutral-700 hover:text-primary-600"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              variants={itemVariants}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <motion.svg 
                className="w-6 h-6"
                animate={{ rotate: isMobileMenuOpen ? 90 : 0 }}
                transition={{ duration: 0.2 }}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </motion.svg>
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              className="md:hidden border-t border-neutral-200 bg-white"
              variants={mobileMenuVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              <div className="px-2 pt-2 pb-3 space-y-1">
                {navigation.map((item) => (
                  <motion.a
                    key={item.key}
                    href={item.href}
                    className={`block px-3 py-2 rounded-md text-base font-medium ${
                      currentPage === item.key
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-neutral-700 hover:text-primary-600 hover:bg-neutral-50'
                    }`}
                    variants={itemVariants}
                    onClick={() => setIsMobileMenuOpen(false)}
                    whileHover={{ x: 5 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    {item.name}
                  </motion.a>
                ))}
                
                {/* Mobile Search */}
                <motion.div className="px-3 py-2" variants={itemVariants}>
                  <form action="/search/" method="get" className="relative">
                    <input
                      type="search"
                      name="q"
                      placeholder="Search artworks..."
                      className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                    />
                    <svg className="absolute left-3 top-2.5 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                  </form>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  );
};

export default Navbar;