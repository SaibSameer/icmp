import React from 'react';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { render } from '../../test-utils';
import '@testing-library/jest-dom';
import BusinessSection from '../BusinessSection';

// Mock the useBusiness hook
jest.mock('../../hooks/useBusiness', () => ({
  __esModule: true,
  default: jest.fn()
}));

describe('BusinessSection', () => {
  const mockHandleSnackbarOpen = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
      },
      writable: true
    });
    
    // Mock localStorage to return a valid business ID
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Clear cookies
    document.cookie = '';
  });

  it('displays loading state initially', async () => {
    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: null,
      isLoading: true,
      error: null
    }));

    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    await screen.findByTestId('loading-state');
  });

  it('renders business details when loaded', async () => {
    const mockBusinessDetails = {
      business_name: 'Test Business',
      address: '123 Test St',
      phone: '123-456-7890',
      email: 'test@business.com'
    };

    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: mockBusinessDetails,
      isLoading: false,
      error: null
    }));

    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    await screen.findByTestId('business-details');
    expect(screen.getByText(mockBusinessDetails.business_name)).toBeInTheDocument();
  });

  it('renders error state', async () => {
    const errorMessage = 'Failed to load business details';
    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: null,
      isLoading: false,
      error: errorMessage
    }));

    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    await screen.findByTestId('error-state');
    expect(screen.getByText(new RegExp(errorMessage))).toBeInTheDocument();
  });

  it('renders empty state when no details available', async () => {
    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: null,
      isLoading: false,
      error: null
    }));

    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    await screen.findByTestId('empty-state');
  });
  
  it('passes business ID from localStorage to useBusiness hook', async () => {
    // Spy on the useBusiness hook
    const useBusiness = require('../../hooks/useBusiness').default;
    
    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    
    // Verify hook was called with business ID from localStorage
    expect(useBusiness).toHaveBeenCalledWith('test-business-id');
  });
  
  it('shows credential error when business ID is missing', async () => {
    // Mock localStorage to return no business ID
    window.localStorage.getItem.mockImplementation(() => null);
    
    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: null,
      isLoading: false,
      error: 'Business ID is required'
    }));
    
    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    
    // Verify error message
    await waitFor(() => {
      expect(mockHandleSnackbarOpen).toHaveBeenCalledWith(
        'Business ID is required. Please check your configuration.',
        'error'
      );
    });
  });
  
  it('handles refresh button click', async () => {
    const mockRefresh = jest.fn();
    
    require('../../hooks/useBusiness').default.mockImplementation(() => ({
      businessDetails: null,
      isLoading: false,
      error: 'Failed to load',
      refreshBusinessDetails: mockRefresh
    }));
    
    render(<BusinessSection handleSnackbarOpen={mockHandleSnackbarOpen} />);
    
    // Find and click refresh button
    const refreshButton = await screen.findByTestId('refresh-button');
    fireEvent.click(refreshButton);
    
    // Verify refresh function was called
    expect(mockRefresh).toHaveBeenCalled();
  });
});