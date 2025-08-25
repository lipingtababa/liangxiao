import ImageService from '../../src/services/ImageService';

describe('ImageService', () => {
  it('downloads and optimizes an image', async () => {
    const url = 'http://example.com/image.jpg';
    const format = 'webp';
    const width = 100;
    const height = 100;

    const downloadedImage = await ImageService.downloadImage(url);
    expect(downloadedImage).toBeInstanceOf(Buffer);

    const optimizedImage = await ImageService.optimizeImage(downloadedImage, { format, width, height });
    expect(optimizedImage).toBeInstanceOf(Buffer);
  });
});