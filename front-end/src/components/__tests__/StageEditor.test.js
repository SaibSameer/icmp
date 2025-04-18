import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../test-utils';
import '@testing-library/jest-dom';
import StageEditor from '../StageEditor';

// Mock useNavigate and useParams
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ stageId: 'new' }),
  useLocation: () => ({
    search: '?business_id=test-business-id',
    state: {
      businessId: 'test-business-id',
      agentId: 'test-agent-id',
      isNewStage: true
    }
  })
}));

// Mock the API service
jest.mock('../../services/api', () => ({
  createTemplate: jest.fn(),
  fetchTemplateDetails: jest.fn(),
  apiService: {
    getStages: jest.fn(),
    createStage: jest.fn(),
    getBusinessDetails: jest.fn()
  },
  handleApiResponse: jest.fn()
}));

// Mock the cachedFetch utility
jest.mock('../../utils/fetchUtils', () => ({
  cachedFetch: jest.fn().mockImplementation((url, options) => {
    // Mock different responses based on the URL
    if (url.includes('/templates')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          {
            template_id: 'template1',
            template_name: 'Test Template',
            template_type: 'stage_selection',
            template_text: 'Test template text'
          }
        ])
      });
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve([])
    });
  })
}));

// Mock the fetch API
global.fetch = jest.fn();

// Helper to setup successful response
const mockSuccessResponse = (data) => {
  global.fetch.mockImplementationOnce(() => 
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data)
    })
  );
};

// Helper to setup failed response
const mockFailedResponse = (errorMessage) => {
  global.fetch.mockImplementationOnce(() => 
    Promise.resolve({
      ok: false,
      json: () => Promise.resolve({ message: errorMessage })
    })
  );
};

