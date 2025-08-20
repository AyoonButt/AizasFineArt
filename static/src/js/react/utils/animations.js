// Framer Motion animation utilities and presets

// Common easing curves
export const easings = {
  spring: { type: "spring", stiffness: 300, damping: 24 },
  smooth: { type: "spring", stiffness: 260, damping: 20 },
  bouncy: { type: "spring", stiffness: 400, damping: 10 },
  snappy: { type: "spring", stiffness: 500, damping: 30 },
  gentle: { type: "spring", stiffness: 200, damping: 25 }
};

// Common animation variants
export const fadeVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: easings.smooth
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.2 }
  }
};

export const slideUpVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: { duration: 0.2 }
  }
};

export const slideDownVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    y: 20,
    transition: { duration: 0.2 }
  }
};

export const slideInFromLeftVariants = {
  hidden: { opacity: 0, x: -30 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    x: -30,
    transition: { duration: 0.2 }
  }
};

export const slideInFromRightVariants = {
  hidden: { opacity: 0, x: 30 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    x: 30,
    transition: { duration: 0.2 }
  }
};

export const scaleVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    scale: 0.9,
    transition: { duration: 0.2 }
  }
};

export const popVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: easings.bouncy
  },
  exit: { 
    opacity: 0, 
    scale: 0.8,
    transition: { duration: 0.15 }
  }
};

// Stagger container variants
export const staggerContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
      ...easings.smooth
    }
  }
};

export const staggerItemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: easings.spring
  }
};

// Gallery specific animations
export const galleryGridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3
    }
  }
};

export const artworkCardVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.9 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: easings.spring
  },
  hover: {
    y: -8,
    scale: 1.02,
    transition: easings.snappy
  }
};

// Form animations
export const formContainerVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
      ...easings.spring
    }
  }
};

export const formFieldVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: easings.spring
  }
};

// Navigation animations
export const navVariants = {
  hidden: { y: -100, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      ...easings.spring
    }
  }
};

export const navItemVariants = {
  hidden: { y: -20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: easings.spring
  }
};

// Loading animations
export const loadingVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    scale: 0.8,
    transition: { duration: 0.2 }
  }
};

// Error/success message animations
export const messageVariants = {
  hidden: { opacity: 0, scale: 0.95, y: -10 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: easings.spring
  },
  exit: { 
    opacity: 0, 
    scale: 0.95, 
    y: -10,
    transition: { duration: 0.2 }
  }
};

// Modal animations
export const modalOverlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 }
};

export const modalContentVariants = {
  hidden: {
    opacity: 0,
    scale: 0.9,
    y: 20
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: easings.spring
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    y: 20,
    transition: { duration: 0.2 }
  }
};

// Utility functions
export const createStaggerVariants = (staggerDelay = 0.1, childDelay = 0.2) => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren: childDelay
    }
  }
});

export const createShakeVariants = (intensity = 3) => ({
  shake: {
    x: [-intensity, intensity, -intensity, intensity, 0],
    transition: { duration: 0.4 }
  }
});

export const createPulseVariants = (scale = 1.05) => ({
  pulse: {
    scale: [1, scale, 1],
    transition: { duration: 0.6, repeat: Infinity }
  }
});

// Hover effects
export const hoverEffects = {
  lift: {
    y: -5,
    transition: easings.snappy
  },
  scale: {
    scale: 1.05,
    transition: easings.snappy
  },
  glow: {
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
    transition: easings.smooth
  },
  tilt: {
    rotateY: 5,
    rotateX: 5,
    transition: easings.snappy
  }
};

// Tap effects
export const tapEffects = {
  scale: {
    scale: 0.95,
    transition: { duration: 0.1 }
  },
  push: {
    scale: 0.98,
    y: 1,
    transition: { duration: 0.1 }
  }
};