'use client';

import {
  ArrowLeft,
  CheckCircle,
  ExternalLink,
  Hash,
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Reddit Auto Commenter
            </h1>
            <p className="text-muted-foreground text-lg mt-2">
              Generate AI-powered comments for Reddit posts with style
            </p>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center">
          <div className="flex items-center space-x-4">
            {[1, 2, 3, 4, 5].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                    currentStep >= step
                      ? 'bg-blue-500 text-white shadow-lg'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {currentStep > step ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    step
                  )}
                </div>
                {step < 5 && (
                  <div
                    className={`w-12 h-1 mx-2 transition-all ${
                      currentStep > step ? 'bg-blue-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {error && (
          <Alert className="border-red-200 bg-red-50 shadow-sm">
            <AlertDescription className="text-red-800 font-medium">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Step 1: Enter Subreddit */}
        {currentStep === Step.ENTER_SUBREDDIT && (
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Hash className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Enter Subreddit</CardTitle>
                  <CardDescription className="text-base">
                    Choose a community to find engaging posts
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    r/
                  </div>
                  <Input
                    className="pl-8 h-12 text-lg border-2 focus:border-blue-500 transition-colors"
                    placeholder="python, askreddit, programming..."
                    value={subreddit}
                    onChange={(e: {
                      target: { value: SetStateAction<string> };
                    }) => setSubreddit(e.target.value)}
                    onKeyDown={(e: { key: string }) =>
                      e.key === 'Enter' && handleSubredditSubmit()
                    }
                  />
                </div>
                <Button
                  onClick={handleSubredditSubmit}
                  disabled={loading || !subreddit.trim()}
                  size="lg"
                  className="px-8"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
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
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <ThumbsUp className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">Select a Post</CardTitle>
                    <CardDescription className="text-base">
                      Top posts from r/{subreddit}
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={resetWorkflow}
                  size="sm"
                  className="gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {posts.map((post, index) => (
                <Card
                  key={post.id}
                  className="cursor-pointer hover:shadow-md hover:border-blue-300 transition-all duration-200 border-2"
                  onClick={() => handlePostSelect(post)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <div className="bg-gray-100 rounded-lg p-3 text-center min-w-16">
                        <div className="text-2xl font-bold text-gray-700">
                          {index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-3 line-clamp-2 leading-relaxed">
                          {post.title}
                        </h3>
                        <div className="flex items-center gap-6 text-sm">
                          <div className="flex items-center gap-2 bg-orange-50 px-3 py-1 rounded-full">
                            <ThumbsUp className="w-4 h-4 text-orange-600" />
                            <span className="font-medium text-orange-800">
                              {post.score.toLocaleString()}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded-full">
                            <MessageCircle className="w-4 h-4 text-blue-600" />
                            <span className="font-medium text-blue-800">
                              {post.num_comments.toLocaleString()}
                            </span>
                          </div>
                          <Badge variant="secondary" className="text-xs">
                            r/{post.subreddit}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Step 3: View Post Details */}
        {currentStep === Step.VIEW_POST && selectedPost && (
          <div className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <MessageCircle className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">Post Details</CardTitle>
                      <CardDescription className="text-base">
                        Review content and existing discussion
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => setCurrentStep(Step.SELECT_POST)}
                    size="sm"
                    className="gap-2"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Posts
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Post Content */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold leading-relaxed">
                    {selectedPost.title}
                  </h2>
                  <div className="flex items-center flex-wrap gap-3">
                    <div className="flex items-center gap-2 bg-orange-50 px-3 py-2 rounded-full">
                      <ThumbsUp className="w-4 h-4 text-orange-600" />
                      <span className="font-semibold text-orange-800">
                        {selectedPost.score.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-full">
                      <MessageCircle className="w-4 h-4 text-blue-600" />
                      <span className="font-semibold text-blue-800">
                        {selectedPost.num_comments.toLocaleString()}
                      </span>
                    </div>
                    <Badge variant="secondary" className="px-3 py-1">
                      r/{selectedPost.subreddit}
                    </Badge>
                    <a
                      href={selectedPost.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium px-3 py-2 hover:bg-blue-50 rounded-full transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View Original
                    </a>
                  </div>
                  <div className="bg-gray-50 border-2 border-gray-100 p-6 rounded-xl">
                    <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {selectedPost.content}
                    </p>
                  </div>
                </div>

                <Separator className="my-6" />

                {/* Comments Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-blue-600" />
                    Top Comments ({selectedPost.comments.length})
                  </h3>
                  <div className="space-y-4">
                    {selectedPost.comments.map((comment, index) => (
                      <Card key={comment.id} className="bg-gray-50/80 border">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-xs font-bold text-blue-700">
                                {index + 1}
                              </div>
                              <span className="font-semibold text-sm text-gray-700">
                                u/{comment.author}
                              </span>
                            </div>
                            <Badge variant="outline" className="bg-white">
                              +{comment.score}
                            </Badge>
                          </div>
                          <p className="text-sm leading-relaxed text-gray-800 pl-11">
                            {comment.body}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>

                {/* Action Section */}
                <Card className="bg-blue-50/50 border-blue-200">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1">
                          <label className="text-sm font-medium text-gray-700 mb-2 block">
                            Comment Tone
                          </label>
                          <Select
                            value={selectedTone}
                            onValueChange={setSelectedTone}
                          >
                            <SelectTrigger className="h-12 bg-white border-2">
                              <SelectValue>
                                <div className="flex items-center justify-between w-full">
                                  <span className="font-medium">
                                    {selectedTone.toUpperCase()}
                                  </span>
                                </div>
                              </SelectValue>
                            </SelectTrigger>
                            <SelectContent>
                              {availableTones.map((tone) => (
                                <SelectItem key={tone} value={tone}>
                                  <span className="font-medium">
                                    {tone.toUpperCase()}
                                  </span>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex items-end">
                          <Button
                            onClick={handleGenerateComment}
                            disabled={loading}
                            size="lg"
                            className="px-8 h-12"
                          >
                            {loading ? (
                              <Loader2 className="w-5 h-5 animate-spin mr-2" />
                            ) : (
                              <MessageCircle className="w-5 h-5 mr-2" />
                            )}
                            Generate Comment
                          </Button>
                        </div>
                      </div>
                      {selectedTone && (
                        <p className="text-sm text-muted-foreground px-1">
                          {getToneDescription(selectedTone)}
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Review Generated Comment */}
        {currentStep === Step.GENERATE_COMMENT && generatedComment && (
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <MessageCircle className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">Generated Comment</CardTitle>
                    <CardDescription className="text-base">
                      Review before posting to Reddit
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep(Step.VIEW_POST)}
                  size="sm"
                  className="gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Post
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-lg">Your Comment</span>
                    <Badge variant="secondary" className="text-xs">
                      {generatedComment.length} characters
                    </Badge>
                  </div>
                  <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">
                    {generatedComment.tone.toUpperCase()}
                  </Badge>
                </div>
                <Card className="bg-blue-50/50 border-blue-200">
                  <CardContent className="p-6">
                    <Textarea
                      value={generatedComment.comment}
                      readOnly
                      className="min-h-[120px] text-base leading-relaxed bg-white border-2 resize-none"
                    />
                  </CardContent>
                </Card>
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  variant="outline"
                  onClick={handleGenerateComment}
                  disabled={loading}
                  className="flex-1 h-12 gap-2"
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
                  size="lg"
                  className="flex-1 h-12 gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Post to Reddit
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 5: Success */}
        {currentStep === Step.POST_COMMENT && (
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-xl text-green-800">
                    Comment Posted Successfully!
                  </CardTitle>
                  <CardDescription className="text-base">
                    Your AI-generated comment is now live on Reddit
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert className="border-green-200 bg-green-50 shadow-sm">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <AlertDescription className="text-green-800 font-medium text-base">
                  🎉 Your comment has been successfully posted to Reddit! The
                  community can now engage with your AI-generated response.
                </AlertDescription>
              </Alert>

              <Button onClick={resetWorkflow} size="lg" className="w-full h-12">
                <MessageCircle className="w-5 h-5 mr-2" />
                Start New Comment
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
