import '@testing-library/jest-dom';
import 'jest-canvas-mock';

// Mock axios
const mockAxios = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
};

jest.mock('axios', () => ({
  __esModule: true,
  default: mockAxios
}));

// Mock fetch
const mockFetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({})
  })
);
mockFetch.mockClear = jest.fn();
global.fetch = mockFetch;

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

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Mock useConfig hook
jest.mock('../hooks/useConfig', () => ({
  __esModule: true,
  default: () => ({
    config: {
      apiKey: 'test_api_key',
      userId: 'test_user',
      businessId: 'test_business',
      businessApiKey: 'test_business_key'
    },
    setConfig: jest.fn(),
    loading: false,
    error: null
  })
}));

// Mock useBusiness hook
jest.mock('../hooks/useBusiness', () => ({
  __esModule: true,
  default: () => ({
    business: {
      id: 'test_business',
      name: 'Test Business',
      apiKey: 'test_business_key'
    },
    setBusiness: jest.fn(),
    loading: false,
    error: null
  })
}));