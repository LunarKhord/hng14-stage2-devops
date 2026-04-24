// Mock external API calls BEFORE importing the app
const axios = require('axios');
jest.mock('axios');

const request = require('supertest');
const app = require('./app');

describe('Frontend API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

    test('GET /health returns 200', async () => {
    axios.get.mockResolvedValue({ data: { status: 'healthy' } });
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    // optionally check the response body
    expect(res.body).toEqual({ status: 'healthy' });
    });

  test('POST /submit returns a job object', async () => {
    // Mock the API call that the frontend makes to the backend
    axios.post.mockResolvedValue({ data: { job_id: 'test-123' } });

    const res = await request(app).post('/submit');
    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual({ job_id: 'test-123' });
  });

  test('GET /status/:id returns status', async () => {
    // Mock the API call that the frontend makes to the backend
    axios.get.mockResolvedValue({ data: { job_id: 'abc', status: 'completed' } });

    const res = await request(app).get('/status/abc');
    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual({ job_id: 'abc', status: 'completed' });
  });
});