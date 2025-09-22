const path = require('path');
const fs = require('fs');
const matter = require('gray-matter');

function getPostData(id) {
  const postsDirectory = path.join(process.cwd(), 'posts');
  const fullPath = path.join(postsDirectory, `${id}.md`);
  
  console.log('Looking for file:', fullPath);
  console.log('File exists:', fs.existsSync(fullPath));
  
  if (!fs.existsSync(fullPath)) {
    console.log('File not found!');
    return null;
  }
  
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const matterResult = matter(fileContents);
  
  const stats = fs.statSync(fullPath);
  const fallbackDate = stats.mtime.toISOString().split('T')[0];
  
  const result = {
    id,
    title: matterResult.data.title || '',
    date: matterResult.data.date || fallbackDate,
    author: matterResult.data.author,
    category: matterResult.data.category,
    tags: matterResult.data.tags,
    description: matterResult.data.description,
    image: matterResult.data.image,
    originalUrl: matterResult.data.originalUrl,
    content: matterResult.content || '',
    contentHtml: matterResult.content || '',
  };
  
  console.log('Result:', {
    hasTitle: !!result.title,
    titleLength: result.title.length,
    hasContent: !!result.content,
    contentLength: result.content.length,
    title: result.title
  });
  
  return result;
}

const postData = getPostData('treat-ai-like-humans-not-software');
console.log('Title:', postData?.title);
console.log('First 100 chars of content:', postData?.content?.substring(0, 100));