describe('StageEditor Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage and cookies
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
      },
      writable: true
    });
    
    document.cookie = '';
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('displays business credentials form when credentials are missing', async () => {
    // Mock localStorage to return no credentials
    window.localStorage.getItem.mockImplementation(() => null);
    
    await render(<StageEditor />);
    
    expect(screen.getByText('Business Credentials Required')).toBeInTheDocument();
    
    // Use getByPlaceholderText instead of getByLabelText for Material-UI inputs
    expect(screen.getByPlaceholderText('Enter your business ID')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your business API key')).toBeInTheDocument();
  });

  it('validates credentials before proceeding', async () => {
    // Mock localStorage to return no credentials
    window.localStorage.getItem.mockImplementation(() => null);
    
    await render(<StageEditor />);
    
    // Fill in credentials using placeholder text
    fireEvent.change(screen.getByPlaceholderText('Enter your business ID'), { 
      target: { value: 'test-business-id' } 
    });
    
    fireEvent.change(screen.getByPlaceholderText('Enter your business API key'), { 
      target: { value: 'test-api-key' } 
    });
    
    // Mock the validation response
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    // Click validate button
    fireEvent.click(screen.getByText('Validate & Save Credentials'));
    
    // Expect localStorage and cookie to be set
    await waitFor(() => {
      expect(window.localStorage.setItem).toHaveBeenCalledWith('businessId', 'test-business-id');
      expect(window.localStorage.setItem).toHaveBeenCalledWith('businessApiKey', 'test-api-key');
    });
  });

  it('shows appropriate error when validation fails', async () => {
    // Mock localStorage to return no credentials
    window.localStorage.getItem.mockImplementation(() => null);
    
    // Mock the validation response to fail
    mockFailedResponse('Invalid business ID or API key');
    
    await render(<StageEditor />);
    
    // Wait for the component to initialize
    await waitFor(() => {
      expect(screen.getByText('Business Credentials Required')).toBeInTheDocument();
    });
    
    // Fill in credentials using placeholder text
    fireEvent.change(screen.getByPlaceholderText('Enter your business ID'), { 
      target: { value: 'test-business-id' } 
    });
    
    fireEvent.change(screen.getByPlaceholderText('Enter your business API key'), { 
      target: { value: 'invalid-api-key' } 
    });
    
    // Click validate button
    fireEvent.click(screen.getByText('Validate & Save Credentials'));
    
    // Expect error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to validate credentials/)).toBeInTheDocument();
    });
  });

  it('loads templates when credentials are valid', async () => {
    // Mock localStorage to return valid credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Mock successful validation
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    await render(<StageEditor />);
    
    // Check that templates are loaded
    await waitFor(() => {
      expect(screen.getByText('Stage Information')).toBeInTheDocument();
    });
  });

  it('handles template selection and saving', async () => {
    // Mock localStorage to return valid credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Mock successful validation
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    await render(<StageEditor />);
    
    // Wait for component to initialize
    await waitFor(() => {
      expect(screen.getByText('Stage Information')).toBeInTheDocument();
    });
    
    // Select a template type using the tab
    const stageSelectionTab = screen.getByText('Stage Selection');
    fireEvent.click(stageSelectionTab);
    
    // Check if template options are displayed - use getAllByText and check the first one
    await waitFor(() => {
      const templateElements = screen.getAllByText('Template');
      expect(templateElements.length).toBeGreaterThan(0);
    });
  });

  it('shows appropriate error when template loading fails', async () => {
    // Mock localStorage to return valid credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Mock successful validation but failed template loading
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    // Override the cachedFetch mock for this test
    jest.spyOn(require('../../utils/fetchUtils'), 'cachedFetch')
      .mockImplementationOnce(() => Promise.reject(new Error('Failed to load templates')));
    
    await render(<StageEditor />);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch templates/)).toBeInTheDocument();
    });
  });

  it('saves a template successfully', async () => {
    // Mock localStorage to return valid credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Mock successful validation
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    // Mock templates fetch
    mockSuccessResponse([]);
    
    await render(<StageEditor />);
    
    // Wait for component to initialize
    await waitFor(() => {
      expect(screen.getByText('Stage Selection')).toBeInTheDocument();
    });
    
    // Enter template text
    fireEvent.change(screen.getByPlaceholderText('Enter template text with variables in {curly_braces}'), {
      target: { value: 'Test template content' }
    });
    
    // Mock successful template save
    mockSuccessResponse({ template_id: 'new-template-id' });
    
    // Click save template
    fireEvent.click(screen.getByText('Save Template'));
    
    // Confirm in dialog
    await waitFor(() => {
      expect(screen.getByText(/Are you sure you want to create a new/)).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Save'));
    
    // Check success message appears
    await waitFor(() => {
      expect(screen.getByText(/template saved successfully/)).toBeInTheDocument();
    });
  });

  it('creates a stage successfully', async () => {
    // Mock localStorage to return valid credentials
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return 'test-business-id';
      if (key === 'businessApiKey') return 'test-api-key';
      return null;
    });
    
    // Mock successful validation
    mockSuccessResponse({ business_id: 'test-business-id' });
    
    // Mock templates fetch
    mockSuccessResponse([]);
    
    await render(<StageEditor />);
    
    // Wait for component to initialize
    await waitFor(() => {
      expect(screen.getByText('Stage Information')).toBeInTheDocument();
    });
    
    // Find the stage name input by its ID pattern
    const stageNameInput = screen.getByRole('textbox', { name: /stage name/i });
    fireEvent.change(stageNameInput, {
      target: { value: 'Test Stage' }
    });
    
    // Find the stage description input by its role
    const stageDescriptionInput = screen.getByRole('textbox', { name: /stage description/i });
    fireEvent.change(stageDescriptionInput, {
      target: { value: 'Test stage description' }
    });
    
    // Mock successful stage creation
    mockSuccessResponse({ stage_id: 'new-stage-id' });
    
    // Click create stage
    fireEvent.click(screen.getByText('Create Stage'));
    
    // Check that the API was called with correct data
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/stages?business_id=test-business-id'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Test Stage')
        })
      );
    });
    
    // Check success message appears
    await waitFor(() => {
      expect(screen.getByText('Stage created successfully')).toBeInTheDocument();
    });
    
    // Check navigation occurs
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalled();
    });
  });
});