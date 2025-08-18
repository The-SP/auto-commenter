// API Types
export interface PostSummary {
  id: string;
  title: string;
  score: number;
  num_comments: number;
  subreddit: string;
}

export interface Comment {
  id: string;
  body: string;
  score: number;
  author: string;
  created_utc: number;
}

export interface PostDetails {
  id: string;
  title: string;
  content: string;
  url: string;
  score: number;
  num_comments: number;
  subreddit: string;
  comments: Comment[];
}

export interface GenerateCommentResponse {
  success: boolean;
  comment?: string;
  length?: number;
  tone: string;
  error?: string;
}

export interface PostCommentResponse {
  success: boolean;
  comment_id?: string;
  comment_url?: string;
  message?: string;
  error?: string;
  error_type?: string;
}
