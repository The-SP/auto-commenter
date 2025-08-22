import axios from 'axios';
import {
  PostSummary,
  PostDetails,
  GenerateCommentResponse,
  PostCommentResponse,
} from '@/types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Get top posts from subreddit
  getPosts: async (
    subreddit: string,
    limit: number = 3,
  ): Promise<PostSummary[]> => {
    const response = await api.get(`/posts/${subreddit}?limit=${limit}`);
    return response.data;
  },

  // Get detailed post with comments
  getPostDetails: async (
    postId: string,
  ): Promise<PostDetails> => {
    const response = await api.get(`/post/${postId}`);
    return response.data;
  },

  // Get available tones
  getTones: async (): Promise<string[]> => {
    const response = await api.get('/tones');
    return response.data;
  },

  // Generate comment
  generateComment: async (
    postId: string,
    tone: string,
  ): Promise<GenerateCommentResponse> => {
    const response = await api.post('/generate-comment', {
      post_id: postId,
      tone,
    });
    return response.data;
  },

  // Post comment
  postComment: async (
    postId: string,
    commentText: string,
    dryRun: boolean = true,
  ): Promise<PostCommentResponse> => {
    const response = await api.post('/post-comment', {
      post_id: postId,
      comment_text: commentText,
      dry_run: dryRun,
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};
