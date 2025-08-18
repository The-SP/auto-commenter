'use client';

import {
  ExternalLink,
  Loader2,
  MessageCircle,
  RefreshCw,
  Send,
  ThumbsUp,
} from 'lucide-react';
import { SetStateAction, useEffect, useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api';
import { GenerateCommentResponse, PostDetails, PostSummary } from '@/types/api';

enum Step {
  ENTER_SUBREDDIT = 1,
  SELECT_POST = 2,
  VIEW_POST = 3,
  GENERATE_COMMENT = 4,
  POST_COMMENT = 5,
}

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>(Step.ENTER_SUBREDDIT);
  const [subreddit, setSubreddit] = useState('');
  const [posts, setPosts] = useState<PostSummary[]>([]);
  const [selectedPost, setSelectedPost] = useState<PostDetails | null>(null);
  const [availableTones, setAvailableTones] = useState<string[]>([]);
  const [selectedTone, setSelectedTone] = useState('auto');
  const [generatedComment, setGeneratedComment] =
    useState<GenerateCommentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load available tones on mount
    const loadTones = async () => {
      try {
        const tones = await apiClient.getTones();
        setAvailableTones(tones);
      } catch (err) {
        console.error('Failed to load tones:', err);
      }
    };
    loadTones();
  }, []);

  const handleSubredditSubmit = async () => {
    if (!subreddit.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const fetchedPosts = await apiClient.getPosts(subreddit.trim());
      setPosts(fetchedPosts);
      setCurrentStep(Step.SELECT_POST);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch posts');
    } finally {
      setLoading(false);
    }
  };

  const handlePostSelect = async (post: PostSummary) => {
    setLoading(true);
    setError(null);

    try {
      const postDetails = await apiClient.getPostDetails(post.id);
      setSelectedPost(postDetails);
      setCurrentStep(Step.VIEW_POST);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch post details');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateComment = async () => {
    if (!selectedPost) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateComment(
        selectedPost.id,
        selectedTone,
      );
      setGeneratedComment(response);

      if (response.success) {
        setCurrentStep(Step.GENERATE_COMMENT);
      } else {
        setError(response.error || 'Failed to generate comment');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate comment');
    } finally {
      setLoading(false);
    }
  };

  const handlePostComment = async (dryRun: boolean = false) => {
    if (!selectedPost || !generatedComment?.comment) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.postComment(
        selectedPost.id,
        generatedComment.comment,
        dryRun,
      );

      if (response.success) {
        setCurrentStep(Step.POST_COMMENT);
      } else {
        setError(response.error || 'Failed to post comment');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  const resetWorkflow = () => {
    setCurrentStep(Step.ENTER_SUBREDDIT);
    setSubreddit('');
    setPosts([]);
    setSelectedPost(null);
    setGeneratedComment(null);
    setError(null);
  };

  const getToneDescription = (tone: string) => {
    const descriptions: Record<string, string> = {
      auto: 'Let AI choose the best tone',
      supportive: 'Encouraging and empathetic',
      funny: 'Humorous and witty',
      analytical: 'Thoughtful and detailed',
      questioning: 'Curious and probing',
      informative: 'Educational and helpful',
      controversial: 'Challenging and thought-provoking',
    };
    return descriptions[tone] || '';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Reddit Auto Commenter
          </h1>
          <p className="text-gray-600 mt-2">
            Generate AI-powered comments for Reddit posts
          </p>
        </div>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Step 1: Enter Subreddit */}
        {currentStep === Step.ENTER_SUBREDDIT && (
          <Card>
            <CardHeader>
              <CardTitle>Step 1: Enter Subreddit</CardTitle>
              <CardDescription>
                Enter the subreddit name to fetch top posts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <div className="flex-1">
                  <Input
                    placeholder="Enter subreddit name (e.g., python, askreddit)"
                    value={subreddit}
                    onChange={(e: {
                      target: { value: SetStateAction<string> };
                    }) => setSubreddit(e.target.value)}
                    onKeyDown={(e: { key: string }) =>
                      e.key === 'Enter' && handleSubredditSubmit()
                    }
                  />
                </div>
                <Button onClick={handleSubredditSubmit} disabled={loading}>
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    'Fetch Posts'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Select Post */}
        {currentStep === Step.SELECT_POST && (
          <Card>
            <CardHeader>
              <CardTitle>Step 2: Select a Post</CardTitle>
              <CardDescription>Top posts from r/{subreddit}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {posts.map((post) => (
                <Card
                  key={post.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => handlePostSelect(post)}
                >
                  <CardContent className="pt-4">
                    <h3 className="font-medium mb-2 line-clamp-2">
                      {post.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        {post.score}
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageCircle className="w-4 h-4" />
                        {post.num_comments}
                      </div>
                      <Badge variant="secondary">r/{post.subreddit}</Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
              <Button
                variant="outline"
                onClick={resetWorkflow}
                className="w-full"
              >
                Back to Subreddit Selection
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 3: View Post Details */}
        {currentStep === Step.VIEW_POST && selectedPost && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Step 3: Post Details</CardTitle>
                <CardDescription>
                  Review the post content and existing comments
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h2 className="text-xl font-semibold mb-2">
                    {selectedPost.title}
                  </h2>
                  <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <ThumbsUp className="w-4 h-4" />
                      {selectedPost.score}
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-4 h-4" />
                      {selectedPost.num_comments}
                    </div>
                    <Badge variant="secondary">
                      r/{selectedPost.subreddit}
                    </Badge>
                    <a
                      href={selectedPost.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View Original
                    </a>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="whitespace-pre-wrap">
                      {selectedPost.content}
                    </p>
                  </div>
                </div>

                <Separator />

                <div>
                  <h3 className="font-semibold mb-3">
                    Top Comments ({selectedPost.comments.length})
                  </h3>
                  <div className="space-y-3">
                    {selectedPost.comments.map((comment) => (
                      <div
                        key={comment.id}
                        className="bg-gray-50 p-3 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm">
                            u/{comment.author}
                          </span>
                          <Badge variant="outline">{comment.score}</Badge>
                        </div>
                        <p className="text-sm">{comment.body}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentStep(Step.SELECT_POST)}
                  >
                    Back to Posts
                  </Button>
                  <div className="flex-1 flex gap-2">
                    <Select
                      value={selectedTone}
                      onValueChange={setSelectedTone}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {availableTones.map((tone) => (
                          <SelectItem key={tone} value={tone}>
                            {tone.toUpperCase()} - {getToneDescription(tone)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button onClick={handleGenerateComment} disabled={loading}>
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Generate Comment'
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Review Generated Comment */}
        {currentStep === Step.GENERATE_COMMENT && generatedComment && (
          <Card>
            <CardHeader>
              <CardTitle>Step 4: Generated Comment</CardTitle>
              <CardDescription>
                Review your AI-generated comment before posting
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">
                    Comment ({generatedComment.length} characters)
                  </span>
                  <Badge variant="secondary">
                    {generatedComment.tone.toUpperCase()}
                  </Badge>
                </div>
                <Textarea
                  value={generatedComment.comment}
                  readOnly
                  className="min-h-[100px]"
                />
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep(Step.VIEW_POST)}
                >
                  Back to Post
                </Button>
                <Button
                  variant="outline"
                  onClick={handleGenerateComment}
                  disabled={loading}
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                  Regenerate
                </Button>
                <Button
                  onClick={() => handlePostComment(true)}
                  disabled={loading}
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Post Comment
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 5: Success */}
        {currentStep === Step.POST_COMMENT && (
          <Card>
            <CardHeader>
              <CardTitle>Step 5: Comment Posted!</CardTitle>
              <CardDescription>
                Your comment has been successfully posted
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="border-green-200 bg-green-50">
                <AlertDescription className="text-green-800">
                  Comment posted successfully! Your AI-generated comment is now
                  live on Reddit.
                </AlertDescription>
              </Alert>

              <Button onClick={resetWorkflow} className="w-full">
                Start New Comment
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
