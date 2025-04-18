import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../test-utils';
import '@testing-library/jest-dom';
import TemplateSection from '../TemplateSection';

// Mock console.log to suppress useEffect logs
const originalConsoleLog = console.log;
beforeAll(() => {
  console.log = jest.fn();
});

afterAll(() => {
  console.log = originalConsoleLog;
});

// Mock API calls
jest.mock('../../services/api', () => ({
  createTemplate: jest.fn(),
  fetchTemplateDetails: jest.fn(),
}));

describe('TemplateSection', () => {
  const mockSetTemplateID = jest.fn();
  const mockSetTemplateName = jest.fn();
  const mockSetTemplateText = jest.fn();
  const mockCreateTemplate = jest.fn();

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

  const renderComponent = (props = {}) => {
    return render(
      <TemplateSection
        templateID=""
        setTemplateID={mockSetTemplateID}
        templateName=""
        setTemplateName={mockSetTemplateName}
        templateText=""
        setTemplateText={mockSetTemplateText}
        createTemplate={mockCreateTemplate}
        businessId="test-business-id"
        {...props}
      />
    );
  };

  it('renders template section with correct title', async () => {
    renderComponent();
    expect(await screen.findByTestId('template-section-title')).toHaveTextContent('Template Management');
  });

  it('renders template ID input field', async () => {
    renderComponent();
    expect(await screen.findByTestId('template-id-input')).toBeInTheDocument();
  });

  it('updates template ID when input changes', async () => {
    renderComponent();
    const input = await screen.findByTestId('template-id-input');
    const inputElement = input.querySelector('input');
    await waitFor(() => {
      fireEvent.change(inputElement, { target: { value: 'test-template' } });
    });
    expect(mockSetTemplateID).toHaveBeenCalledWith('test-template');
  });

  it('renders template text textarea', async () => {
    renderComponent();
    expect(await screen.findByTestId('template-text-input')).toBeInTheDocument();
  });

  it('updates template content when textarea changes', async () => {
    renderComponent();
    const textareaContainer = await screen.findByTestId('template-text-input');
    const textareaElement = textareaContainer.querySelector('textarea');
    await waitFor(() => {
      fireEvent.change(textareaElement, { target: { value: 'Test content' } });
    });
    expect(mockSetTemplateText).toHaveBeenCalledWith('Test content');
  });

  it('renders create template button', async () => {
    renderComponent();
    expect(await screen.findByTestId('create-template-button')).toHaveTextContent('Create Template');
  });

  it('calls createTemplate when create button is clicked', async () => {
    renderComponent();
    const button = await screen.findByTestId('create-template-button');
    fireEvent.click(button);
    expect(mockCreateTemplate).toHaveBeenCalled();
  });
  
  it('checks for business ID in localStorage before template operations', async () => {
    // Mock localStorage to return no business ID
    window.localStorage.getItem.mockImplementation(() => null);
    
    const component = renderComponent();
    const button = await screen.findByTestId('create-template-button');
    
    // Create a spy on the console.error method
    const consoleSpy = jest.spyOn(console, 'error');
    
    // Click create button without a business ID
    fireEvent.click(button);
    
    // Verify error is logged
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Business ID is required'));
    
    // Clean up
    consoleSpy.mockRestore();
  });
  
  it('includes business ID from props when creating template', async () => {
    renderComponent({ businessId: 'custom-business-id' });
    const button = await screen.findByTestId('create-template-button');
    
    fireEvent.click(button);
    
    // Verify createTemplate was called with business ID
    expect(mockCreateTemplate).toHaveBeenCalledWith(
      expect.objectContaining({
        business_id: 'custom-business-id'
      })
    );
  });
  
  it('falls back to localStorage business ID when not in props', async () => {
    renderComponent({ businessId: undefined });
    const button = await screen.findByTestId('create-template-button');
    
    fireEvent.click(button);
    
    // Verify createTemplate was called with business ID from localStorage
    expect(mockCreateTemplate).toHaveBeenCalledWith(
      expect.objectContaining({
        business_id: 'test-business-id'
      })
    );
  });
});