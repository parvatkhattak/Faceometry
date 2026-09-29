/**
 * Faceometry API Response Types
 * ==============================
 * TypeScript interfaces matching the backend Pydantic models.
 * The frontend depends ONLY on these types, not on internal
 * calculation details.
 */

export interface PoseEstimate {
  yaw: number;
  pitch: number;
  roll: number;
}

export interface FaceInfo {
  count: number;
  pose: PoseEstimate;
}

export interface ScoreBreakdown {
  symmetry: number;
  proportion: number;
  golden_ratio: number;
  facial_thirds: number;
  facial_fifths: number;
  harmony: number;
}

export interface RatioAnalysis {
  name: string;
  value: number;
  target: number;
  deviation: number;
  score: number;
}

export interface GoldenRatioAnalysis {
  ratios: RatioAnalysis[];
  overall_score: number;
}

export interface SymmetryDetail {
  region: string;
  error: number;
  score: number;
}

export interface SymmetryAnalysis {
  overall_score: number;
  details: SymmetryDetail[];
}

export interface FacialThirdsAnalysis {
  upper_third: number;
  middle_third: number;
  lower_third: number;
  score: number;
}

export interface FacialFifthsAnalysis {
  sections: number[];
  score: number;
}

export interface FacialMeasurements {
  face_width: number;
  face_height: number;
  face_aspect_ratio: number;
  left_eye_width: number;
  right_eye_width: number;
  average_eye_width: number;
  inter_eye_distance: number;
  eye_face_width_ratio: number;
  nose_length: number;
  nose_width: number;
  nose_aspect_ratio: number;
  mouth_width: number;
  mouth_nose_ratio: number;
  hairline_to_nose_base: number;
}

export interface ScoreExplanation {
  component: string;
  score: number;
  explanation: string;
}

export interface AnalysisResponse {
  success: boolean;
  face: FaceInfo;
  scores: ScoreBreakdown;
  measurements: FacialMeasurements;
  golden_ratio_analysis: GoldenRatioAnalysis;
  symmetry_analysis: SymmetryAnalysis;
  facial_thirds: FacialThirdsAnalysis;
  facial_fifths: FacialFifthsAnalysis;
  explanations: ScoreExplanation[];
  landmark_image_base64: string | null;
}

export interface ErrorResponse {
  success: false;
  error: string;
  detail?: string | null;
}

export interface ValidationErrorResponse {
  success: false;
  error: string;
  issues: string[];
}

export type ApiResponse = AnalysisResponse | ErrorResponse | ValidationErrorResponse;

export function isAnalysisResponse(data: ApiResponse): data is AnalysisResponse {
  return data.success === true;
}

export function isValidationError(data: ApiResponse): data is ValidationErrorResponse {
  return data.success === false && 'issues' in data;
}
