import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../test-utils';
import '@testing-library/jest-dom';
import UserSection from '../UserSection';

describe('UserSection', () => {
  const mockSetFirstName = jest.fn();
  const mockSetLastName = jest.fn();
  const mockSetEmail = jest.fn();
  const mockSetPhone = jest.fn();
  const mockCreateUser = jest.fn();

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
      if (key === 'userId') return 'test-user-id';
      return null;
    });
    
    // Clear cookies
    document.cookie = '';
    
    // Mock fetch API
    global.fetch = jest.fn();
  });
  
  afterEach(() => {
    jest.resetAllMocks();
  });

  const renderComponent = (props = {}) => {
    return render(
      <UserSection
        firstName=""
        setFirstName={mockSetFirstName}
        lastName=""
        setLastName={mockSetLastName}
        email=""
        setEmail={mockSetEmail}
        phone=""
        setPhone={mockSetPhone}
        createUser={mockCreateUser}
        businessId="test-business-id"
        {...props}
      />
    );
  };

  it('renders user section with correct title', () => {
    renderComponent();
    expect(screen.getByText('User Management')).toBeInTheDocument();
  });

  it('updates first name on input change', () => {
    renderComponent();
    const input = screen.getByLabelText('First Name');
    fireEvent.change(input, { target: { value: 'John' } });
    expect(mockSetFirstName).toHaveBeenCalledWith('John');
  });

  it('renders create user button', () => {
    renderComponent();
    expect(screen.getByRole('button', { name: 'Create User' })).toBeInTheDocument();
  });
  
  it('includes business ID when creating a user', async () => {
    renderComponent();
    
    // Fill form fields
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'john@example.com' } });
    fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '555-1234' } });
    
    // Mock successful API response
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ user_id: 'new-user-id' })
      })
    );
    
    // Click create button
    fireEvent.click(screen.getByRole('button', { name: 'Create User' }));
    
    // Verify createUser was called with business ID
    await waitFor(() => {
      expect(mockCreateUser).toHaveBeenCalledWith(
        expect.objectContaining({
          business_id: 'test-business-id'
        })
      );
    });
  });
  
  it('falls back to localStorage business ID when not in props', async () => {
    renderComponent({ businessId: undefined });
    
    // Fill form fields
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } });
    
    // Click create button
    fireEvent.click(screen.getByRole('button', { name: 'Create User' }));
    
    // Verify createUser was called with business ID from localStorage
    await waitFor(() => {
      expect(mockCreateUser).toHaveBeenCalledWith(
        expect.objectContaining({
          business_id: 'test-business-id'
        })
      );
    });
  });
  
  it('shows error when no business ID is available', async () => {
    // Mock localStorage to return no business ID
    window.localStorage.getItem.mockImplementation(() => null);
    
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    renderComponent({ businessId: undefined });
    
    // Click create button without a business ID
    fireEvent.click(screen.getByRole('button', { name: 'Create User' }));
    
    // Verify error is logged
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Business ID is required'));
    });
    
    // Clean up
    consoleSpy.mockRestore();
  });
  
  it('loads user info when userId is available', async () => {
    // Mock API response
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ 
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '555-1234'
        })
      })
    );
    
    renderComponent();
    
    // Verify user info is fetched and state is updated
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/users/test-user-id'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'test-api-key'
          })
        })
      );
      
      expect(mockSetFirstName).toHaveBeenCalledWith('John');
      expect(mockSetLastName).toHaveBeenCalledWith('Doe');
      expect(mockSetEmail).toHaveBeenCalledWith('john@example.com');
      expect(mockSetPhone).toHaveBeenCalledWith('555-1234');
    });
  });
});