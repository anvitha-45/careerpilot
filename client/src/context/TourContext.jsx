import React, { createContext, useContext, useState, useEffect } from 'react';

const TourContext = createContext(null);

export const TourProvider = ({ children }) => {
  const [isTourOpen, setIsTourOpen] = useState(false);
  const [isOfferOpen, setIsOfferOpen] = useState(false);

  useEffect(() => {
    // When a user opens the app, check if they have already been offered the tour
    const tourOffered = localStorage.getItem('careerpilot_tour_offered');
    if (!tourOffered) {
      // Offer the tour automatically after a short delay (700ms) on first visit
      const timer = setTimeout(() => {
        setIsOfferOpen(true);
      }, 700);
      return () => clearTimeout(timer);
    }
  }, []);

  const startTour = () => {
    setIsOfferOpen(false);
    setIsTourOpen(true);
    localStorage.setItem('careerpilot_tour_offered', 'true');
  };

  const dismissOffer = () => {
    setIsOfferOpen(false);
    localStorage.setItem('careerpilot_tour_offered', 'true');
  };

  const closeTour = () => {
    setIsTourOpen(false);
    localStorage.setItem('careerpilot_tour_offered', 'true');
    localStorage.setItem('careerpilot_tour_completed', 'true');
  };

  const restartTour = () => {
    setIsOfferOpen(false);
    setIsTourOpen(true);
  };

  const resetTourPreferences = () => {
    localStorage.removeItem('careerpilot_tour_offered');
    localStorage.removeItem('careerpilot_tour_completed');
    setIsOfferOpen(true);
  };

  return (
    <TourContext.Provider
      value={{
        isTourOpen,
        isOfferOpen,
        startTour,
        dismissOffer,
        closeTour,
        restartTour,
        resetTourPreferences,
        setIsTourOpen,
        setIsOfferOpen
      }}
    >
      {children}
    </TourContext.Provider>
  );
};

export const useTour = () => {
  const context = useContext(TourContext);
  if (!context) {
    throw new Error('useTour must be used within a TourProvider');
  }
  return context;
};
