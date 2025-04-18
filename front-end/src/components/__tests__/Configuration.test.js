import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../test-utils';
import '@testing-library/jest-dom';
import Configuration from '../Configuration';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('Configuration Component', () => {
  let mockProps;
  
  beforeEach(() => {
    mockProps = {
      userId: '',
      setUserId: jest.fn(),
      businessId: '',
      setBusinessId: jest.fn(),
      businessApiKey: '',
      setBusinessApiKey: jest.fn(),
      handleSnackbarOpen: jest.fn(),
      handleLogout: jest.fn()
    };
    jest.clearAllMocks();
    global.fetch = jest.fn();
    
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
    
    // Clear cookies
    document.cookie = '';
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const renderWithProps = (props = mockProps) => {
    return render(<Configuration {...props} />);
  };

  it('renders remaining input fields', async () => {
    renderWithProps();

    const businessKeyInput = await screen.findByTestId('business-api-key-input');
    const userIdInput = await screen.findByTestId('user-id-input');
    const businessIdInput = await screen.findByTestId('business-id-input');

    expect(businessKeyInput).toBeInTheDocument();
    expect(userIdInput).toBeInTheDocument();
    expect(businessIdInput).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderWithProps();

    await waitFor(() => {
      fireEvent.click(screen.getByText(/Save Config/i));
    });

    expect(mockProps.handleSnackbarOpen).toHaveBeenCalledWith(
      'Please enter all the configuration values',
      'warning'
    );
  });

  it('handles successful configuration validation', async () => {
    const mockResponse = { ok: true, json: () => Promise.resolve({ success: true }) };
    global.fetch.mockImplementationOnce(() => Promise.resolve(mockResponse));

    const filledProps = {
      ...mockProps,
      userId: 'test_user',
      businessId: 'test_business',
      businessApiKey: 'test_business_key'
    };

    renderWithProps(filledProps);

    await waitFor(() => {
      fireEvent.click(screen.getByText(/Save Config/i));
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/save-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        userId: 'test_user',
        businessId: 'test_business',
        businessApiKey: 'test_business_key'
      })
    });

    expect(mockProps.handleSnackbarOpen).toHaveBeenCalledWith(
      'Configuration saved successfully',
      'success'
    );
    expect(mockNavigate).toHaveBeenCalledWith('/business');
    
    // Verify credentials are stored in localStorage
    await waitFor(() => {
      expect(window.localStorage.setItem).toHaveBeenCalledWith('businessId', 'test_business');
      expect(window.localStorage.setItem).toHaveBeenCalledWith('businessApiKey', 'test_business_key');
      expect(window.localStorage.setItem).toHaveBeenCalledWith('userId', 'test_user');
    });
  });

  it('handles configuration validation error', async () => {
    const mockResponse = { ok: false, json: () => Promise.resolve({ message: 'Invalid credentials' }) };
    global.fetch.mockImplementationOnce(() => Promise.resolve(mockResponse));

    const filledProps = {
      ...mockProps,
      userId: 'test_user',
      businessId: 'test_business',
      businessApiKey: 'test_business_key'
    };

    renderWithProps(filledProps);

    await waitFor(() => {
      fireEvent.click(screen.getByText(/Save Config/i));
    });

    expect(mockProps.handleSnackbarOpen).toHaveBeenCalledWith(
      'Invalid credentials',
      'error'
    );
    
    // Ensure localStorage is not called when validation fails
    expect(window.localStorage.setItem).not.toHaveBeenCalled();
  });

  it('handles logout correctly', async () => {
    renderWithProps();

    await waitFor(() => {
      fireEvent.click(screen.getByText(/Logout/i));
    });

    expect(mockProps.handleLogout).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
    
    // Ensure logout clears credentials from localStorage
    expect(window.localStorage.removeItem).toHaveBeenCalledTimes(3);
  });
  
  it('loads saved credentials from localStorage on mount', async () => {
    // Mock localStorage to return saved credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'saved_business_id';
      if (key === 'businessApiKey') return 'saved_api_key';
      if (key === 'userId') return 'saved_user_id';
      return null;
    });
    
    renderWithProps();
    
    // Verify props are updated with stored values
    await waitFor(() => {
      expect(mockProps.setBusinessId).toHaveBeenCalledWith('saved_business_id');
      expect(mockProps.setBusinessApiKey).toHaveBeenCalledWith('saved_api_key');
      expect(mockProps.setUserId).toHaveBeenCalledWith('saved_user_id');
    });
  });
});