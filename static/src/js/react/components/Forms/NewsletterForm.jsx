import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const NewsletterForm = ({ endpoint = '/htmx/newsletter/' }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error'
  const [submitMessage, setSubmitMessage] = useState('');

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        staggerChildren: 0.1
      }
    }
  };

  const fieldVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, scale: 0.95, y: -5 },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    },
    exit: { 
      opacity: 0, 
      scale: 0.95, 
      y: -5,
      transition: { duration: 0.2 }
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) return;
    
    setIsSubmitting(true);
    setSubmitStatus(null);
    
    try {
      const response = await axios.post(endpoint, { email }, {
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value,
          'Content-Type': 'application/json'
        }
      });
      
      setSubmitStatus('success');
      setSubmitMessage('Thank you for subscribing! Check your email to confirm.');
      
      // Reset form after successful submission
      setTimeout(() => {
        setEmail('');
        setSubmitStatus(null);
      }, 4000);
      
    } catch (error) {
      setSubmitStatus('error');
      setSubmitMessage(
        error.response?.data?.message || 
        'There was an error subscribing. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="newsletter-form-container">
      {/* Success/Error Messages */}
      <AnimatePresence>
        {submitStatus && (
          <motion.div
            className={`mb-4 p-3 rounded-lg text-sm ${
              submitStatus === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
            variants={messageVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <div className="flex items-start">
              <motion.div
                initial={{ scale: 0, rotate: -90 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 24 }}
                className="mr-2 mt-0.5"
              >
                {submitStatus === 'success' ? (
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
              </motion.div>
              <span>{submitMessage}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Newsletter Form */}
      <motion.form
        onSubmit={handleSubmit}
        className="relative"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Loading overlay */}
        <AnimatePresence>
          {isSubmitting && (
            <motion.div
              className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10 rounded-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="w-5 h-5 border-2 border-primary-300 border-t-primary-600 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex flex-col sm:flex-row gap-3">
          {/* Email Input */}
          <motion.div className="flex-1" variants={fieldVariants}>
            <label htmlFor="newsletter-email" className="sr-only">
              Email address
            </label>
            <motion.input
              id="newsletter-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              className="form-input w-full"
              required
              disabled={isSubmitting}
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 24 }}
            />
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            className="btn-primary px-6 whitespace-nowrap relative overflow-hidden"
            disabled={isSubmitting || !email.trim()}
            variants={fieldVariants}
            whileHover={{ scale: isSubmitting ? 1 : 1.05 }}
            whileTap={{ scale: isSubmitting ? 1 : 0.95 }}
            transition={{ type: "spring", stiffness: 300, damping: 24 }}
          >
            <motion.span
              animate={isSubmitting ? { opacity: 0.7 } : { opacity: 1 }}
            >
              {isSubmitting ? 'Subscribing...' : 'Subscribe'}
            </motion.span>
          </motion.button>
        </div>

        {/* Privacy Notice */}
        <motion.p 
          className="text-xs text-neutral-500 mt-3"
          variants={fieldVariants}
        >
          By subscribing, you agree to receive newsletters about new artworks and exhibitions. 
          You can unsubscribe at any time. See our{' '}
          <a href="/privacy/" className="text-primary-600 hover:underline">
            Privacy Policy
          </a>.
        </motion.p>
      </motion.form>
    </div>
  );
};

export default NewsletterForm;