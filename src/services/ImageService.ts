import axios from 'axios';
import sharp from 'sharp';

interface ImageOptions {
  format: 'jpeg' | 'png' | 'webp';
  width?: number;
  height?: number;
}

class ImageService {
  async downloadImage(url: string): Promise<Buffer> {
    const response = await axios.get(url, { responseType: 'arraybuffer' });
    return response.data;
  }

  async optimizeImage(imageBuffer: Buffer, options: ImageOptions): Promise<Buffer> {
    let image = sharp(imageBuffer);
    if (options.width || options.height) {
      image = image.resize(options.width, options.height);
    }
    switch (options.format) {
      case 'jpeg':
        image = image.jpeg({ quality: 80 });
        break;
      case 'png':
        image = image.png({ compressionLevel: 9 });
        break;
      case 'webp':
        image = image.webp({ quality: 80 });
        break;
    }
    return image.toBuffer();
  }
}

export default new ImageService();