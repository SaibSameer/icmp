import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Custom render function that includes router context
const customRender = (ui, options = {}) => {
  return render(ui, {
    wrapper: ({ children }) => (
      <BrowserRouter>
        {children}
      </BrowserRouter>
    ),
    ...options,
  });
};

// Mock template data
export const mockTemplates = {
  stage_selection: [
    {
      template_id: 'template1',
      template_name: 'Stage Selection Template',
      template_type: 'stage_selection',
      template_text: 'Test stage selection template'
    }
  ],
  data_extraction: [
    {
      template_id: 'template2',
      template_name: 'Data Extraction Template',
      template_type: 'data_extraction',
      template_text: 'Test data extraction template'
    }
  ],
  response_generation: [
    {
      template_id: 'template3',
      template_name: 'Response Generation Template',
      template_type: 'response_generation',
      template_text: 'Test response generation template'
    }
  ],
  default_stage_selection: [
    {
      template_id: 'default1',
      template_name: 'Default Stage Selection',
      template_type: 'default_stage_selection',
      template_text: 'Default stage selection template'
    }
  ],
  default_data_extraction: [
    {
      template_id: 'default2',
      template_name: 'Default Data Extraction',
      template_type: 'default_data_extraction',
      template_text: 'Default data extraction template'
    }
  ],
  default_response_generation: [
    {
      template_id: 'default3',
      template_name: 'Default Response Generation',
      template_type: 'default_response_generation',
      template_text: 'Default response generation template'
    }
  ]
};

// Helper to mock localStorage
export const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Helper to setup localStorage mock
export const setupLocalStorageMock = (credentials = null) => {
  if (credentials) {
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'businessId') return credentials.businessId;
      if (key === 'businessApiKey') return credentials.businessApiKey;
      return null;
    });
  } else {
    mockLocalStorage.getItem.mockImplementation(() => null);
  }
};

// Export everything
export * from '@testing-library/react';
export { customRender as render };