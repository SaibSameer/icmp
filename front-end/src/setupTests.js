import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { act } from 'react';

// Increase test timeout
jest.setTimeout(10000);

// Configure testing-library
configure({
  asyncUtilTimeout: 5000,
  testIdAttribute: 'data-testid',
});

// Configure global test environment
global.React = { act };

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Setup fetch mock
global.fetch = jest.fn();

// Helper to reset all mocks
beforeEach(() => {
  global.fetch.mockClear();
  jest.clearAllMocks();
});

// Add fetch mock implementations
global.fetch.mockImplementation(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({}),
}));

// Configure MUI for testing environment
window.HTMLElement.prototype.scrollIntoView = jest.fn();