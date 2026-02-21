const { getPostData } = require('./lib/posts.ts');

try {
  console.log('Testing direct call to getPostData...');
  const data = getPostData('treat-ai-like-humans-not-software');
  console.log('Result:', {
    title: data.title,
    hasContent: !!data.content,
    contentLength: data.content?.length
  });
} catch (error) {
  console.error('Error:', error);
}
