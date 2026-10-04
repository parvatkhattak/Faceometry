/**
 * Faceometry API Client
 * ======================
 * Handles communication with the FastAPI backend.
 */

import { AnalysisResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  public status: number;
  public issues: string[];

  constructor(message: string, status: number, issues: string[] = []) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.issues = issues;
  }
}

/**
 * Upload an image and run facial analysis.
 *
 * @param file - The image file to analyze.
 * @returns AnalysisResponse with scores, measurements, and explanations.
 * @throws ApiError if the request fails or validation fails.
 */
export async function analyzeImage(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(
        'An unexpected error occurred. Please try again.',
        response.status
      );
    }

    // Handle structured error from FastAPI
    const detail = errorData.detail || errorData;
    const message = detail.error || detail.message || 'Analysis failed.';
    const issues = detail.issues || [];

    throw new ApiError(message, response.status, issues);
  }

  const data: AnalysisResponse = await response.json();
  return data;
}

/**
 * Check if the backend is healthy.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch {
    return false;
  }
}
